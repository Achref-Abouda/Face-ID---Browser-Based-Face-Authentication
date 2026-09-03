"""
Central configuration for the Face ID app.
Change thresholds here if detection feels too strict or too loose
for your webcam / lighting conditions.
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FACES_DIR = os.path.join(DATA_DIR, "faces")          # saved pose snapshots, per user
ENCODINGS_FILE = os.path.join(DATA_DIR, "encodings.pkl")  # name -> list of face encodings

# Flask
SECRET_KEY = os.environ.get("FACE_ID_SECRET_KEY", "dev-key-change-me-in-production")

# --- Enrollment (sign up) pose sequence ---
# The user is walked through these poses, in order, to build a robust
# face profile. Feel free to shorten this list (e.g. just ["center"])
# for a faster demo.
SIGNUP_STEPS = ["center", "right", "left", "up", "down"]

# --- Login only needs one confident, centered look ---
LOGIN_STEPS = ["center"]

STEP_COPY = {
    "center": {
        "title": "Look straight at the camera",
        "hint": "Keep your whole face inside the frame.",
    },
    "right": {
        "title": "Turn your head to the right",
        "hint": "Slowly rotate until your profile is visible.",
    },
    "left": {
        "title": "Turn your head to the left",
        "hint": "Slowly rotate until your profile is visible.",
    },
    "up": {
        "title": "Tilt your head up",
        "hint": "Lift your chin slightly toward the ceiling.",
    },
    "down": {
        "title": "Tilt your head down",
        "hint": "Lower your chin slightly toward your chest.",
    },
}

# --- Face matching ---
# Lower = stricter match. face_recognition's default is 0.6.
MATCH_TOLERANCE = 0.5

# --- Head pose heuristic thresholds ---
# These are ratios of nose displacement relative to half the face
# width/height. Raise them if "center" is too hard to hit; lower
# them if turns aren't being detected.
HORIZONTAL_TURN_THRESHOLD = 0.16
VERTICAL_TILT_THRESHOLD = 0.16
