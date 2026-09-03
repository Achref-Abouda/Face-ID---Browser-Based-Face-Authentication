# Face ID — Browser-Based Face Authentication

A Flask app that replaces passwords with a guided face scan, done entirely in the browser — no desktop OpenCV window, no native camera app. Sign up walks the user through five poses to build a face profile; logging in requires only one confident look at the camera.

*Cybersecurity / Computer Vision research project — see the Ethical & Security Notice before using this on real biometric data.*

---

## Author

**Achref Abouda**
Cybersecurity Engineer | Network Security

---

## Overview

The webcam feed never leaves the page until a frame is deliberately captured and sent to the server for analysis. Each captured frame is checked for a face, checked for the correct head pose, then converted into a 128-dimension face embedding using `face_recognition` (built on `dlib`). Those embeddings — not raw photos — are what gets compared on login.

## How It Works

| Step | Screen | What happens |
|------|--------|---------------|
| 1 | Home | The user types their name. Log In and Sign Up stay disabled until they do. Sign Up requires a new name; Log In requires one that's already enrolled. |
| 2 | Capture — Sign Up | The webcam opens in-page (`getUserMedia`). The user is guided through center, right, left, up, and down. Each pose is validated server-side via facial landmarks before it's accepted, then encoded and stored. |
| 2 | Capture — Log In | Same webcam flow, but only the center pose is required. The resulting embedding is compared against the stored one for that name. |
| 3 | Welcome | Confirms enrollment ("You're enrolled, *name*") or a successful match ("Welcome back, *name*"). |

Everything is stored locally in `data/encodings.pkl`, created on first run. No data is sent anywhere outside the local machine.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask (routing, session state) |
| Face detection, landmarks, matching | `face_recognition` (dlib-based) |
| Frontend camera capture | Vanilla JS, `getUserMedia`, `<canvas>` |
| Storage | Local pickle file (`data/encodings.pkl`) |
| Styling | Hand-written CSS, no framework |

## Project Structure

```
face_auth_app/
├── app.py                    # Flask routes (home, capture flow, welcome)
├── config.py                 # Pose sequence, copy, thresholds, paths
├── requirements.txt
├── core/
│   ├── face_utils.py         # Frame decoding, pose heuristic, encoding, matching
│   └── data_store.py         # Load/save encodings.pkl
├── templates/
│   ├── base.html
│   ├── index.html            # Home: name + sign up / log in
│   ├── capture.html          # Webcam capture flow
│   └── welcome.html          # Success screen
├── static/
│   ├── css/style.css
│   └── js/
│       ├── home.js           # Enables buttons once a name is entered
│       └── capture.js        # Webcam access + frame submission loop
└── data/                     # encodings.pkl lives here after first run
```

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000 and allow camera access when prompted.

### If `dlib` fails to install

`face-recognition` depends on `dlib`, which compiles from source and needs CMake and a C++ compiler. Prebuilt wheels also may not exist yet for the newest Python versions — Python 3.11 or 3.12 is the safest bet.

| Platform | Fix |
|---|---|
| macOS | `brew install cmake`, then re-run `pip install -r requirements.txt` |
| Ubuntu / Debian | `sudo apt-get install cmake build-essential` |
| Windows | Install CMake (cmake.org/download) and the "Desktop development with C++" workload from Visual Studio Build Tools, or use conda: `conda install -c conda-forge dlib` |
| Any OS, quickest fix | Use Python 3.11/3.12 in a fresh venv: `py -3.11 -m venv venv` |

## Configuration

Tunable in `config.py`:

| Setting | Purpose |
|---|---|
| `SIGNUP_STEPS` | Pose sequence required at enrollment |
| `LOGIN_STEPS` | Pose(s) required at login |
| `MATCH_TOLERANCE` | Lower means a stricter face match (default `0.5`) |
| `HORIZONTAL_TURN_THRESHOLD` / `VERTICAL_TILT_THRESHOLD` | How far the user must turn or tilt for a pose to register |

## Notes and Limitations

- Pose detection is a simple heuristic, not a trained pose-estimation model — it looks at where the nose sits relative to the jawline and eyebrows. It works well in good lighting and can be picky otherwise. Tune the thresholds above if steps feel too strict or too loose.
- This is not a liveness or anti-spoofing system. A printed photo or video of someone's face could pass the checks. Do not use this for anything security-critical as-is.
- Session state is a signed cookie holding the current step and in-progress encodings during sign up. Restarting the server mid-enrollment means starting over.
- To remove a stored profile, delete its entry from `data/encodings.pkl`, or run `core.data_store.delete_user("name")` from a Python shell.

---

## Credentials

**Education**
- Professional Master's Degree in Information Systems and Infrastructure Security
- Bachelor of Science in Information and Communication Sciences and Technologies — Network Security

**Areas of Focus**
- Cybersecurity
- Network Security
- Application Security
- Secure Software Development
- Authentication and Access Control
- Computer Vision Security
- Web Application Security
- Security Research

This project was developed as part of a practical cybersecurity and software-development portfolio, combining Python, Flask, browser-based webcam access, facial recognition, and authentication concepts.

## Ethical and Security Notice

This project is intended only for educational, defensive, research, and authorized security purposes. It may be used for:

- Educational cybersecurity research
- Authentication prototyping
- Computer-vision experimentation
- Security-awareness training
- Personal cybersecurity laboratories
- Authorized security assessments
- Controlled demonstrations
- Secure software-development research

Because this project processes biometric-related information, users must ensure they have appropriate authorization and consent before enrolling or analyzing another person's face.

This project must not be considered a production-ready authentication system. The current implementation does not provide robust liveness detection, anti-spoofing, encrypted biometric storage, or enterprise-grade identity management.

The author does not endorse unauthorized access, identity impersonation, privacy violations, biometric-data abuse, surveillance, or any other malicious use of this software.

---

# Copyright

Copyright © 2026 **Achref Abouda**. All rights reserved.

This project and its original source code were developed by **Achref Abouda** for educational, defensive, and authorized cybersecurity research purposes.

The project is distributed under the MIT License. Redistribution, modification, and commercial use are permitted under the terms of that license, provided that the applicable copyright and license notices are retained.

**Author:** Achref Abouda
**Project:** Face ID — Browser-Based Face Authentication
**Category:** Cybersecurity / Computer Vision / Authentication
**Year:** 2026

---

# License

MIT License

Copyright © 2026 **Achref Abouda**

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files, to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the software.

THE SOFTWARE IS PROVIDED **"AS IS"**, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY ARISING FROM THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

**Developed by Achref Abouda — 2026**
**Face ID | Browser-Based Face Authentication**
**Cybersecurity Research Project**
