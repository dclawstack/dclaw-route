"""Proof-of-delivery photo validator.

Demo-ready stub. Returns True if the photo payload looks like a non-empty
base64 string of plausible length. Per PRD P0.4, the production version
adds AI photo validation + fraud detection (cloud vision API or a local
model).
"""
import base64


MIN_PHOTO_BYTES = 1024  # ~1 KB; arbitrary lower bound for a real photo


def validate_photo(photo_b64: str | None) -> bool | None:
    if not photo_b64:
        return None
    payload = photo_b64.split(",", 1)[-1] if photo_b64.startswith("data:") else photo_b64
    try:
        decoded = base64.b64decode(payload, validate=True)
    except Exception:
        return False
    return len(decoded) >= MIN_PHOTO_BYTES
