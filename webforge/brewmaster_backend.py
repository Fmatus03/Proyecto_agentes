from __future__ import annotations

import re
from textwrap import dedent
from typing import Any

from .brewmaster_docs import _json
from .brewmaster_spec import _fallback_entities

def _backend_pyproject() -> str:
    return dedent(
        """
        [project]
        name = "brewmaster-api"
        version = "0.1.0"
        requires-python = ">=3.11"
        dependencies = [
          "fastapi",
          "uvicorn",
          "sqlalchemy",
          "alembic",
          "pydantic",
          "pymysql",
          "apscheduler",
          "python-jose",
          "passlib[bcrypt]",
          "openpyxl",
          "reportlab"
        ]
        """
    ).strip()


def _route_function_name(index: int, endpoint: dict[str, Any]) -> str:
    raw = f"{index}_{endpoint['method'].lower()}_{endpoint['path'].removeprefix('/api/v1/')}"
    cleaned = re.sub(r"[^0-9A-Za-z_]+", "_", raw.replace("{", "").replace("}", ""))
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return f"route_{cleaned}"


def _path_params(path: str) -> list[str]:
    return re.findall(r"\{([A-Za-z_][A-Za-z0-9_]*)\}", path)


def _route_payload(endpoint: dict[str, Any]) -> dict[str, Any]:
    return {
        "handler": endpoint["handler"],
        "method": endpoint["method"],
        "path": endpoint["path"],
        "transactional": bool(endpoint.get("transactional")),
        "source": endpoint.get("source", "generated"),
    }


def _explicit_route_blocks(endpoints: list[dict[str, Any]]) -> str:
    ordered = sorted(enumerate(endpoints, start=1), key=lambda item: ("{" in item[1]["path"], item[0]))
    blocks: list[str] = []
    for index, endpoint in ordered:
        method = endpoint["method"].lower()
        path = endpoint["path"]
        name = _route_function_name(index, endpoint)
        params = _path_params(path)
        signature = ", ".join(f"{param}: int" for param in params)
        payload = _route_payload(endpoint)
        if params:
            payload["path_params"] = {param: f"{{{param}}}" for param in params}
        blocks.append(
            "\n".join(
                [
                    f"@app.{method}({path!r})",
                    f"def {name}({signature}):",
                    f"    return ok({payload!r})",
                ]
            )
        )
    return "\n\n\n".join(blocks)


def _backend_main(blueprint: dict[str, Any]) -> str:
    if blueprint.get("milestone_id") == "HITO-001":
        return _hito1_backend_main()
    routes_json = _json(blueprint["endpoints"])
    route_blocks = _explicit_route_blocks(blueprint["endpoints"])
    header = dedent(
        f'''
        from fastapi import FastAPI, Request
        from fastapi.responses import JSONResponse

        from app.core.responses import ok
        from app.domain.catalog import ROUTE_CATALOG

        app = FastAPI(title="BrewMaster API", version="0.1.0", openapi_url="/api/v1/openapi.json")


        @app.middleware("http")
        async def add_request_id(request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", "REQ-LOCAL")
            return response


        @app.get("/api/v1/health")
        def health():
            return ok({{"status": "ok", "service": "brewmaster"}})


        @app.get("/api/v1/catalog/routes")
        def catalog_routes():
            return ok(ROUTE_CATALOG)

        @app.exception_handler(ValueError)
        async def value_error_handler(_: Request, exc: ValueError):
            return JSONResponse(status_code=422, content={{"error": {{"code": "validation_error", "message": str(exc), "details": []}}, "meta": {{"request_id": "REQ-LOCAL"}}}})


        ROUTE_CATALOG_SEED = {routes_json!r}
        '''
    ).strip()
    return header + "\n\n\n" + route_blocks


def _hito1_backend_main() -> str:
    return dedent(
        """
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

        EMAIL_RE = re.compile(r"^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$")
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
        """
    ).strip()


def _responses_py() -> str:
    return dedent(
        """
        from datetime import datetime, timezone
        from typing import Any


        def ok(data: Any, request_id: str = "REQ-LOCAL") -> dict[str, Any]:
            return {"data": data, "meta": {"request_id": request_id, "timestamp": datetime.now(timezone.utc).isoformat()}}


        def error(code: str, message: str, details: list[dict[str, str]] | None = None, request_id: str = "REQ-LOCAL") -> dict[str, Any]:
            return {"error": {"code": code, "message": message, "details": details or []}, "meta": {"request_id": request_id}}
        """
    ).strip()


def _security_py() -> str:
    return dedent(
        """
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
        """
    ).strip()


def _catalog_py(blueprint: dict[str, Any]) -> str:
    return "ROUTE_CATALOG = " + repr(blueprint["endpoints"]) + "\nMODULE_CATALOG = " + repr(blueprint["modules"]) + "\nSCREEN_CATALOG = " + repr(blueprint["screens"]) + "\n"


