"""
Tiny persistence layer. Face encodings live in a single pickle file:
    { "alice": {"encodings": [[...128 floats...], ...], "created": "2026-09-03T12:00:00"},
      "bob":   {...} }

This is fine for a local demo / small team tool. For anything
production-grade, swap this for a real database.
"""

import os
import pickle
from datetime import datetime, timezone

import config


def _ensure_dirs():
    os.makedirs(config.DATA_DIR, exist_ok=True)
    os.makedirs(config.FACES_DIR, exist_ok=True)


def load_users() -> dict:
    _ensure_dirs()
    if not os.path.exists(config.ENCODINGS_FILE):
        return {}
    with open(config.ENCODINGS_FILE, "rb") as f:
        return pickle.load(f)


def save_users(users: dict) -> None:
    _ensure_dirs()
    with open(config.ENCODINGS_FILE, "wb") as f:
        pickle.dump(users, f)


def user_exists(name: str) -> bool:
    return name in load_users()


def add_user(name: str, encodings: list) -> None:
    users = load_users()
    users[name] = {
        "encodings": encodings,
        "created": datetime.now(timezone.utc).isoformat(),
    }
    save_users(users)


def get_user_encodings(name: str):
    users = load_users()
    user = users.get(name)
    return user["encodings"] if user else None


def delete_user(name: str) -> bool:
    users = load_users()
    if name in users:
        del users[name]
        save_users(users)
        return True
    return False
