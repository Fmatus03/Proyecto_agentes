from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import re
import secrets
from typing import Any

from fastapi import Body, Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from app.core.responses import ok
from app.core.security import create_access_token, hash_password, require_permission, verify_password, verify_token
from app.domain.catalog import ROUTE_CATALOG

app = FastAPI(title="BrewMaster API", version="0.1.0", openapi_url="/api/v1/openapi.json")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
RESET_TOKEN_TTL_MINUTES = 30
AUDIT_LOGS: list[dict[str, Any]] = []
RESET_RECORDS: dict[str, dict[str, Any]] = {}
ROLES: dict[str, dict[str, Any]] = {
    "admin": {"id": 1, "nombre": "admin", "estado": "activo", "permissions": ["*"]},
    "auditor": {"id": 2, "nombre": "auditor", "estado": "activo", "permissions": ["audit.read"]},
    "operador": {"id": 3, "nombre": "operador", "estado": "activo", "permissions": []},
}
USERS: dict[int, dict[str, Any]] = {}
NEXT_USER_ID = 2


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime | None = None) -> str:
    return (value or _now()).isoformat()


USERS[1] = {
    "id": 1,
    "nombre": "Admin",
    "email": "admin@brewmaster.local",
    "password_hash": hash_password("Admin123!"),
    "role": "admin",
    "estado": "activo",
    "created_at": _iso(),
    "updated_at": _iso(),
}


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", "REQ-LOCAL")
    return response


@app.exception_handler(HTTPException)
async def http_error_handler(_: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, dict) else {"code": "http_error", "message": str(exc.detail)}
    return JSONResponse(status_code=exc.status_code, content={"error": {"code": detail.get("code", "http_error"), "message": detail.get("message", "request_error"), "details": detail.get("details", [])}, "meta": {"request_id": "REQ-LOCAL"}})


@app.exception_handler(ValueError)
async def value_error_handler(_: Request, exc: ValueError):
    return JSONResponse(status_code=422, content={"error": {"code": "validation_error", "message": str(exc), "details": []}, "meta": {"request_id": "REQ-LOCAL"}})


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "local"


def _audit(request: Request, user_id: int | None, action: str, entity: str, entity_id: int | None = None, detail: str = "") -> None:
    AUDIT_LOGS.append(
        {
            "id": len(AUDIT_LOGS) + 1,
            "user_id": user_id,
            "action": action,
            "entity": entity,
            "entity_id": entity_id,
            "detail": detail,
            "ip_address": _client_ip(request),
            "created_at": _iso(),
        }
    )


def _public_user(user: dict[str, Any]) -> dict[str, Any]:
    role = ROLES.get(str(user["role"]), {"permissions": []})
    return {
        "id": user["id"],
        "nombre": user["nombre"],
        "email": user["email"],
        "role": user["role"],
        "estado": user["estado"],
        "permissions": role.get("permissions", []),
        "created_at": user["created_at"],
        "updated_at": user["updated_at"],
    }


def _find_user_by_email(email: str) -> dict[str, Any] | None:
    normalized = email.strip().lower()
    return next((user for user in USERS.values() if user["email"].lower() == normalized), None)


def _validate_email(email: str) -> str:
    normalized = email.strip().lower()
    if not EMAIL_RE.match(normalized):
        raise HTTPException(422, {"code": "validation_error", "message": "email_invalid"})
    return normalized


def _validate_new_pwd(raw_value: str) -> str:
    if len(raw_value) < 8:
        raise HTTPException(422, {"code": "validation_error", "message": "password_min_length"})
    return raw_value


def _role_or_422(role_name: str) -> dict[str, Any]:
    role = ROLES.get(role_name)
    if not role:
        raise HTTPException(422, {"code": "validation_error", "message": "role_required"})
    if role["estado"] != "activo":
        raise HTTPException(422, {"code": "inactive_entity", "message": "role_inactive"})
    return role


def _current_user(authorization: str | None = Header(None)) -> dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, {"code": "auth_error", "message": "missing_bearer_token"})
    payload = verify_token(authorization.removeprefix("Bearer ").strip())
    user = USERS.get(int(payload["sub"]))
    if not user or user["estado"] != "activo":
        raise HTTPException(401, {"code": "auth_error", "message": "inactive_or_unknown_user"})
    return user


