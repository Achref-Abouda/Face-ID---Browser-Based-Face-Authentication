"""
All face-detection / pose-estimation / matching logic lives here,
kept deliberately separate from Flask routing.

Pipeline for a single captured frame:
  1. decode_frame()      -> raw JPEG bytes to an RGB numpy array
  2. get_landmarks()     -> dlib's 68-point face landmarks (via face_recognition)
  3. estimate_direction()-> a cheap geometric heuristic: where is the nose
                            sitting relative to the face's bounding box?
  4. get_encoding()      -> a 128-d face embedding, used for matching identity

Note on the pose heuristic: this is intentionally simple (no ML pose
model, no calibration step) so the project has zero extra model
downloads beyond what face_recognition already ships with. It works
well enough to gate an enrollment flow, but it is not a liveness or
anti-spoofing system.
"""

import base64
import io

import face_recognition
import numpy as np
from PIL import Image

import config


def decode_frame(data_url: str) -> np.ndarray:
    """Turn a `data:image/jpeg;base64,...` string from the browser into an RGB numpy array."""
    if "," in data_url:
        data_url = data_url.split(",", 1)[1]
    raw = base64.b64decode(data_url)
    image = Image.open(io.BytesIO(raw)).convert("RGB")
    return np.array(image)


def get_face_locations(frame: np.ndarray):
    return face_recognition.face_locations(frame, model="hog")


def get_landmarks(frame: np.ndarray, face_locations=None):
    landmarks_list = face_recognition.face_landmarks(frame, face_locations=face_locations)
    if not landmarks_list:
        return None
    return landmarks_list[0]


def get_encoding(frame: np.ndarray, face_locations=None):
    encodings = face_recognition.face_encodings(frame, known_face_locations=face_locations)
    if not encodings:
        return None
    return encodings[0]


def estimate_direction(landmarks: dict) -> str:
    """
    Rough heuristic for which way a face is pointed, using only the
    68-point landmark set. Returns one of: center, left, right, up, down.
    """
    jaw = landmarks.get("chin", [])
    nose_bridge = landmarks.get("nose_bridge", [])
    nose_tip = landmarks.get("nose_tip", [])
    left_eyebrow = landmarks.get("left_eyebrow", [])
    right_eyebrow = landmarks.get("right_eyebrow", [])

    if not (jaw and nose_tip and nose_bridge and left_eyebrow and right_eyebrow):
        return "unknown"

    # --- horizontal: nose tip x vs. the midpoint of the jawline ---
    jaw_left_x, jaw_right_x = jaw[0][0], jaw[-1][0]
    face_width = max(jaw_right_x - jaw_left_x, 1)
    face_center_x = (jaw_left_x + jaw_right_x) / 2
    nose_x = nose_tip[-1][0]
    horizontal_ratio = (nose_x - face_center_x) / (face_width / 2)

    # --- vertical: nose tip y vs. the midpoint between eyebrows and chin ---
    eyebrow_y = sum(p[1] for p in left_eyebrow + right_eyebrow) / len(left_eyebrow + right_eyebrow)
    chin_y = jaw[len(jaw) // 2][1]  # bottom-center chin point
    face_height = max(chin_y - eyebrow_y, 1)
    face_center_y = (eyebrow_y + chin_y) / 2
    nose_y = nose_tip[-1][1]
    vertical_ratio = (nose_y - face_center_y) / (face_height / 2)

    h_thresh = config.HORIZONTAL_TURN_THRESHOLD
    v_thresh = config.VERTICAL_TILT_THRESHOLD

    # Horizontal turns tend to dominate the signal, so check them first.
    if horizontal_ratio > h_thresh:
        return "right"
    if horizontal_ratio < -h_thresh:
        return "left"
    if vertical_ratio < -v_thresh:
        return "up"
    if vertical_ratio > v_thresh:
        return "down"
    return "center"


def analyze_frame(data_url: str, expected_step: str):
    """
    Full check for one enrollment/login step.
    Returns (ok: bool, message: str, encoding: list[float] | None)
    """
    frame = decode_frame(data_url)
    face_locations = get_face_locations(frame)

    if len(face_locations) == 0:
        return False, "No face detected. Move into frame and make sure you're well lit.", None
    if len(face_locations) > 1:
        return False, "More than one face detected. Make sure you're alone in frame.", None

    landmarks = get_landmarks(frame, face_locations)
    if landmarks is None:
        return False, "Couldn't read facial features clearly. Try better lighting.", None

    direction = estimate_direction(landmarks)
    if direction == "unknown":
        return False, "Couldn't read facial features clearly. Try better lighting.", None

    if direction != expected_step:
        return False, f"Detected '{direction}', expected '{expected_step}'. Keep adjusting.", None

    encoding = get_encoding(frame, face_locations)
    if encoding is None:
        return False, "Face detected but couldn't be encoded. Try again.", None

    return True, "Captured.", encoding.tolist()


def best_match(stored_encodings, candidate_encoding, tolerance=None):
    """
    Compare a candidate encoding against a list of stored encodings.
    Returns (is_match: bool, distance: float)
    """
    if tolerance is None:
        tolerance = config.MATCH_TOLERANCE
    if not stored_encodings:
        return False, 1.0

    stored = np.array(stored_encodings)
    candidate = np.array(candidate_encoding)
    distances = np.linalg.norm(stored - candidate, axis=1)
    min_distance = float(np.min(distances))
    return min_distance <= tolerance, min_distance
