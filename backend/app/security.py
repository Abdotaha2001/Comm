"""Password hashing (stdlib PBKDF2) and a minimal HS256 JWT (stdlib only).

We implement HS256 directly with hmac/hashlib to avoid a heavy crypto dependency
(PyJWT pulls in `cryptography`, which is unnecessary for HMAC-signed tokens).
"""
import base64
import hashlib
import hmac
import json
import os
import time

from .config import settings

_ALGO = "pbkdf2_sha256"
_ITERS = 200_000


# ── Password hashing ──────────────────────────────────────────
def hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _ITERS)
    return f"{_ALGO}${_ITERS}${base64.b64encode(salt).decode()}${base64.b64encode(dk).decode()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algo, iters, salt_b64, hash_b64 = stored.split("$")
        if algo != _ALGO:
            return False
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(hash_b64)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, int(iters))
        return hmac.compare_digest(dk, expected)
    except Exception:
        return False


# ── JWT (HS256) ───────────────────────────────────────────────
def _b64u(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _b64u_decode(seg: str) -> bytes:
    return base64.urlsafe_b64decode(seg + "=" * (-len(seg) % 4))


def _sign(signing_input: str) -> bytes:
    return hmac.new(
        settings.jwt_secret.encode(), signing_input.encode(), hashlib.sha256
    ).digest()


def create_access_token(*, sub: str, org_id: str, role: str) -> str:
    now = int(time.time())
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": sub,
        "org_id": org_id,
        "role": role,
        "iat": now,
        "exp": now + settings.jwt_expire_seconds,
    }
    signing_input = (
        _b64u(json.dumps(header, separators=(",", ":")).encode())
        + "."
        + _b64u(json.dumps(payload, separators=(",", ":")).encode())
    )
    return signing_input + "." + _b64u(_sign(signing_input))


def decode_token(token: str) -> dict:
    try:
        header_b64, payload_b64, sig_b64 = token.split(".")
    except ValueError:
        raise ValueError("malformed token")
    signing_input = f"{header_b64}.{payload_b64}"
    if not hmac.compare_digest(_sign(signing_input), _b64u_decode(sig_b64)):
        raise ValueError("bad signature")
    payload = json.loads(_b64u_decode(payload_b64))
    if int(payload.get("exp", 0)) < int(time.time()):
        raise ValueError("token expired")
    return payload