def _require_admin(user: dict[str, Any] = Depends(_current_user)) -> dict[str, Any]:
    role = ROLES.get(str(user["role"]), {"permissions": []})
    try:
        require_permission(set(role.get("permissions", [])), "admin.users")
    except PermissionError:
        raise HTTPException(403, {"code": "permission_denied", "message": "admin_users_required"})
    return user


def _require_audit(user: dict[str, Any] = Depends(_current_user)) -> dict[str, Any]:
    role = ROLES.get(str(user["role"]), {"permissions": []})
    try:
        require_permission(set(role.get("permissions", [])), "audit.read")
    except PermissionError:
        raise HTTPException(403, {"code": "permission_denied", "message": "audit_read_required"})
    return user


@app.get("/api/v1/health")
def health():
    return ok({"status": "ok", "service": "brewmaster", "milestone": "HITO-001"})


@app.get("/api/v1/catalog/routes")
def catalog_routes():
    return ok(ROUTE_CATALOG)


@app.post("/api/v1/auth/login")
def login(request: Request, body: dict[str, Any] = Body(...)):
    email = _validate_email(str(body.get("email", "")))
    pwd_value = str(body.get("password", ""))
    user = _find_user_by_email(email)
    if not user or not verify_password(pwd_value, user["password_hash"]):
        _audit(request, user["id"] if user else None, "login_failed", "users", user["id"] if user else None, "invalid_credentials")
        raise HTTPException(401, {"code": "auth_error", "message": "invalid_credentials"})
    if user["estado"] != "activo":
        _audit(request, user["id"], "login_failed", "users", user["id"], "inactive_user")
        raise HTTPException(401, {"code": "auth_error", "message": "inactive_user"})
    role = _role_or_422(str(user["role"]))
    jwt_value = create_access_token(str(user["id"]), role.get("permissions", []), {"role": user["role"]})
    _audit(request, user["id"], "login_success", "users", user["id"], "jwt_issued")
    return ok({"access_token": jwt_value, "token_type": "bearer", "expires_in": 3600, "user": _public_user(user)})


@app.post("/api/v1/auth/logout")
def logout(request: Request, user: dict[str, Any] = Depends(_current_user)):
    _audit(request, user["id"], "logout", "users", user["id"], "session_closed")
    return ok({"status": "logged_out"})


@app.get("/api/v1/auth/me")
def me(user: dict[str, Any] = Depends(_current_user)):
    return ok(_public_user(user))


