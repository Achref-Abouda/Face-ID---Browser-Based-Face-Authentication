"""
Face ID demo app.

Flow:
  /                -> enter your name, choose Sign Up or Log In
  /start           -> validates the name + mode, opens a capture session
  /capture         -> browser webcam walks through the required poses
  /api/capture     -> receives one frame per pose, validates + stores it
  /welcome         -> success screen after sign up or log in
  /cancel          -> abandon the current capture session

Run with:  python app.py
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify

import config
from core import data_store, face_utils

app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY


def steps_for(mode: str):
    return config.SIGNUP_STEPS if mode == "signup" else config.LOGIN_STEPS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/start", methods=["POST"])
def start():
    name = (request.form.get("name") or "").strip()
    mode = request.form.get("mode")

    if not name:
        return render_template("index.html", error="Enter your name first.")
    if mode not in ("signup", "login"):
        return render_template("index.html", error="Something went wrong. Try again.")

    exists = data_store.user_exists(name)
    if mode == "signup" and exists:
        return render_template(
            "index.html", error=f"'{name}' is already enrolled. Try logging in instead."
        )
    if mode == "login" and not exists:
        return render_template(
            "index.html", error=f"No Face ID found for '{name}'. Sign up first."
        )

    session["auth_name"] = name
    session["auth_mode"] = mode
    session["step_index"] = 0
    session["captured_encodings"] = []
    return redirect(url_for("capture"))


@app.route("/capture")
def capture():
    if "auth_mode" not in session:
        return redirect(url_for("index"))

    mode = session["auth_mode"]
    steps = steps_for(mode)
    step_index = session.get("step_index", 0)

    if step_index >= len(steps):
        return redirect(url_for("index"))

    return render_template(
        "capture.html",
        name=session["auth_name"],
        mode=mode,
        steps=steps,
        step_copy=config.STEP_COPY,
        step_index=step_index,
        total_steps=len(steps),
    )


@app.route("/api/capture", methods=["POST"])
def api_capture():
    if "auth_mode" not in session:
        return jsonify(ok=False, message="Session expired. Start again."), 400

    payload = request.get_json(silent=True) or {}
    image_data_url = payload.get("image")
    if not image_data_url:
        return jsonify(ok=False, message="No image received.")

    mode = session["auth_mode"]
    name = session["auth_name"]
    steps = steps_for(mode)
    step_index = session.get("step_index", 0)

    if step_index >= len(steps):
        return jsonify(ok=False, message="Session already complete.")

    expected_step = steps[step_index]
    ok, message, encoding = face_utils.analyze_frame(image_data_url, expected_step)

    if not ok:
        return jsonify(ok=False, message=message, done=False)

    if mode == "signup":
        captured = session.get("captured_encodings", [])
        captured.append(encoding)
        session["captured_encodings"] = captured
        session["step_index"] = step_index + 1

        if session["step_index"] >= len(steps):
            data_store.add_user(name, captured)
            session.pop("auth_name", None)
            session.pop("auth_mode", None)
            session.pop("step_index", None)
            session.pop("captured_encodings", None)
            session["welcome_name"] = name
            session["welcome_status"] = "signup"
            return jsonify(ok=True, message="Enrollment complete.", done=True, redirect=url_for("welcome"))

        return jsonify(
            ok=True,
            message=message,
            done=False,
            next_index=session["step_index"],
        )

    # --- login mode: single center capture, then match against stored encodings ---
    stored_encodings = data_store.get_user_encodings(name)
    matched, distance = face_utils.best_match(stored_encodings, encoding)

    if not matched:
        return jsonify(
            ok=False,
            done=False,
            message="Face didn't match our records for this name. Try again.",
        )

    session.pop("auth_name", None)
    session.pop("auth_mode", None)
    session.pop("step_index", None)
    session.pop("captured_encodings", None)
    session["welcome_name"] = name
    session["welcome_status"] = "login"
    return jsonify(ok=True, message="Identity verified.", done=True, redirect=url_for("welcome"))


@app.route("/welcome")
def welcome():
    name = session.pop("welcome_name", None)
    status = session.pop("welcome_status", None)
    if not name:
        return redirect(url_for("index"))
    return render_template("welcome.html", name=name, status=status)


@app.route("/cancel", methods=["POST"])
def cancel():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