def _rules_py() -> str:
    return dedent(
        """
        from __future__ import annotations

        from dataclasses import dataclass


        @dataclass(frozen=True)
        class CostInput:
            supplies: float
            labor_hours: float
            labor_rate: float
            energy_kwh: float
            energy_rate: float
            water_liters: float
            water_rate: float
            waste_cost: float
            indirect_cost: float
            presentation_cost: float
            produced_liters: float
            produced_units: int


        def available_stock(current_stock: float, active_reservations: float) -> float:
            value = current_stock - active_reservations
            return value if value > 0 else 0


        def ensure_positive(value: float, field: str) -> None:
            if value <= 0:
                raise ValueError(f"{field}_must_be_greater_than_zero")


        def ensure_non_negative(value: float, field: str) -> None:
            if value < 0:
                raise ValueError(f"{field}_must_be_greater_or_equal_zero")


        def line_profit(unit_price: float, unit_cost: float, quantity: float) -> float:
            ensure_positive(quantity, "quantity")
            return (unit_price - unit_cost) * quantity


        def should_send_stock_alert(current_stock: float, minimum_stock: float, hours_since_last_alert: float | None) -> bool:
            if current_stock <= 0:
                return True
            if current_stock >= minimum_stock:
                return False
            return hours_since_last_alert is None or hours_since_last_alert >= 24


        def batch_cost(data: CostInput) -> dict[str, float]:
            for field, value in data.__dict__.items():
                if field != "produced_units":
                    ensure_non_negative(float(value), field)
            ensure_positive(data.produced_liters, "produced_liters")
            ensure_positive(float(data.produced_units), "produced_units")
            total = (
                data.supplies
                + data.labor_hours * data.labor_rate
                + data.energy_kwh * data.energy_rate
                + data.water_liters * data.water_rate
                + data.waste_cost
                + data.indirect_cost
                + data.presentation_cost * data.produced_units
            )
            return {
                "total": round(total, 4),
                "cost_per_liter": round(total / data.produced_liters, 4),
                "cost_per_unit": round(total / data.produced_units, 4),
            }
        """
    ).strip()


def _inventory_service_py() -> str:
    return dedent(
        """
        from app.domain.rules import available_stock, ensure_positive


        def register_supply_entry(stock: float, quantity: float) -> dict[str, float | str]:
            ensure_positive(quantity, "quantity")
            return {"stock_actual": stock + quantity, "movement": "ENTRADA"}


        def reserve_stock(current_stock: float, active_reservations: float, quantity: float) -> dict[str, float | str]:
            ensure_positive(quantity, "quantity")
            if quantity > available_stock(current_stock, active_reservations):
                raise ValueError("stock_unavailable")
            return {"reserved": quantity, "status": "activa"}
        """
    ).strip()


def _production_service_py() -> str:
    return dedent(
        """
        from app.domain.rules import CostInput, batch_cost, ensure_positive


        def complete_batch(cost_input: CostInput, stock_ok: bool) -> dict[str, object]:
            if not stock_ok:
                raise ValueError("stock_unavailable")
            ensure_positive(cost_input.produced_liters, "produced_liters")
            return {"state": "completado", "cost": batch_cost(cost_input), "kardex": "SALIDA_PRODUCCION"}
        """
    ).strip()


def _sales_service_py() -> str:
    return dedent(
        """
        from app.domain.rules import available_stock, ensure_positive, line_profit


        def confirm_sale(current_stock: float, active_reservations: float, quantity: float, unit_price: float, unit_cost: float) -> dict[str, float | str]:
            ensure_positive(quantity, "quantity")
            if quantity > available_stock(current_stock, active_reservations):
                raise ValueError("stock_unavailable")
            return {"movement": "VENTA", "remaining_stock": current_stock - quantity, "profit": line_profit(unit_price, unit_cost, quantity)}
        """
    ).strip()


def _purchasing_service_py() -> str:
    return dedent(
        """
        from app.domain.rules import ensure_positive


        def receive_order(requested: float, already_received: float, incoming: float, allow_over_receive: bool = False) -> dict[str, float | str]:
            ensure_positive(incoming, "incoming")
            pending = requested - already_received
            if incoming > pending and not allow_over_receive:
                raise ValueError("state_conflict")
            new_received = already_received + incoming
            status = "recibida" if new_received >= requested else "parcialmente_recibida"
            return {"cantidad_recibida": new_received, "estado": status, "movement": "ENTRADA"}
        """
    ).strip()


def _notifications_service_py() -> str:
    return dedent(
        """
        from app.domain.rules import should_send_stock_alert


        def enqueue_stock_alert(current_stock: float, minimum_stock: float, hours_since_last_alert: float | None) -> dict[str, object]:
            if not should_send_stock_alert(current_stock, minimum_stock, hours_since_last_alert):
                return {"queued": False, "reason": "interval_or_threshold_not_met"}
            return {"queued": True, "status": "pendiente", "max_attempts": 5}
        """
    ).strip()


def _entity_models(blueprint: dict[str, Any]) -> list[dict[str, Any]]:
    if blueprint.get("entity_models"):
        return blueprint["entity_models"]
    return _fallback_entities()


