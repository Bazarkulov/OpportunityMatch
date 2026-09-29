"""Password hashing and signed bearer tokens without external auth services."""
from __future__ import annotations
import base64
import hashlib
import hmac
import json
import secrets
import time
from backend.config import get_settings

PBKDF2_ITERATIONS = 600_000

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"

def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt, expected = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256": return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), base64.urlsafe_b64decode(salt), int(iterations))
        return hmac.compare_digest(base64.urlsafe_b64encode(digest).decode(), expected)
    except (ValueError, TypeError):
        return False

def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))

def create_token(user_id: str) -> str:
    settings = get_settings()
    payload = {"sub": user_id, "exp": int(time.time()) + settings.access_token_minutes * 60}
    body = _b64(json.dumps(payload, separators=(",", ":")).encode())
    signature = _b64(hmac.new(settings.auth_secret.encode(), body.encode(), hashlib.sha256).digest())
    return f"{body}.{signature}"

def decode_token(token: str) -> str | None:
    try:
        body, supplied = token.split(".", 1)
        expected = _b64(hmac.new(get_settings().auth_secret.encode(), body.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(supplied, expected): return None
        payload = json.loads(_unb64(body))
        if payload["exp"] < time.time(): return None
        return str(payload["sub"])
    except (ValueError, KeyError, json.JSONDecodeError):
        return None
