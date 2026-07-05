from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import secrets
from typing import Any

from fastapi import HTTPException

SENSITIVE_PERMISSIONS = {"costs:read", "financial:read", "smtp:update", "users:write", "admin.users", "audit.read"}
SIGNING_KEY = hashlib.sha256(b"brewmaster-local-dev-signing-key").digest()
HASH_ITERATIONS = 120000
ACCESS_TOKEN_MINUTES = 60


def require_permission(user_permissions: set[str], required: str) -> None:
    if "*" in user_permissions or required in user_permissions:
        return
    raise PermissionError("permission_denied")


def can_view_costs(user_permissions: set[str]) -> bool:
    return "*" in user_permissions or "costs:read" in user_permissions or "financial:read" in user_permissions


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


def hash_password(raw_value: str, salt: str | None = None) -> str:
    salt_value = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", raw_value.encode("utf-8"), salt_value.encode("utf-8"), HASH_ITERATIONS)
    return f"pbkdf2_sha256${HASH_ITERATIONS}${salt_value}${digest.hex()}"


def verify_password(raw_value: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, salt_value, expected = stored_hash.split("$", 3)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    digest = hashlib.pbkdf2_hmac("sha256", raw_value.encode("utf-8"), salt_value.encode("utf-8"), int(iterations))
    return hmac.compare_digest(digest.hex(), expected)


def create_access_token(subject: str, permissions: list[str], extra: dict[str, Any] | None = None) -> str:
    issued_at = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "permissions": permissions,
        "iat": int(issued_at.timestamp()),
        "exp": int((issued_at + timedelta(minutes=ACCESS_TOKEN_MINUTES)).timestamp()),
    }
    if extra:
        payload.update(extra)
    header = {"alg": "HS256", "typ": "JWT"}
    signing_input = ".".join(
        [
            _b64url_encode(json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")),
            _b64url_encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")),
        ]
    )
    signature = hmac.new(SIGNING_KEY, signing_input.encode("ascii"), hashlib.sha256).digest()
    return signing_input + "." + _b64url_encode(signature)


def verify_token(jwt_value: str) -> dict[str, Any]:
    try:
        header_part, payload_part, signature_part = jwt_value.split(".", 2)
        signing_input = f"{header_part}.{payload_part}"
        expected = hmac.new(SIGNING_KEY, signing_input.encode("ascii"), hashlib.sha256).digest()
        if not hmac.compare_digest(_b64url_decode(signature_part), expected):
            raise ValueError("bad_signature")
        payload = json.loads(_b64url_decode(payload_part))
        if int(payload.get("exp", 0)) < int(datetime.now(timezone.utc).timestamp()):
            raise ValueError("expired")
        if not payload.get("sub"):
            raise ValueError("missing_subject")
        return payload
    except Exception:
        raise HTTPException(401, {"code": "auth_error", "message": "invalid_or_expired_token"})