@app.post("/api/v1/auth/change-password")
def change_password(request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
    current_pwd = str(body.get("current_password", ""))
    new_pwd = _validate_new_pwd(str(body.get("new_password", "")))
    if not verify_password(current_pwd, user["password_hash"]):
        raise HTTPException(401, {"code": "auth_error", "message": "current_password_invalid"})
    user["password_hash"] = hash_password(new_pwd)
    user["updated_at"] = _iso()
    _audit(request, user["id"], "password_changed", "users", user["id"], "changed_by_user")
    return ok({"status": "password_changed"})


@app.post("/api/v1/auth/password-reset/request")
def request_password_reset(request: Request, body: dict[str, Any] = Body(...)):
    email = _validate_email(str(body.get("email", "")))
    user = _find_user_by_email(email)
    response: dict[str, Any] = {"status": "reset_requested"}
    if user and user["estado"] == "activo":
        reset_value = secrets.token_urlsafe(16)
        reset_hash = hashlib.sha256(reset_value.encode("utf-8")).hexdigest()
        RESET_RECORDS[reset_hash] = {
            "user_id": user["id"],
            "expires_at": _now() + timedelta(minutes=RESET_TOKEN_TTL_MINUTES),
            "used_at": None,
        }
        response["local_delivery"] = reset_value
        _audit(request, user["id"], "password_reset_requested", "password_reset_tokens", None, "local_delivery")
    return ok(response)


@app.post("/api/v1/auth/password-reset/confirm")
def confirm_password_reset(request: Request, body: dict[str, Any] = Body(...)):
    token_value = str(body.get("token", ""))
    new_pwd = _validate_new_pwd(str(body.get("new_password", "")))
    reset_hash = hashlib.sha256(token_value.encode("utf-8")).hexdigest()
    record = RESET_RECORDS.get(reset_hash)
    if not record or record["used_at"] is not None or record["expires_at"] < _now():
        raise HTTPException(401, {"code": "auth_error", "message": "reset_token_invalid"})
    user = USERS.get(int(record["user_id"]))
    if not user or user["estado"] != "activo":
        raise HTTPException(401, {"code": "auth_error", "message": "inactive_or_unknown_user"})
    user["password_hash"] = hash_password(new_pwd)
    user["updated_at"] = _iso()
    record["used_at"] = _now()
    _audit(request, user["id"], "password_reset_confirmed", "users", user["id"], "token_used")
    return ok({"status": "password_reset_confirmed"})


@app.get("/api/v1/users")
def list_users(_: dict[str, Any] = Depends(_require_admin)):
    return ok([_public_user(user) for user in USERS.values()])


@app.post("/api/v1/users")
def create_user(request: Request, body: dict[str, Any] = Body(...), admin_user: dict[str, Any] = Depends(_require_admin)):
    global NEXT_USER_ID
    email = _validate_email(str(body.get("email", "")))
    if _find_user_by_email(email):
        raise HTTPException(422, {"code": "duplicate_record", "message": "email_already_exists"})
    role_name = str(body.get("role", "")).strip()
    _role_or_422(role_name)
    pwd_value = _validate_new_pwd(str(body.get("password", "")))
    user_id = NEXT_USER_ID
    NEXT_USER_ID += 1
    USERS[user_id] = {
        "id": user_id,
        "nombre": str(body.get("nombre", "")).strip() or email,
        "email": email,
        "password_hash": hash_password(pwd_value),
        "role": role_name,
        "estado": "activo",
        "created_at": _iso(),
        "updated_at": _iso(),
    }
    _audit(request, admin_user["id"], "user_created", "users", user_id, "admin.users")
    return ok(_public_user(USERS[user_id]))


@app.get("/api/v1/users/{id}")
def get_user(id: int, _: dict[str, Any] = Depends(_require_admin)):
    user = USERS.get(id)
    if not user:
        raise HTTPException(404, {"code": "not_found", "message": "user_not_found"})
    return ok(_public_user(user))


@app.put("/api/v1/users/{id}")
def update_user(id: int, request: Request, body: dict[str, Any] = Body(...), admin_user: dict[str, Any] = Depends(_require_admin)):
    user = USERS.get(id)
    if not user:
        raise HTTPException(404, {"code": "not_found", "message": "user_not_found"})
    if "email" in body:
        email = _validate_email(str(body["email"]))
        duplicate = _find_user_by_email(email)
        if duplicate and duplicate["id"] != id:
            raise HTTPException(422, {"code": "duplicate_record", "message": "email_already_exists"})
        user["email"] = email
    if "role" in body:
        role_name = str(body["role"]).strip()
        _role_or_422(role_name)
        user["role"] = role_name
    if "nombre" in body:
        user["nombre"] = str(body["nombre"]).strip() or user["nombre"]
    if "estado" in body:
        state = str(body["estado"]).strip()
        if state not in {"activo", "inactivo"}:
            raise HTTPException(422, {"code": "validation_error", "message": "invalid_user_state"})
        user["estado"] = state
    user["updated_at"] = _iso()
    _audit(request, admin_user["id"], "user_updated", "users", id, "admin.users")
    return ok(_public_user(user))


@app.patch("/api/v1/users/{id}/toggle-status")
def toggle_user_status(id: int, request: Request, admin_user: dict[str, Any] = Depends(_require_admin)):
    user = USERS.get(id)
    if not user:
        raise HTTPException(404, {"code": "not_found", "message": "user_not_found"})
    user["estado"] = "inactivo" if user["estado"] == "activo" else "activo"
    user["updated_at"] = _iso()
    _audit(request, admin_user["id"], "user_status_toggled", "users", id, user["estado"])
    return ok(_public_user(user))


@app.get("/api/v1/audit-logs")
def list_audit_logs(_: dict[str, Any] = Depends(_require_audit)):
    return ok(AUDIT_LOGS)