def _class_name(table_name: str) -> str:
    return "".join(part.title() for part in table_name.split("_"))


def _column_type(field: str, sqlalchemy_prefix: str = "") -> str:
    numeric_terms = [
        "cantidad",
        "stock",
        "costo",
        "precio",
        "total",
        "monto",
        "abv",
        "ibu",
        "kwh",
        "litros",
        "volumen",
        "porcentaje",
        "limite",
        "margen",
        "descuento",
        "temperatura",
        "temp",
        "og",
        "fg",
        "ph",
        "capacidad",
        "tolerancia",
    ]
    date_terms = ["fecha", "_at", "expires", "used_at", "sent_at", "completed_at", "revision"]
    bool_terms = ["enable_", "use_", "temperatura_controlada"]
    if field == "id" or field.endswith("_id") or field in {"port", "attempts", "produced_units", "num_clientes"}:
        return f"{sqlalchemy_prefix}Integer()"
    if any(term in field for term in bool_terms):
        return f"{sqlalchemy_prefix}Boolean()"
    if any(term in field for term in date_terms):
        return f"{sqlalchemy_prefix}DateTime()"
    if any(term in field for term in numeric_terms):
        return f"{sqlalchemy_prefix}Numeric(12, 4)"
    return f"{sqlalchemy_prefix}String(255)"


def _unique_fields(fields: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for field in fields:
        if field not in seen:
            seen.add(field)
            result.append(field)
    return result


def _models_py(blueprint: dict[str, Any]) -> str:
    tables: list[str] = []
    for entity in _entity_models(blueprint):
        fields = _unique_fields(entity["fields"])
        columns: list[str] = []
        for field in fields:
            if field == "id":
                columns.append("    id = Column(Integer, primary_key=True)")
                continue
            nullable = "False" if field in {"created_at", "updated_at"} else "True"
            columns.append(f"    {field} = Column({_column_type(field)}, nullable={nullable})")
        if not any(column.startswith("    id = ") for column in columns):
            columns.insert(0, "    id = Column(Integer, primary_key=True)")
        tables.append(
            "\n".join(
                [
                    f"class {_class_name(entity['name'])}(Base):",
                    f"    __tablename__ = {entity['name']!r}",
                    *columns,
                    "",
                ]
            )
        )
    return dedent(
        """
        from sqlalchemy import Boolean, Column, DateTime, Integer, Numeric, String
        from sqlalchemy.orm import declarative_base


        Base = declarative_base()

        """
    ).strip() + "\n\n" + "\n".join(tables)


def _session_py() -> str:
    return dedent(
        """
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker


        def make_session_factory(database_url: str):
            engine = create_engine(database_url, pool_pre_ping=True, future=True)
            return sessionmaker(engine, autoflush=False, autocommit=False, future=True)
        """
    ).strip()


def _scheduler_py() -> str:
    return dedent(
        """
        JOBS = [
            "stock_alerts",
            "email_retries",
            "reservation_expiration",
            "deferred_exports",
            "low_activity_backup",
        ]


        def job_policy() -> dict[str, object]:
            return {"scheduler": "APScheduler", "jobs": JOBS, "idempotent": True, "blocking_main_flow": False}
        """
    ).strip()


def _alembic_env_py() -> str:
    return "from app.db.models import Base\n\ntarget_metadata = Base.metadata\n"


def _migration_py(blueprint: dict[str, Any]) -> str:
    lines = [
        "from alembic import op",
        "import sqlalchemy as sa",
        "",
        "revision = '0001_brewmaster_schema'",
        "down_revision = None",
        "branch_labels = None",
        "depends_on = None",
        "",
        "",
        "def upgrade():",
    ]
    for entity in _entity_models(blueprint):
        fields = _unique_fields(entity["fields"])
        if "id" not in fields:
            fields.insert(0, "id")
        lines.append(f"    op.create_table({entity['name']!r},")
        for field in fields:
            if field == "id":
                lines.append("        sa.Column('id', sa.Integer(), primary_key=True),")
            else:
                nullable = "False" if field in {"created_at", "updated_at"} else "True"
                lines.append(f"        sa.Column({field!r}, {_column_type(field, 'sa.')}, nullable={nullable}),")
        lines.append("    )")
        if "estado" in fields:
            lines.append(f"    op.create_index('ix_{entity['name']}_estado', {entity['name']!r}, ['estado'])")
        if "created_at" in fields:
            lines.append(f"    op.create_index('ix_{entity['name']}_created_at', {entity['name']!r}, ['created_at'])")
        lines.append("")
    lines.extend(["", "def downgrade():"])
    for entity in reversed(_entity_models(blueprint)):
        fields = entity["fields"]
        if "created_at" in fields:
            lines.append(f"    op.drop_index('ix_{entity['name']}_created_at', table_name={entity['name']!r})")
        if "estado" in fields:
            lines.append(f"    op.drop_index('ix_{entity['name']}_estado', table_name={entity['name']!r})")
        lines.append(f"    op.drop_table({entity['name']!r})")
    return "\n".join(lines)
