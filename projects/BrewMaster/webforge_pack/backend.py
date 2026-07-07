from __future__ import annotations

import re
from textwrap import dedent
from typing import Any

from .docs import _json
from .spec import _fallback_entities

def _backend_pyproject(milestone_id: str | None = None) -> str:
    if (milestone_id or "").strip().upper() in {"HITO-001", "HITO-002", "HITO-003", "HITO-004", "HITO-005"}:
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
              "pymysql"
            ]
            """
        ).strip()
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
    if blueprint.get("milestone_id") == "HITO-002":
        return _hito2_backend_main()
    if blueprint.get("milestone_id") == "HITO-003":
        return _hito3_backend_main()
    if blueprint.get("milestone_id") == "HITO-004":
        return _hito4_backend_main()
    if blueprint.get("milestone_id") == "HITO-005":
        return _hito5_backend_main()
    if blueprint.get("milestone_id") == "HITO-006":
        return _hito6_backend_main()
    if blueprint.get("milestone_id") == "HITO-007":
        return _hito7_backend_main()
    if blueprint.get("milestone_id") == "HITO-008":
        return _hito7_backend_main().replace('"milestone": "HITO-007"', '"milestone": "HITO-008"')
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


def _hito2_backend_main() -> str:
    hito1 = _hito1_backend_main().replace('"milestone": "HITO-001"', '"milestone": "HITO-002"')
    hito2 = dedent(
        """


        # HITO-002 maestros: proveedores, insumos, bodegas, recetas y tipos de presentacion.
        ROLES["compras"] = {
            "id": 4,
            "nombre": "compras",
            "estado": "activo",
            "permissions": ["suppliers.read", "suppliers.create", "suppliers.update", "supplies.read", "supplies.create", "supplies.update", "supplies.toggle-status"],
        }
        ROLES["produccion"] = {
            "id": 5,
            "nombre": "produccion",
            "estado": "activo",
            "permissions": ["supplies.read", "recipes.read", "recipes.create", "recipes.update", "recipes.clone"],
        }

        MASTER_STATES = {"activo", "inactivo"}
        RECIPE_STATES = {"activo", "inactivo", "en_prueba"}
        SUPPLY_TYPES = {"malta", "lupulo", "levadura", "adjunto", "envase", "limpieza", "otro"}
        SUPPLIERS: dict[int, dict[str, Any]] = {}
        WAREHOUSES: dict[int, dict[str, Any]] = {}
        SUPPLIES: dict[int, dict[str, Any]] = {}
        PRESENTATION_TYPES: dict[int, dict[str, Any]] = {}
        RECIPES: dict[int, dict[str, Any]] = {}
        NEXT_MASTER_ID = {
            "supplier": 1,
            "warehouse": 1,
            "supply": 1,
            "presentation": 1,
            "recipe": 1,
        }


        def _next_master_id(kind: str) -> int:
            value = NEXT_MASTER_ID[kind]
            NEXT_MASTER_ID[kind] += 1
            return value


        def _permissions_for(user: dict[str, Any]) -> set[str]:
            role = ROLES.get(str(user["role"]), {"permissions": []})
            return set(role.get("permissions", []))


        def _ensure_permission(user: dict[str, Any], permission: str) -> None:
            try:
                require_permission(_permissions_for(user), permission)
            except PermissionError:
                raise HTTPException(403, {"code": "permission_denied", "message": permission})


        def _required_text(body: dict[str, Any], field: str, alias: str | None = None) -> str:
            raw_value = body.get(field, body.get(alias, "")) if alias else body.get(field, "")
            value = str(raw_value or "").strip()
            if not value:
                raise HTTPException(422, {"code": "validation_error", "message": f"{field}_required"})
            return value


        def _optional_text(body: dict[str, Any], field: str, default: str = "") -> str:
            return str(body.get(field, default) or "").strip()


        def _state(body: dict[str, Any], allowed: set[str] = MASTER_STATES, default: str = "activo") -> str:
            value = str(body.get("estado", default) or default).strip()
            if value not in allowed:
                raise HTTPException(422, {"code": "validation_error", "message": "invalid_state"})
            return value


        def _non_negative(value: Any, field: str) -> float:
            try:
                number = float(value)
            except (TypeError, ValueError):
                raise HTTPException(422, {"code": "validation_error", "message": f"{field}_invalid"})
            if number < 0:
                raise HTTPException(422, {"code": "validation_error", "message": f"{field}_must_be_non_negative"})
            return number


        def _positive(value: Any, field: str) -> float:
            number = _non_negative(value, field)
            if number <= 0:
                raise HTTPException(422, {"code": "validation_error", "message": f"{field}_must_be_positive"})
            return number


        def _optional_email(value: str) -> str:
            email = str(value or "").strip().lower()
            if email and not EMAIL_RE.match(email):
                raise HTTPException(422, {"code": "validation_error", "message": "email_invalid"})
            return email


        def _get(store: dict[int, dict[str, Any]], item_id: int, label: str) -> dict[str, Any]:
            item = store.get(item_id)
            if not item:
                raise HTTPException(404, {"code": "not_found", "message": f"{label}_not_found"})
            return item


        def _ensure_unique(store: dict[int, dict[str, Any]], field: str, value: str, current_id: int | None = None) -> None:
            normalized = value.strip().lower()
            for item_id, item in store.items():
                if current_id is not None and item_id == current_id:
                    continue
                if str(item.get(field, "")).strip().lower() == normalized:
                    raise HTTPException(422, {"code": "duplicate_record", "message": f"{field}_already_exists"})


        def _timestamps(record: dict[str, Any], creating: bool = False) -> dict[str, Any]:
            if creating:
                record["created_at"] = _iso()
            record["updated_at"] = _iso()
            return record


        def _is_active(record: dict[str, Any]) -> bool:
            return record.get("estado") == "activo"


        def _active_supplier(supplier_id: int) -> dict[str, Any]:
            supplier = _get(SUPPLIERS, supplier_id, "supplier")
            if not _is_active(supplier):
                raise HTTPException(422, {"code": "inactive_entity", "message": "supplier_inactive"})
            return supplier


        def _active_warehouse(warehouse_id: int) -> dict[str, Any]:
            warehouse = _get(WAREHOUSES, warehouse_id, "warehouse")
            if not _is_active(warehouse):
                raise HTTPException(422, {"code": "inactive_entity", "message": "warehouse_inactive"})
            return warehouse


        def _active_supply(supply_id: int) -> dict[str, Any]:
            supply = _get(SUPPLIES, supply_id, "supply")
            if not _is_active(supply):
                raise HTTPException(422, {"code": "inactive_entity", "message": "supply_inactive"})
            return supply


        def _recipe_uses_supply(supply_id: int) -> bool:
            for recipe in RECIPES.values():
                if recipe.get("estado") not in {"activo", "en_prueba"}:
                    continue
                for ingredient in recipe.get("ingredientes", []):
                    if int(ingredient.get("supply_id", 0)) == supply_id:
                        return True
            return False


        def _ingredient_payload(raw_items: Any) -> list[dict[str, Any]]:
            if not isinstance(raw_items, list) or not raw_items:
                raise HTTPException(422, {"code": "validation_error", "message": "recipe_ingredients_required"})
            ingredients: list[dict[str, Any]] = []
            seen: set[int] = set()
            for raw in raw_items:
                if not isinstance(raw, dict):
                    raise HTTPException(422, {"code": "validation_error", "message": "ingredient_invalid"})
                supply_id = int(raw.get("supply_id", 0))
                if supply_id in seen:
                    raise HTTPException(422, {"code": "duplicate_record", "message": "ingredient_duplicate"})
                seen.add(supply_id)
                supply = _active_supply(supply_id)
                quantity = _positive(raw.get("cantidad"), "ingredient_quantity")
                unit = str(raw.get("unidad", supply.get("unidad_medida", "")) or "").strip()
                if not unit:
                    raise HTTPException(422, {"code": "validation_error", "message": "ingredient_unit_required"})
                ingredients.append(
                    {
                        "supply_id": supply_id,
                        "nombre_insumo": supply["nombre"],
                        "cantidad": quantity,
                        "unidad": unit,
                        "costo_unitario": supply["costo_unitario"],
                        "costo_total": round(quantity * float(supply["costo_unitario"]), 4),
                    }
                )
            return ingredients


        def _recipe_cost(ingredients: list[dict[str, Any]]) -> float:
            return round(sum(float(item["costo_total"]) for item in ingredients), 4)


        def _filtered(items: list[dict[str, Any]], estado: str | None, text: str | None) -> list[dict[str, Any]]:
            result = items
            if estado:
                result = [item for item in result if item.get("estado") == estado]
            if text:
                needle = text.strip().lower()
                result = [
                    item
                    for item in result
                    if needle in str(item.get("nombre", "")).lower() or needle in str(item.get("codigo", "")).lower()
                ]
            return result


        @app.get("/api/v1/suppliers")
        def list_suppliers(estado: str | None = None, nombre: str | None = None, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "suppliers.read")
            return ok(_filtered(list(SUPPLIERS.values()), estado, nombre))


        @app.post("/api/v1/suppliers")
        def create_supplier(request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "suppliers.create")
            code = _required_text(body, "codigo")
            _ensure_unique(SUPPLIERS, "codigo", code)
            supplier_id = _next_master_id("supplier")
            supplier = _timestamps(
                {
                    "id": supplier_id,
                    "codigo": code,
                    "nombre": _required_text(body, "nombre", "razon_social"),
                    "email": _optional_email(_optional_text(body, "email")),
                    "telefono": _optional_text(body, "telefono"),
                    "direccion": _optional_text(body, "direccion"),
                    "contacto": _optional_text(body, "contacto", _optional_text(body, "contacto_principal")),
                    "tipo_insumos": _optional_text(body, "tipo_insumos"),
                    "condicion_pago": _optional_text(body, "condicion_pago"),
                    "estado": _state(body),
                },
                creating=True,
            )
            SUPPLIERS[supplier_id] = supplier
            _audit(request, user["id"], "supplier_created", "suppliers", supplier_id, "HITO-002")
            return ok(supplier)


        @app.put("/api/v1/suppliers/{id}")
        def update_supplier(id: int, request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "suppliers.update")
            supplier = _get(SUPPLIERS, id, "supplier")
            if "codigo" in body:
                code = _required_text(body, "codigo")
                _ensure_unique(SUPPLIERS, "codigo", code, current_id=id)
                supplier["codigo"] = code
            if "nombre" in body or "razon_social" in body:
                supplier["nombre"] = _required_text(body, "nombre", "razon_social")
            if "email" in body:
                supplier["email"] = _optional_email(_optional_text(body, "email"))
            for field in ["telefono", "direccion", "contacto", "tipo_insumos", "condicion_pago"]:
                if field in body:
                    supplier[field] = _optional_text(body, field)
            if "estado" in body:
                supplier["estado"] = _state(body)
            _timestamps(supplier)
            _audit(request, user["id"], "supplier_updated", "suppliers", id, "HITO-002")
            return ok(supplier)


        @app.patch("/api/v1/suppliers/{id}/toggle-status")
        def toggle_supplier_status(id: int, request: Request, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "suppliers.update")
            supplier = _get(SUPPLIERS, id, "supplier")
            supplier["estado"] = "inactivo" if supplier["estado"] == "activo" else "activo"
            _timestamps(supplier)
            _audit(request, user["id"], "supplier_status_toggled", "suppliers", id, supplier["estado"])
            return ok(supplier)


        @app.get("/api/v1/warehouses")
        def list_warehouses(estado: str | None = None, nombre: str | None = None, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "supplies.read")
            return ok(_filtered(list(WAREHOUSES.values()), estado, nombre))


        @app.post("/api/v1/warehouses")
        def create_warehouse(request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "supplies.update")
            code = _required_text(body, "codigo")
            _ensure_unique(WAREHOUSES, "codigo", code)
            warehouse_id = _next_master_id("warehouse")
            warehouse = _timestamps(
                {
                    "id": warehouse_id,
                    "codigo": code,
                    "nombre": _required_text(body, "nombre"),
                    "tipo": _required_text(body, "tipo"),
                    "responsable": _optional_text(body, "responsable"),
                    "capacidad": _non_negative(body.get("capacidad", 0), "capacidad"),
                    "temperatura_controlada": bool(body.get("temperatura_controlada", False)),
                    "estado": _state(body),
                },
                creating=True,
            )
            WAREHOUSES[warehouse_id] = warehouse
            _audit(request, user["id"], "warehouse_created", "warehouses", warehouse_id, "HITO-002")
            return ok(warehouse)


        @app.put("/api/v1/warehouses/{id}")
        def update_warehouse(id: int, request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "supplies.update")
            warehouse = _get(WAREHOUSES, id, "warehouse")
            if "codigo" in body:
                code = _required_text(body, "codigo")
                _ensure_unique(WAREHOUSES, "codigo", code, current_id=id)
                warehouse["codigo"] = code
            for field in ["nombre", "tipo"]:
                if field in body:
                    warehouse[field] = _required_text(body, field)
            if "responsable" in body:
                warehouse["responsable"] = _optional_text(body, "responsable")
            if "capacidad" in body:
                warehouse["capacidad"] = _non_negative(body.get("capacidad"), "capacidad")
            if "temperatura_controlada" in body:
                warehouse["temperatura_controlada"] = bool(body.get("temperatura_controlada"))
            if "estado" in body:
                warehouse["estado"] = _state(body)
            _timestamps(warehouse)
            _audit(request, user["id"], "warehouse_updated", "warehouses", id, "HITO-002")
            return ok(warehouse)


        @app.get("/api/v1/supplies")
        def list_supplies(estado: str | None = None, nombre: str | None = None, tipo: str | None = None, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "supplies.read")
            result = _filtered(list(SUPPLIES.values()), estado, nombre)
            if tipo:
                result = [item for item in result if item.get("tipo") == tipo]
            return ok(result)


        @app.post("/api/v1/supplies")
        def create_supply(request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "supplies.create")
            code = _required_text(body, "codigo")
            _ensure_unique(SUPPLIES, "codigo", code)
            supply_type = _required_text(body, "tipo")
            if supply_type not in SUPPLY_TYPES:
                raise HTTPException(422, {"code": "validation_error", "message": "supply_type_invalid"})
            minimum_stock = _non_negative(body.get("stock_minimo", 0), "stock_minimo")
            maximum_stock = body.get("stock_maximo")
            maximum_stock_value = None if maximum_stock in {None, ""} else _non_negative(maximum_stock, "stock_maximo")
            if maximum_stock_value is not None and maximum_stock_value < minimum_stock:
                raise HTTPException(422, {"code": "validation_error", "message": "stock_maximo_less_than_minimo"})
            supplier_id = int(body.get("proveedor_id", 0))
            warehouse_id = int(body.get("bodega_id", 0))
            _active_supplier(supplier_id)
            _active_warehouse(warehouse_id)
            supply_id = _next_master_id("supply")
            supply = _timestamps(
                {
                    "id": supply_id,
                    "codigo": code,
                    "nombre": _required_text(body, "nombre"),
                    "descripcion": _optional_text(body, "descripcion"),
                    "tipo": supply_type,
                    "unidad_medida": _required_text(body, "unidad_medida"),
                    "proveedor_id": supplier_id,
                    "bodega_id": warehouse_id,
                    "costo_unitario": _non_negative(body.get("costo_unitario", 0), "costo_unitario"),
                    "stock_minimo": minimum_stock,
                    "stock_maximo": maximum_stock_value,
                    "stock_actual": _non_negative(body.get("stock_actual", 0), "stock_actual"),
                    "fecha_vencimiento": _optional_text(body, "fecha_vencimiento"),
                    "enable_email_alerts": bool(body.get("enable_email_alerts", False)),
                    "alert_emails": list(body.get("alert_emails", [])) if isinstance(body.get("alert_emails", []), list) else [],
                    "estado": _state(body),
                },
                creating=True,
            )
            SUPPLIES[supply_id] = supply
            _audit(request, user["id"], "supply_created", "supplies", supply_id, "HITO-002")
            return ok(supply)


        @app.get("/api/v1/supplies/{id}")
        def get_supply(id: int, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "supplies.read")
            return ok(_get(SUPPLIES, id, "supply"))


        @app.put("/api/v1/supplies/{id}")
        def update_supply(id: int, request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "supplies.update")
            supply = _get(SUPPLIES, id, "supply")
            if "codigo" in body:
                code = _required_text(body, "codigo")
                _ensure_unique(SUPPLIES, "codigo", code, current_id=id)
                supply["codigo"] = code
            if "nombre" in body:
                supply["nombre"] = _required_text(body, "nombre")
            if "descripcion" in body:
                supply["descripcion"] = _optional_text(body, "descripcion")
            if "tipo" in body:
                supply_type = _required_text(body, "tipo")
                if supply_type not in SUPPLY_TYPES:
                    raise HTTPException(422, {"code": "validation_error", "message": "supply_type_invalid"})
                supply["tipo"] = supply_type
            if "unidad_medida" in body:
                supply["unidad_medida"] = _required_text(body, "unidad_medida")
            if "proveedor_id" in body:
                supplier_id = int(body.get("proveedor_id", 0))
                _active_supplier(supplier_id)
                supply["proveedor_id"] = supplier_id
            if "bodega_id" in body:
                warehouse_id = int(body.get("bodega_id", 0))
                _active_warehouse(warehouse_id)
                supply["bodega_id"] = warehouse_id
            for field in ["costo_unitario", "stock_minimo", "stock_actual"]:
                if field in body:
                    supply[field] = _non_negative(body.get(field), field)
            if "stock_maximo" in body:
                max_value = body.get("stock_maximo")
                supply["stock_maximo"] = None if max_value in {None, ""} else _non_negative(max_value, "stock_maximo")
            if supply.get("stock_maximo") is not None and supply["stock_maximo"] < supply["stock_minimo"]:
                raise HTTPException(422, {"code": "validation_error", "message": "stock_maximo_less_than_minimo"})
            if "fecha_vencimiento" in body:
                supply["fecha_vencimiento"] = _optional_text(body, "fecha_vencimiento")
            if "enable_email_alerts" in body:
                supply["enable_email_alerts"] = bool(body.get("enable_email_alerts"))
            if "alert_emails" in body:
                supply["alert_emails"] = list(body.get("alert_emails", [])) if isinstance(body.get("alert_emails", []), list) else []
            if "estado" in body:
                new_state = _state(body)
                if new_state == "inactivo" and _recipe_uses_supply(id):
                    raise HTTPException(422, {"code": "state_conflict", "message": "supply_used_by_active_recipe"})
                supply["estado"] = new_state
            _timestamps(supply)
            _audit(request, user["id"], "supply_updated", "supplies", id, "HITO-002")
            return ok(supply)


        @app.patch("/api/v1/supplies/{id}/toggle-status")
        def toggle_supply_status(id: int, request: Request, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "supplies.toggle-status")
            supply = _get(SUPPLIES, id, "supply")
            new_state = "inactivo" if supply["estado"] == "activo" else "activo"
            if new_state == "inactivo" and _recipe_uses_supply(id):
                raise HTTPException(422, {"code": "state_conflict", "message": "supply_used_by_active_recipe"})
            supply["estado"] = new_state
            _timestamps(supply)
            _audit(request, user["id"], "supply_status_toggled", "supplies", id, supply["estado"])
            return ok(supply)


        @app.get("/api/v1/presentation-types")
        def list_presentation_types(estado: str | None = None, nombre: str | None = None, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "recipes.read")
            return ok(_filtered(list(PRESENTATION_TYPES.values()), estado, nombre))


        @app.post("/api/v1/presentation-types")
        def create_presentation_type(request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "recipes.update")
            name = _required_text(body, "nombre")
            _ensure_unique(PRESENTATION_TYPES, "nombre", name)
            presentation_id = _next_master_id("presentation")
            presentation = _timestamps(
                {
                    "id": presentation_id,
                    "nombre": name,
                    "volumen": _positive(body.get("volumen"), "volumen"),
                    "unidad": _required_text(body, "unidad"),
                    "costo_presentacion": _non_negative(body.get("costo_presentacion", 0), "costo_presentacion"),
                    "estado": _state(body),
                },
                creating=True,
            )
            PRESENTATION_TYPES[presentation_id] = presentation
            _audit(request, user["id"], "presentation_type_created", "presentation_types", presentation_id, "HITO-002")
            return ok(presentation)


        @app.put("/api/v1/presentation-types/{id}")
        def update_presentation_type(id: int, request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "recipes.update")
            presentation = _get(PRESENTATION_TYPES, id, "presentation_type")
            if "nombre" in body:
                name = _required_text(body, "nombre")
                _ensure_unique(PRESENTATION_TYPES, "nombre", name, current_id=id)
                presentation["nombre"] = name
            if "volumen" in body:
                presentation["volumen"] = _positive(body.get("volumen"), "volumen")
            if "unidad" in body:
                presentation["unidad"] = _required_text(body, "unidad")
            if "costo_presentacion" in body:
                presentation["costo_presentacion"] = _non_negative(body.get("costo_presentacion"), "costo_presentacion")
            if "estado" in body:
                presentation["estado"] = _state(body)
            _timestamps(presentation)
            _audit(request, user["id"], "presentation_type_updated", "presentation_types", id, "HITO-002")
            return ok(presentation)


        @app.get("/api/v1/recipes")
        def list_recipes(estado: str | None = None, nombre: str | None = None, tipo: str | None = None, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "recipes.read")
            result = _filtered(list(RECIPES.values()), estado, nombre)
            if tipo:
                result = [item for item in result if item.get("tipo") == tipo]
            return ok(result)


        @app.post("/api/v1/recipes")
        def create_recipe(request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "recipes.create")
            name = _required_text(body, "nombre")
            _ensure_unique(RECIPES, "nombre", name)
            ingredients = _ingredient_payload(body.get("ingredientes"))
            recipe_id = _next_master_id("recipe")
            recipe = _timestamps(
                {
                    "id": recipe_id,
                    "nombre": name,
                    "descripcion": _optional_text(body, "descripcion"),
                    "tipo": _required_text(body, "tipo"),
                    "abv_estimado": _non_negative(body.get("abv_estimado", 0), "abv_estimado"),
                    "volumen_por_lote": _positive(body.get("volumen_por_lote"), "volumen_por_lote"),
                    "pasos_elaboracion": _optional_text(body, "pasos_elaboracion"),
                    "ingredientes": ingredients,
                    "costo_estimado": _recipe_cost(ingredients),
                    "estado": _state(body, RECIPE_STATES),
                },
                creating=True,
            )
            RECIPES[recipe_id] = recipe
            _audit(request, user["id"], "recipe_created", "recipes", recipe_id, "HITO-002")
            return ok(recipe)


        @app.get("/api/v1/recipes/{id}")
        def get_recipe(id: int, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "recipes.read")
            return ok(_get(RECIPES, id, "recipe"))


        @app.put("/api/v1/recipes/{id}")
        def update_recipe(id: int, request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "recipes.update")
            recipe = _get(RECIPES, id, "recipe")
            if "nombre" in body:
                name = _required_text(body, "nombre")
                _ensure_unique(RECIPES, "nombre", name, current_id=id)
                recipe["nombre"] = name
            for field in ["descripcion", "pasos_elaboracion"]:
                if field in body:
                    recipe[field] = _optional_text(body, field)
            if "tipo" in body:
                recipe["tipo"] = _required_text(body, "tipo")
            if "abv_estimado" in body:
                recipe["abv_estimado"] = _non_negative(body.get("abv_estimado"), "abv_estimado")
            if "volumen_por_lote" in body:
                recipe["volumen_por_lote"] = _positive(body.get("volumen_por_lote"), "volumen_por_lote")
            if "ingredientes" in body:
                ingredients = _ingredient_payload(body.get("ingredientes"))
                recipe["ingredientes"] = ingredients
                recipe["costo_estimado"] = _recipe_cost(ingredients)
            if "estado" in body:
                recipe["estado"] = _state(body, RECIPE_STATES)
            _timestamps(recipe)
            _audit(request, user["id"], "recipe_updated", "recipes", id, "HITO-002")
            return ok(recipe)


        @app.post("/api/v1/recipes/{id}/clone")
        def clone_recipe(id: int, request: Request, body: dict[str, Any] = Body(default={}), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "recipes.clone")
            source = _get(RECIPES, id, "recipe")
            if source.get("estado") not in {"activo", "en_prueba"}:
                raise HTTPException(422, {"code": "state_conflict", "message": "recipe_not_cloneable"})
            clone_name = str(body.get("nombre") or f"{source['nombre']} copia").strip()
            _ensure_unique(RECIPES, "nombre", clone_name)
            clone_id = _next_master_id("recipe")
            clone = {
                **source,
                "id": clone_id,
                "nombre": clone_name,
                "estado": "en_prueba",
                "ingredientes": [dict(item) for item in source.get("ingredientes", [])],
                "created_at": _iso(),
                "updated_at": _iso(),
            }
            RECIPES[clone_id] = clone
            _audit(request, user["id"], "recipe_cloned", "recipes", clone_id, f"source={id}")
            return ok(clone)
        """
    ).strip()
    return hito1 + "\n\n" + hito2


def _hito3_backend_main() -> str:
    hito2 = _hito2_backend_main().replace('"milestone": "HITO-002"', '"milestone": "HITO-003"')
    hito2 = hito2.replace(
        '"alert_emails": list(body.get("alert_emails", [])) if isinstance(body.get("alert_emails", []), list) else [],',
        '"alert_emails": _valid_email_list(body.get("alert_emails", [])),',
    )
    hito2 = hito2.replace(
        'supply["alert_emails"] = list(body.get("alert_emails", [])) if isinstance(body.get("alert_emails", []), list) else []',
        'supply["alert_emails"] = _valid_email_list(body.get("alert_emails", []))',
    )
    hito2 = hito2.replace(
        'SUPPLIES[supply_id] = supply\n    _audit(request, user["id"], "supply_created", "supplies", supply_id, "HITO-002")',
        '_ensure_supply_alert_config(supply)\n    SUPPLIES[supply_id] = supply\n    _audit(request, user["id"], "supply_created", "supplies", supply_id, "HITO-003")',
    )
    hito2 = hito2.replace(
        '    _timestamps(supply)\n    _audit(request, user["id"], "supply_updated", "supplies", id, "HITO-002")',
        '    _ensure_supply_alert_config(supply)\n    _timestamps(supply)\n    _audit(request, user["id"], "supply_updated", "supplies", id, "HITO-003")',
    )
    low_stock_route = dedent(
        """


        @app.get("/api/v1/supplies/low-stock")
        def list_low_stock_supplies(user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "supplies.read")
            return ok(_low_stock_payload())
        """
    ).strip()
    hito2 = hito2.replace('@app.get("/api/v1/supplies/{id}")', low_stock_route + "\n\n\n@app.get(\"/api/v1/supplies/{id}\")")
    hito3 = dedent(
        """


        # HITO-003 inventario: entradas de insumos, Kardex, alertas locales y SMTP sanitizado.
        ROLES["compras"]["permissions"] = sorted(set(ROLES["compras"]["permissions"]) | {"supply-entries.create"})
        ROLES["inventario"] = {
            "id": 6,
            "nombre": "inventario",
            "estado": "activo",
            "permissions": ["supplies.read", "supply-entries.create"],
        }

        SUPPLY_ENTRIES: dict[int, dict[str, Any]] = {}
        SUPPLY_MOVEMENTS: dict[int, dict[str, Any]] = {}
        NOTIFICATION_QUEUE: dict[int, dict[str, Any]] = {}
        SMTP_CONFIG: dict[str, Any] | None = None
        NEXT_INVENTORY_ID = {"entry": 1, "movement": 1, "notification": 1}
        MAX_EMAIL_ATTEMPTS = 5
        MIN_ALERT_INTERVAL_HOURS = 24


        def _next_inventory_id(kind: str) -> int:
            value = NEXT_INVENTORY_ID[kind]
            NEXT_INVENTORY_ID[kind] += 1
            return value


        def _ensure_any_permission(user: dict[str, Any], permissions: set[str]) -> None:
            granted = _permissions_for(user)
            if "*" in granted or granted.intersection(permissions):
                return
            raise HTTPException(403, {"code": "permission_denied", "message": "permission_required"})


        def _valid_email_list(raw_value: Any) -> list[str]:
            values = raw_value
            if isinstance(values, str):
                values = [item.strip() for item in values.split(",")]
            if not isinstance(values, list):
                raise HTTPException(422, {"code": "validation_error", "message": "alert_emails_invalid"})
            result: list[str] = []
            for item in values:
                email = _optional_email(str(item or ""))
                if email and email not in result:
                    result.append(email)
            return result


        def _ensure_supply_alert_config(supply: dict[str, Any]) -> None:
            if bool(supply.get("enable_email_alerts")) and not supply.get("alert_emails"):
                raise HTTPException(422, {"code": "validation_error", "message": "alert_emails_required"})


        def _hours_since(value: str | None) -> float | None:
            if not value:
                return None
            try:
                alert_time = datetime.fromisoformat(value)
            except ValueError:
                return None
            if alert_time.tzinfo is None:
                alert_time = alert_time.replace(tzinfo=timezone.utc)
            return (_now() - alert_time).total_seconds() / 3600


        def _should_send_stock_alert(supply: dict[str, Any]) -> bool:
            current_stock = float(supply.get("stock_actual", 0))
            minimum_stock = float(supply.get("stock_minimo", 0))
            if current_stock <= 0:
                return True
            if current_stock >= minimum_stock:
                return False
            hours = _hours_since(supply.get("last_alert_sent_at"))
            return hours is None or hours >= MIN_ALERT_INTERVAL_HOURS


        def _enqueue_stock_alert(supply: dict[str, Any], reason: str) -> dict[str, Any]:
            _ensure_supply_alert_config(supply)
            notification_id = _next_inventory_id("notification")
            notification = {
                "id": notification_id,
                "supply_id": supply["id"],
                "recipients": list(supply.get("alert_emails", [])),
                "subject": f"Stock bajo: {supply['nombre']}",
                "body_html": f"<p>{supply['nombre']} tiene stock {supply['stock_actual']} bajo minimo {supply['stock_minimo']}.</p>",
                "status": "queued",
                "attempts": 0,
                "sent_at": None,
                "error_message": "",
                "final_error": False,
                "reason": reason,
                "created_at": _iso(),
                "updated_at": _iso(),
            }
            NOTIFICATION_QUEUE[notification_id] = notification
            supply["last_alert_sent_at"] = _iso()
            return notification


        def _evaluate_stock_alert(supply: dict[str, Any]) -> dict[str, Any]:
            current_stock = float(supply.get("stock_actual", 0))
            minimum_stock = float(supply.get("stock_minimo", 0))
            if current_stock >= minimum_stock:
                supply["last_alert_sent_at"] = None
                return {"queued": False, "reason": "stock_recovered"}
            if not bool(supply.get("enable_email_alerts", False)):
                return {"queued": False, "reason": "alerts_disabled"}
            if not _should_send_stock_alert(supply):
                return {"queued": False, "reason": "interval_not_elapsed"}
            notification = _enqueue_stock_alert(supply, "zero_stock" if current_stock <= 0 else "low_stock")
            return {"queued": True, "notification_id": notification["id"]}


        def _low_stock_payload() -> list[dict[str, Any]]:
            return [
                item
                for item in SUPPLIES.values()
                if item.get("estado") == "activo" and float(item.get("stock_actual", 0)) < float(item.get("stock_minimo", 0))
            ]


        def _safe_notification(notification: dict[str, Any]) -> dict[str, Any]:
            return {
                "id": notification["id"],
                "supply_id": notification.get("supply_id"),
                "recipients": list(notification.get("recipients", [])),
                "subject": notification.get("subject", ""),
                "status": notification.get("status", "queued"),
                "attempts": notification.get("attempts", 0),
                "sent_at": notification.get("sent_at"),
                "error_message": notification.get("error_message", ""),
                "final_error": bool(notification.get("final_error", False)),
                "reason": notification.get("reason", ""),
                "transport": notification.get("transport", "local_queue"),
                "created_at": notification.get("created_at"),
                "updated_at": notification.get("updated_at"),
            }


        def _encrypted_marker(raw_secret: str, username: str) -> str:
            if not raw_secret:
                raise HTTPException(422, {"code": "validation_error", "message": "smtp_secret_required"})
            digest = hashlib.sha256(f"{username}:{raw_secret}".encode("utf-8")).hexdigest()
            return f"local-encrypted:{digest}"


        def _smtp_public(config: dict[str, Any] | None) -> dict[str, Any]:
            if not config:
                return {"configured": False}
            return {
                "configured": True,
                "host": config["host"],
                "port": config["port"],
                "username": config["username"],
                "from_email": config["from_email"],
                "use_tls": config["use_tls"],
                "updated_by": config["updated_by"],
                "updated_at": config["updated_at"],
                "secret_configured": bool(config.get("password_encrypted")),
            }


        def _require_admin_settings(user: dict[str, Any] = Depends(_current_user)) -> dict[str, Any]:
            _ensure_permission(user, "admin.settings")
            return user


        @app.post("/api/v1/supply-entries")
        def create_supply_entry(request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "supply-entries.create")
            supply_id = int(body.get("supply_id", 0))
            supply = _active_supply(supply_id)
            quantity = _positive(body.get("cantidad"), "cantidad")
            unit_cost = _non_negative(body.get("costo_unitario", supply.get("costo_unitario", 0)), "costo_unitario")
            supplier_id = int(body.get("proveedor_id") or supply.get("proveedor_id") or 0)
            if supplier_id:
                _active_supplier(supplier_id)
            previous_stock = float(supply.get("stock_actual", 0))
            resulting_stock = round(previous_stock + quantity, 4)
            supply["stock_actual"] = resulting_stock
            supply["costo_unitario"] = unit_cost
            supply["updated_at"] = _iso()

            entry_id = _next_inventory_id("entry")
            entry = {
                "id": entry_id,
                "supply_id": supply_id,
                "cantidad": quantity,
                "costo_unitario": unit_cost,
                "proveedor_id": supplier_id,
                "referencia": _optional_text(body, "referencia"),
                "created_by": user["id"],
                "created_at": _iso(),
            }
            movement_id = _next_inventory_id("movement")
            movement = {
                "id": movement_id,
                "supply_id": supply_id,
                "tipo_movimiento": "ENTRADA",
                "cantidad": quantity,
                "costo_unitario": unit_cost,
                "saldo_resultante": resulting_stock,
                "referencia": entry["referencia"],
                "user_id": user["id"],
                "created_at": entry["created_at"],
            }
            SUPPLY_ENTRIES[entry_id] = entry
            SUPPLY_MOVEMENTS[movement_id] = movement
            alert_result = _evaluate_stock_alert(supply)
            _audit(request, user["id"], "supply_entry_created", "supply_entries", entry_id, f"supply={supply_id}")
            return ok({"entry": entry, "movement": movement, "stock_actual": resulting_stock, "alert": alert_result})


        @app.get("/api/v1/supply-entries")
        def list_supply_entries(supply_id: int | None = None, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "supplies.read")
            entries = list(SUPPLY_ENTRIES.values())
            if supply_id is not None:
                entries = [item for item in entries if item["supply_id"] == supply_id]
            return ok(entries)


        @app.get("/api/v1/supplies/{id}/kardex")
        def get_supply_kardex(id: int, tipo: str | None = None, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "supplies.read")
            _get(SUPPLIES, id, "supply")
            movements = [item for item in SUPPLY_MOVEMENTS.values() if item["supply_id"] == id]
            if tipo:
                movements = [item for item in movements if item["tipo_movimiento"] == tipo]
            return ok(sorted(movements, key=lambda item: item["created_at"]))


        @app.get("/api/v1/settings/smtp")
        def get_smtp_config(_: dict[str, Any] = Depends(_require_admin_settings)):
            return ok(_smtp_public(SMTP_CONFIG))


        @app.put("/api/v1/settings/smtp")
        def update_smtp_config(request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_require_admin_settings)):
            global SMTP_CONFIG
            host = _required_text(body, "host", "server")
            port = int(_positive(body.get("port"), "port"))
            if port > 65535:
                raise HTTPException(422, {"code": "validation_error", "message": "smtp_port_invalid"})
            username = _required_text(body, "username")
            raw_secret = str(body.get("password", body.get("secret", "")) or "")
            from_email = _optional_email(_required_text(body, "from_email"))
            encrypted = SMTP_CONFIG.get("password_encrypted") if SMTP_CONFIG and not raw_secret else _encrypted_marker(raw_secret, username)
            SMTP_CONFIG = {
                "id": 1,
                "host": host,
                "port": port,
                "username": username,
                "password_encrypted": encrypted,
                "from_email": from_email,
                "use_tls": bool(body.get("use_tls", True)),
                "updated_by": user["id"],
                "updated_at": _iso(),
            }
            _audit(request, user["id"], "smtp_config_updated", "smtp_config", 1, "HITO-003")
            return ok(_smtp_public(SMTP_CONFIG))


        @app.post("/api/v1/settings/smtp/test")
        def test_smtp_config(request: Request, body: dict[str, Any] = Body(default={}), user: dict[str, Any] = Depends(_require_admin_settings)):
            if not SMTP_CONFIG:
                raise HTTPException(422, {"code": "validation_error", "message": "smtp_not_configured"})
            recipients = _valid_email_list(body.get("recipients", body.get("recipient", [SMTP_CONFIG["from_email"]])))
            notification_id = _next_inventory_id("notification")
            notification = {
                "id": notification_id,
                "supply_id": None,
                "recipients": recipients,
                "subject": "Prueba SMTP BrewMaster",
                "body_html": "<p>Prueba local SMTP BrewMaster.</p>",
                "status": "sent",
                "attempts": 1,
                "sent_at": _iso(),
                "error_message": "",
                "final_error": False,
                "reason": "smtp_test",
                "transport": "mock_local",
                "created_at": _iso(),
                "updated_at": _iso(),
            }
            NOTIFICATION_QUEUE[notification_id] = notification
            _audit(request, user["id"], "smtp_test_queued_locally", "notification_queue", notification_id, "mock_local")
            return ok({"delivered": False, "mocked": True, "notification": _safe_notification(notification)})


        @app.get("/api/v1/notifications")
        def list_notifications(status: str | None = None, user: dict[str, Any] = Depends(_current_user)):
            _ensure_any_permission(user, {"admin.settings", "supplies.read"})
            notifications = [_safe_notification(item) for item in NOTIFICATION_QUEUE.values()]
            if status:
                notifications = [item for item in notifications if item["status"] == status]
            return ok(notifications)
        """
    ).strip()
    return hito2 + "\n\n" + hito3


def _hito4_backend_main() -> str:
    hito3 = _hito3_backend_main().replace('"milestone": "HITO-003"', '"milestone": "HITO-004"')
    hito3 = hito3.replace(
        '    recipe = _get(RECIPES, id, "recipe")\n    if "nombre" in body:',
        '    recipe = _get(RECIPES, id, "recipe")\n    if _recipe_has_active_batches(id):\n        raise HTTPException(422, {"code": "state_conflict", "message": "recipe_has_active_batches"})\n    if "nombre" in body:',
    )
    hito4 = dedent(
        """


        # HITO-004 produccion: lotes, calidad, mermas e inventario de productos terminados.
        ROLES["produccion"]["permissions"] = sorted(
            set(ROLES["produccion"]["permissions"])
            | {
                "batches.read",
                "batches.create",
                "batches.complete",
                "batches.cancel",
                "batches.quality-check",
                "waste.create",
                "waste.read",
                "products.read",
            }
        )
        ROLES["productos"] = {
            "id": 7,
            "nombre": "productos",
            "estado": "activo",
            "permissions": ["products.read", "products.update-price"],
        }

        BATCH_STATES = {"en_elaboracion", "completado", "cancelado"}
        QUALITY_RESULTS = {"aprobado", "rechazado"}
        WASTE_TYPES = {"proceso", "calidad", "vencimiento", "rotura", "ajuste", "otro"}
        PRODUCTION_BATCHES: dict[int, dict[str, Any]] = {}
        BATCH_QUALITY_CHECKS: dict[int, dict[str, Any]] = {}
        WASTE_RECORDS: dict[int, dict[str, Any]] = {}
        FINISHED_PRODUCTS: dict[int, dict[str, Any]] = {}
        PRODUCT_MOVEMENTS: dict[int, dict[str, Any]] = {}
        BATCH_SUPPLY_SNAPSHOTS: dict[int, dict[str, Any]] = {}
        NEXT_PRODUCTION_ID = {
            "batch": 1,
            "quality": 1,
            "waste": 1,
            "product": 1,
            "product_movement": 1,
            "snapshot": 1,
        }


        def _next_production_id(kind: str) -> int:
            value = NEXT_PRODUCTION_ID[kind]
            NEXT_PRODUCTION_ID[kind] += 1
            return value


        def _recipe_has_active_batches(recipe_id: int) -> bool:
            return any(
                batch.get("recipe_id") == recipe_id and batch.get("estado") == "en_elaboracion"
                for batch in PRODUCTION_BATCHES.values()
            )


        def _active_recipe(recipe_id: int) -> dict[str, Any]:
            recipe = _get(RECIPES, recipe_id, "recipe")
            if recipe.get("estado") != "activo":
                raise HTTPException(422, {"code": "inactive_entity", "message": "recipe_inactive"})
            return recipe


        def _active_presentation(presentation_id: int) -> dict[str, Any]:
            presentation = _get(PRESENTATION_TYPES, presentation_id, "presentation_type")
            if presentation.get("estado") != "activo":
                raise HTTPException(422, {"code": "inactive_entity", "message": "presentation_type_inactive"})
            return presentation


        def _batch_or_404(batch_id: int) -> dict[str, Any]:
            return _get(PRODUCTION_BATCHES, batch_id, "batch")


        def _product_or_404(product_id: int) -> dict[str, Any]:
            return _get(FINISHED_PRODUCTS, product_id, "product")


        def _batch_supply_requirements(recipe: dict[str, Any], produced_liters: float) -> list[dict[str, Any]]:
            recipe_volume = _positive(recipe.get("volumen_por_lote"), "recipe_volume")
            ratio = produced_liters / recipe_volume
            requirements: list[dict[str, Any]] = []
            for ingredient in recipe.get("ingredientes", []):
                supply = _active_supply(int(ingredient["supply_id"]))
                quantity = round(float(ingredient["cantidad"]) * ratio, 4)
                requirements.append(
                    {
                        "supply_id": supply["id"],
                        "nombre_insumo": supply["nombre"],
                        "cantidad_usada": quantity,
                        "costo_unitario": float(supply.get("costo_unitario", 0)),
                        "stock_actual": float(supply.get("stock_actual", 0)),
                    }
                )
            return requirements


        def _stock_warnings(requirements: list[dict[str, Any]]) -> list[dict[str, Any]]:
            return [
                {
                    "supply_id": item["supply_id"],
                    "required": item["cantidad_usada"],
                    "available": item["stock_actual"],
                }
                for item in requirements
                if item["cantidad_usada"] > item["stock_actual"]
            ]


        def _produced_units(produced_liters: float, presentation: dict[str, Any], body: dict[str, Any]) -> int:
            if body.get("unidades_producidas") not in {None, ""}:
                return int(_positive(body.get("unidades_producidas"), "unidades_producidas"))
            volume = _positive(presentation.get("volumen"), "presentation_volume")
            unit = str(presentation.get("unidad", "ml")).lower()
            if unit in {"ml", "mililitros"}:
                return max(1, int(round(produced_liters * 1000 / volume)))
            return max(1, int(round(produced_liters / volume)))


        def _find_finished_product(recipe_id: int, presentation_id: int) -> dict[str, Any] | None:
            for product in FINISHED_PRODUCTS.values():
                if product["recipe_id"] == recipe_id and product["presentation_type_id"] == presentation_id:
                    return product
            return None


        def _product_public(product: dict[str, Any]) -> dict[str, Any]:
            return dict(product)


        def _record_supply_output(requirement: dict[str, Any], batch_id: int, user_id: int) -> dict[str, Any]:
            supply = _active_supply(int(requirement["supply_id"]))
            resulting_stock = round(float(supply.get("stock_actual", 0)) - float(requirement["cantidad_usada"]), 4)
            supply["stock_actual"] = resulting_stock
            supply["updated_at"] = _iso()
            movement_id = _next_inventory_id("movement")
            movement = {
                "id": movement_id,
                "supply_id": supply["id"],
                "tipo_movimiento": "SALIDA_PRODUCCION",
                "cantidad": requirement["cantidad_usada"],
                "costo_unitario": requirement["costo_unitario"],
                "saldo_resultante": resulting_stock,
                "referencia": f"batch:{batch_id}",
                "user_id": user_id,
                "created_at": _iso(),
            }
            SUPPLY_MOVEMENTS[movement_id] = movement
            snapshot_id = _next_production_id("snapshot")
            snapshot = {
                "id": snapshot_id,
                "batch_id": batch_id,
                "supply_id": supply["id"],
                "cantidad_usada": requirement["cantidad_usada"],
                "costo_unitario_momento": requirement["costo_unitario"],
                "nombre_insumo": requirement["nombre_insumo"],
                "created_at": _iso(),
            }
            BATCH_SUPPLY_SNAPSHOTS[snapshot_id] = snapshot
            return snapshot


        def _record_product_movement(product: dict[str, Any], movement_type: str, quantity: float, unit_cost: float, reference: str, user_id: int) -> dict[str, Any]:
            movement_id = _next_production_id("product_movement")
            movement = {
                "id": movement_id,
                "product_id": product["id"],
                "tipo_movimiento": movement_type,
                "cantidad": quantity,
                "costo_unitario": unit_cost,
                "saldo_resultante": product["cantidad_stock"],
                "referencia": reference,
                "user_id": user_id,
                "created_at": _iso(),
            }
            PRODUCT_MOVEMENTS[movement_id] = movement
            return movement


        @app.get("/api/v1/batches")
        def list_batches(recipe_id: int | None = None, estado: str | None = None, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "batches.read")
            batches = list(PRODUCTION_BATCHES.values())
            if recipe_id is not None:
                batches = [item for item in batches if item["recipe_id"] == recipe_id]
            if estado:
                batches = [item for item in batches if item["estado"] == estado]
            return ok(batches)


        @app.post("/api/v1/batches")
        def create_batch(request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "batches.create")
            recipe_id = int(body.get("recipe_id", 0))
            presentation_id = int(body.get("presentation_type_id", 0))
            recipe = _active_recipe(recipe_id)
            presentation = _active_presentation(presentation_id)
            produced_liters = _positive(body.get("cantidad_producida", body.get("cantidad_a_producir")), "cantidad_producida")
            production_date = _required_text(body, "fecha_produccion", "fecha")
            responsible_id = int(body.get("responsable_id") or user["id"])
            if responsible_id not in USERS:
                raise HTTPException(422, {"code": "validation_error", "message": "responsable_required"})
            batch_number = _required_text(body, "numero_lote") if body.get("numero_lote") else f"LOT-{_next_production_id('batch'):04d}"
            _ensure_unique(PRODUCTION_BATCHES, "numero_lote", batch_number)
            requirements = _batch_supply_requirements(recipe, produced_liters)
            batch_id = int(batch_number.removeprefix("LOT-")) if batch_number.startswith("LOT-") and batch_number.removeprefix("LOT-").isdigit() else _next_production_id("batch")
            while batch_id in PRODUCTION_BATCHES:
                batch_id = _next_production_id("batch")
            batch = _timestamps(
                {
                    "id": batch_id,
                    "numero_lote": batch_number,
                    "recipe_id": recipe_id,
                    "recipe_name": recipe["nombre"],
                    "presentation_type_id": presentation_id,
                    "presentation_name": presentation["nombre"],
                    "cantidad_producida": produced_liters,
                    "fecha_produccion": production_date,
                    "responsable_id": responsible_id,
                    "estado": "en_elaboracion",
                    "horas_mano_obra": _non_negative(body.get("horas_mano_obra", 0), "horas_mano_obra"),
                    "kwh_consumidos": _non_negative(body.get("kwh_consumidos", 0), "kwh_consumidos"),
                    "litros_agua": _non_negative(body.get("litros_agua", 0), "litros_agua"),
                    "porcentaje_merma": _non_negative(body.get("porcentaje_merma", 0), "porcentaje_merma"),
                    "costo_indirecto": _non_negative(body.get("costo_indirecto", 0), "costo_indirecto"),
                    "observaciones": _optional_text(body, "observaciones"),
                    "stock_alerts": _stock_warnings(requirements),
                    "requirements": requirements,
                    "costo_total": 0,
                    "costo_por_litro": 0,
                    "costo_por_unidad": 0,
                },
                creating=True,
            )
            if batch["porcentaje_merma"] > 100:
                raise HTTPException(422, {"code": "validation_error", "message": "porcentaje_merma_invalid"})
            PRODUCTION_BATCHES[batch_id] = batch
            _audit(request, user["id"], "batch_created", "production_batches", batch_id, "HITO-004")
            return ok(batch)


        @app.get("/api/v1/batches/{id}")
        def get_batch(id: int, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "batches.read")
            batch = _batch_or_404(id)
            snapshots = [item for item in BATCH_SUPPLY_SNAPSHOTS.values() if item["batch_id"] == id]
            quality = next((item for item in BATCH_QUALITY_CHECKS.values() if item["batch_id"] == id), None)
            return ok({**batch, "snapshots": snapshots, "quality_check": quality})


        @app.put("/api/v1/batches/{id}")
        def update_batch(id: int, request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "batches.create")
            batch = _batch_or_404(id)
            if batch["estado"] != "en_elaboracion":
                raise HTTPException(422, {"code": "state_conflict", "message": "batch_not_editable"})
            for field in ["fecha_produccion", "observaciones"]:
                if field in body:
                    batch[field] = _optional_text(body, field)
            for field in ["cantidad_producida", "horas_mano_obra", "kwh_consumidos", "litros_agua", "porcentaje_merma", "costo_indirecto"]:
                if field in body:
                    batch[field] = _positive(body.get(field), field) if field == "cantidad_producida" else _non_negative(body.get(field), field)
            if batch["porcentaje_merma"] > 100:
                raise HTTPException(422, {"code": "validation_error", "message": "porcentaje_merma_invalid"})
            recipe = _active_recipe(int(batch["recipe_id"]))
            batch["requirements"] = _batch_supply_requirements(recipe, float(batch["cantidad_producida"]))
            batch["stock_alerts"] = _stock_warnings(batch["requirements"])
            _timestamps(batch)
            _audit(request, user["id"], "batch_updated", "production_batches", id, "HITO-004")
            return ok(batch)


        @app.post("/api/v1/batches/{id}/complete")
        def complete_batch_route(id: int, request: Request, body: dict[str, Any] = Body(default={}), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "batches.complete")
            batch = _batch_or_404(id)
            if batch["estado"] == "cancelado":
                raise HTTPException(422, {"code": "state_conflict", "message": "batch_cancelled"})
            if batch["estado"] == "completado":
                raise HTTPException(422, {"code": "state_conflict", "message": "batch_already_completed"})
            recipe = _active_recipe(int(batch["recipe_id"]))
            presentation = _active_presentation(int(batch["presentation_type_id"]))
            produced_liters = _positive(body.get("cantidad_producida", batch["cantidad_producida"]), "cantidad_producida")
            requirements = _batch_supply_requirements(recipe, produced_liters)
            stock_warnings = _stock_warnings(requirements)
            if stock_warnings:
                raise HTTPException(422, {"code": "stock_unavailable", "message": "insufficient_supply_stock", "details": stock_warnings})
            labor_hours = _non_negative(body.get("horas_mano_obra", batch.get("horas_mano_obra", 0)), "horas_mano_obra")
            labor_rate = _non_negative(body.get("tarifa_mano_obra", 0), "tarifa_mano_obra")
            energy_kwh = _non_negative(body.get("kwh_consumidos", batch.get("kwh_consumidos", 0)), "kwh_consumidos")
            energy_rate = _non_negative(body.get("tarifa_kwh", 0), "tarifa_kwh")
            water_liters = _non_negative(body.get("litros_agua", batch.get("litros_agua", 0)), "litros_agua")
            water_rate = _non_negative(body.get("tarifa_litro_agua", 0), "tarifa_litro_agua")
            waste_pct = _non_negative(body.get("porcentaje_merma", batch.get("porcentaje_merma", 0)), "porcentaje_merma")
            if waste_pct > 100:
                raise HTTPException(422, {"code": "validation_error", "message": "porcentaje_merma_invalid"})
            indirect_cost = _non_negative(body.get("costo_indirecto", batch.get("costo_indirecto", 0)), "costo_indirecto")
            units = _produced_units(produced_liters, presentation, body)
            supplies_cost = round(sum(item["cantidad_usada"] * item["costo_unitario"] for item in requirements), 4)
            waste_cost = round(supplies_cost * waste_pct / 100, 4)
            presentation_cost = _non_negative(presentation.get("costo_presentacion", 0), "costo_presentacion") * units
            total_cost = round(
                supplies_cost
                + labor_hours * labor_rate
                + energy_kwh * energy_rate
                + water_liters * water_rate
                + waste_cost
                + indirect_cost
                + presentation_cost,
                4,
            )
            if total_cost < 0:
                raise HTTPException(422, {"code": "validation_error", "message": "costo_total_invalid"})
            snapshots = [_record_supply_output(item, id, user["id"]) for item in requirements]
            product = _find_finished_product(recipe["id"], presentation["id"])
            if product is None:
                product_id = _next_production_id("product")
                product = _timestamps(
                    {
                        "id": product_id,
                        "recipe_id": recipe["id"],
                        "recipe_name": recipe["nombre"],
                        "presentation_type_id": presentation["id"],
                        "presentation_name": presentation["nombre"],
                        "cantidad_stock": 0,
                        "costo_unitario": 0,
                        "precio_venta": 0,
                        "fecha_vencimiento_aprox": _optional_text(body, "fecha_vencimiento_aprox"),
                        "estado": "activo",
                    },
                    creating=True,
                )
                FINISHED_PRODUCTS[product_id] = product
            previous_stock = float(product.get("cantidad_stock", 0))
            new_stock = round(previous_stock + units, 4)
            weighted_cost = total_cost / units
            if previous_stock > 0:
                weighted_cost = ((previous_stock * float(product["costo_unitario"])) + total_cost) / new_stock
            product["cantidad_stock"] = new_stock
            product["costo_unitario"] = round(weighted_cost, 4)
            product["precio_venta"] = max(float(product.get("precio_venta", 0)), product["costo_unitario"])
            product["updated_at"] = _iso()
            product_movement = _record_product_movement(product, "ENTRADA_PRODUCCION", units, product["costo_unitario"], f"batch:{id}", user["id"])
            batch.update(
                {
                    "estado": "completado",
                    "cantidad_producida": produced_liters,
                    "unidades_producidas": units,
                    "horas_mano_obra": labor_hours,
                    "kwh_consumidos": energy_kwh,
                    "litros_agua": water_liters,
                    "porcentaje_merma": waste_pct,
                    "costo_insumos": supplies_cost,
                    "costo_merma": waste_cost,
                    "costo_total": total_cost,
                    "costo_por_litro": round(total_cost / produced_liters, 4),
                    "costo_por_unidad": round(total_cost / units, 4),
                    "product_id": product["id"],
                    "completed_at": _iso(),
                    "updated_at": _iso(),
                }
            )
            _audit(request, user["id"], "batch_completed", "production_batches", id, f"product={product['id']}")
            return ok({"batch": batch, "snapshots": snapshots, "product": product, "product_movement": product_movement})


        @app.post("/api/v1/batches/{id}/cancel")
        def cancel_batch(id: int, request: Request, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "batches.cancel")
            batch = _batch_or_404(id)
            if batch["estado"] != "en_elaboracion":
                raise HTTPException(422, {"code": "state_conflict", "message": "batch_not_cancelable"})
            batch["estado"] = "cancelado"
            batch["updated_at"] = _iso()
            _audit(request, user["id"], "batch_cancelled", "production_batches", id, "no_inventory_effect")
            return ok(batch)


        @app.post("/api/v1/batches/{id}/quality-check")
        def create_quality_check(id: int, request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "batches.quality-check")
            batch = _batch_or_404(id)
            if batch["estado"] != "completado":
                raise HTTPException(422, {"code": "state_conflict", "message": "batch_not_completed"})
            if any(item["batch_id"] == id for item in BATCH_QUALITY_CHECKS.values()):
                raise HTTPException(422, {"code": "state_conflict", "message": "quality_check_already_exists"})
            result = _required_text(body, "resultado")
            if result not in QUALITY_RESULTS:
                raise HTTPException(422, {"code": "validation_error", "message": "quality_result_invalid"})
            rejection_reason = _optional_text(body, "motivo_rechazo")
            if result == "rechazado" and not rejection_reason:
                raise HTTPException(422, {"code": "validation_error", "message": "motivo_rechazo_required"})
            og = _positive(body.get("og", 1), "og")
            fg = _positive(body.get("fg", 0.5), "fg")
            if fg >= og:
                raise HTTPException(422, {"code": "validation_error", "message": "fg_must_be_less_than_og"})
            ph = _non_negative(body.get("ph", 7), "ph")
            if ph > 14:
                raise HTTPException(422, {"code": "validation_error", "message": "ph_invalid"})
            for field in ["nota_aroma", "nota_sabor"]:
                if field in body:
                    note = _non_negative(body.get(field), field)
                    if note < 1 or note > 10:
                        raise HTTPException(422, {"code": "validation_error", "message": f"{field}_invalid"})
            quality_id = _next_production_id("quality")
            quality = _timestamps(
                {
                    "id": quality_id,
                    "batch_id": id,
                    "og": og,
                    "fg": fg,
                    "abv_calculado": _non_negative(body.get("abv_calculado", batch.get("costo_por_litro", 0)), "abv_calculado"),
                    "ph": ph,
                    "temp_fermentacion": _non_negative(body.get("temp_fermentacion", 0), "temp_fermentacion"),
                    "nota_aroma": body.get("nota_aroma"),
                    "nota_sabor": body.get("nota_sabor"),
                    "resultado": result,
                    "motivo_rechazo": rejection_reason,
                    "responsable_id": int(body.get("responsable_id") or user["id"]),
                },
                creating=True,
            )
            BATCH_QUALITY_CHECKS[quality_id] = quality
            batch["resultado_calidad"] = result
            batch["updated_at"] = _iso()
            _audit(request, user["id"], "quality_check_created", "batch_quality_checks", quality_id, f"batch={id}")
            return ok(quality)


        @app.get("/api/v1/products")
        def list_products(estado: str | None = None, recipe_id: int | None = None, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "products.read")
            products = [_product_public(item) for item in FINISHED_PRODUCTS.values()]
            if estado:
                products = [item for item in products if item.get("estado") == estado]
            if recipe_id is not None:
                products = [item for item in products if item.get("recipe_id") == recipe_id]
            return ok(products)


        @put_app_placeholder
        def _unused_placeholder():
            return None
        """
    ).strip()
    hito4 = hito4.replace(
        "@put_app_placeholder\ndef _unused_placeholder():\n    return None",
        dedent(
            """


            @app.put("/api/v1/products/{id}/price")
            def update_product_price(id: int, request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
                _ensure_permission(user, "products.update-price")
                product = _product_or_404(id)
                price = _non_negative(body.get("precio_venta"), "precio_venta")
                product["precio_venta"] = price
                product["updated_at"] = _iso()
                warning = "price_below_cost" if price < float(product.get("costo_unitario", 0)) else ""
                _audit(request, user["id"], "product_price_updated", "finished_products", id, warning or "HITO-004")
                return ok({"product": _product_public(product), "warning": warning})


            @app.get("/api/v1/products/{id}/kardex")
            def get_product_kardex(id: int, tipo: str | None = None, user: dict[str, Any] = Depends(_current_user)):
                _ensure_permission(user, "products.read")
                _product_or_404(id)
                movements = [item for item in PRODUCT_MOVEMENTS.values() if item["product_id"] == id]
                if tipo:
                    movements = [item for item in movements if item["tipo_movimiento"] == tipo]
                return ok(sorted(movements, key=lambda item: item["created_at"]))


            @app.get("/api/v1/waste-records")
            def list_waste_records(tipo_entidad: str | None = None, user: dict[str, Any] = Depends(_current_user)):
                _ensure_permission(user, "waste.read")
                records = list(WASTE_RECORDS.values())
                if tipo_entidad:
                    records = [item for item in records if item["tipo_entidad"] == tipo_entidad]
                return ok(records)


            @app.post("/api/v1/waste-records")
            def create_waste_record(request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
                _ensure_permission(user, "waste.create")
                entity_type = _required_text(body, "tipo_entidad")
                if entity_type not in {"insumo", "producto"}:
                    raise HTTPException(422, {"code": "validation_error", "message": "tipo_entidad_invalid"})
                waste_type = _required_text(body, "tipo_merma")
                if waste_type not in WASTE_TYPES:
                    raise HTTPException(422, {"code": "validation_error", "message": "tipo_merma_invalid"})
                reason = _required_text(body, "motivo_detallado", "motivo")
                quantity = _positive(body.get("cantidad_perdida", body.get("cantidad")), "cantidad_perdida")
                entity_id = int(body.get("entidad_id", body.get("supply_id", body.get("product_id", 0))))
                batch_id = int(body.get("batch_id", 0) or 0)
                unit_cost = body.get("costo_unitario")
                if entity_type == "insumo":
                    supply = _active_supply(entity_id)
                    if quantity > float(supply.get("stock_actual", 0)):
                        raise HTTPException(422, {"code": "stock_unavailable", "message": "waste_exceeds_stock"})
                    cost = _non_negative(unit_cost if unit_cost not in {None, ""} else supply.get("costo_unitario", 0), "costo_unitario")
                    supply["stock_actual"] = round(float(supply.get("stock_actual", 0)) - quantity, 4)
                    supply["updated_at"] = _iso()
                    movement_id = _next_inventory_id("movement")
                    movement = {
                        "id": movement_id,
                        "supply_id": supply["id"],
                        "tipo_movimiento": "MERMA",
                        "cantidad": quantity,
                        "costo_unitario": cost,
                        "saldo_resultante": supply["stock_actual"],
                        "referencia": f"waste:{batch_id or 'manual'}",
                        "user_id": user["id"],
                        "created_at": _iso(),
                    }
                    SUPPLY_MOVEMENTS[movement_id] = movement
                else:
                    product = _product_or_404(entity_id)
                    if quantity > float(product.get("cantidad_stock", 0)):
                        raise HTTPException(422, {"code": "stock_unavailable", "message": "waste_exceeds_stock"})
                    cost = _non_negative(unit_cost if unit_cost not in {None, ""} else product.get("costo_unitario", 0), "costo_unitario")
                    product["cantidad_stock"] = round(float(product.get("cantidad_stock", 0)) - quantity, 4)
                    product["updated_at"] = _iso()
                    movement = _record_product_movement(product, "MERMA", quantity, cost, f"waste:{batch_id or 'manual'}", user["id"])
                waste_id = _next_production_id("waste")
                record = _timestamps(
                    {
                        "id": waste_id,
                        "tipo_entidad": entity_type,
                        "entidad_id": entity_id,
                        "cantidad_perdida": quantity,
                        "costo_unitario": cost,
                        "costo_total": round(quantity * cost, 4),
                        "tipo_merma": waste_type,
                        "motivo_detallado": reason,
                        "responsable_id": int(body.get("responsable_id") or user["id"]),
                        "fecha": _optional_text(body, "fecha", _iso()),
                        "batch_id": batch_id or None,
                        "movement": movement,
                    },
                    creating=True,
                )
                WASTE_RECORDS[waste_id] = record
                _audit(request, user["id"], "waste_record_created", "waste_records", waste_id, f"{entity_type}={entity_id}")
                return ok(record)
            """
        ).strip(),
    )
    return hito3 + "\n\n" + hito4


def _hito5_backend_main() -> str:
    hito4 = _hito4_backend_main().replace('"milestone": "HITO-004"', '"milestone": "HITO-005"')
    commerce_block = dedent(
        """

        # HITO-005 clientes, ventas, reservas y compras.
        ROLES["ventas"] = {
            "id": 7,
            "nombre": "ventas",
            "estado": "activo",
            "permissions": [
                "products.read",
                "sales.read",
                "sales.create",
                "customers.read",
                "customers.create",
                "customers.update",
                "reservations.create",
                "reservations.manage",
            ],
        }
        ROLES["compras"]["permissions"] = sorted(
            set(ROLES["compras"]["permissions"])
            | {
                "purchase-orders.read",
                "purchase-orders.create",
                "purchase-orders.receive",
                "purchase-orders.cancel",
                "suppliers.read",
                "supplies.read",
                "supply-entries.create",
            }
        )

        CUSTOMER_TYPES: dict[str, dict[str, Any]] = {
            "minorista": {"id": 1, "nombre": "minorista", "descripcion": "Cliente directo", "descuento_pct_base": 0},
            "mayorista": {"id": 2, "nombre": "mayorista", "descripcion": "Compra por volumen", "descuento_pct_base": 8},
            "distribuidor": {"id": 3, "nombre": "distribuidor", "descripcion": "Canal distribuidor", "descuento_pct_base": 12},
        }
        CUSTOMERS: dict[int, dict[str, Any]] = {}
        PRODUCT_PRICES: dict[int, dict[str, Any]] = {}
        SALES: dict[int, dict[str, Any]] = {}
        SALE_ITEMS: dict[int, dict[str, Any]] = {}
        STOCK_RESERVATIONS: dict[int, dict[str, Any]] = {}
        PURCHASE_ORDERS: dict[int, dict[str, Any]] = {}
        PURCHASE_ORDER_ITEMS: dict[int, dict[str, Any]] = {}
        NEXT_COMMERCIAL_ID = {
            "customer": 1,
            "product_price": 1,
            "sale": 1,
            "sale_item": 1,
            "reservation": 1,
            "purchase_order": 1,
            "purchase_item": 1,
        }
        RESERVATION_ACTIVE_STATES = {"activa"}
        ORDER_EDITABLE_STATES = {"borrador"}
        ORDER_RECEIVABLE_STATES = {"enviada", "parcialmente_recibida"}


        def _next_commercial_id(kind: str) -> int:
            value = NEXT_COMMERCIAL_ID[kind]
            NEXT_COMMERCIAL_ID[kind] += 1
            return value


        def _customer_type(value: str | None) -> str:
            normalized = str(value or "minorista").strip().lower()
            if normalized not in CUSTOMER_TYPES:
                raise HTTPException(422, {"code": "validation_error", "message": "customer_type_invalid"})
            return normalized


        def _customer_or_404(customer_id: int) -> dict[str, Any]:
            return _get(CUSTOMERS, customer_id, "customer")


        def _active_customer(customer_id: int) -> dict[str, Any]:
            customer = _customer_or_404(customer_id)
            if customer.get("estado") != "activo":
                raise HTTPException(422, {"code": "inactive_entity", "message": "customer_inactive"})
            return customer


        def _customer_has_sales(customer_id: int) -> bool:
            return any(sale.get("cliente_id") == customer_id for sale in SALES.values())


        def _product_active_or_422(product_id: int) -> dict[str, Any]:
            product = _product_or_404(product_id)
            if product.get("estado") != "activo":
                raise HTTPException(422, {"code": "inactive_entity", "message": "product_inactive"})
            return product


        def _active_reservation_total(product_id: int, exclude_reservation_id: int | None = None) -> float:
            total = 0.0
            for reservation_id, reservation in STOCK_RESERVATIONS.items():
                if exclude_reservation_id is not None and reservation_id == exclude_reservation_id:
                    continue
                if reservation.get("estado") in RESERVATION_ACTIVE_STATES and int(reservation.get("product_id", 0)) == product_id:
                    total += float(reservation.get("cantidad_reservada", 0))
            return round(total, 4)


        def _available_product_stock(product_id: int, exclude_reservation_id: int | None = None) -> float:
            product = _product_active_or_422(product_id)
            return max(round(float(product.get("cantidad_stock", 0)) - _active_reservation_total(product_id, exclude_reservation_id), 4), 0)


        def _suggested_unit_price(product: dict[str, Any], customer_type: str, quantity: float) -> float:
            base_price = _non_negative(product.get("precio_venta", 0), "precio_venta")
            matching_prices = [
                item
                for item in PRODUCT_PRICES.values()
                if item["product_id"] == product["id"] and item["tipo_cliente"] == customer_type
            ]
            if matching_prices:
                price = matching_prices[-1]
                if quantity >= 12 and float(price.get("precio_por_docena", 0)) > 0:
                    return round(float(price["precio_por_docena"]) / 12, 4)
                return round(float(price.get("precio_unitario", base_price)), 4)
            discount = float(CUSTOMER_TYPES[customer_type]["descuento_pct_base"])
            return round(base_price * (1 - discount / 100), 4)


        def _sale_items_for(sale_id: int) -> list[dict[str, Any]]:
            return [item for item in SALE_ITEMS.values() if item["sale_id"] == sale_id]


        def _sale_public(sale: dict[str, Any]) -> dict[str, Any]:
            return {**sale, "items": _sale_items_for(sale["id"])}


        def _create_sale_from_lines(request: Request, user: dict[str, Any], body: dict[str, Any], reserved_stock_by_product: dict[int, float] | None = None) -> dict[str, Any]:
            customer_id = int(body.get("cliente_id", body.get("customer_id", 0)) or 0)
            customer = _active_customer(customer_id) if customer_id else None
            customer_type = _customer_type(customer.get("tipo_cliente") if customer else body.get("tipo_cliente"))
            raw_items = body.get("items", body.get("lineas", []))
            if not isinstance(raw_items, list) or not raw_items:
                raise HTTPException(422, {"code": "validation_error", "message": "sale_items_required"})
            reserved_stock_by_product = reserved_stock_by_product or {}
            prepared_items: list[dict[str, Any]] = []
            total = 0.0
            profit_total = 0.0
            warnings: list[str] = []
            for raw in raw_items:
                if not isinstance(raw, dict):
                    raise HTTPException(422, {"code": "validation_error", "message": "sale_item_invalid"})
                product_id = int(raw.get("product_id", 0))
                product = _product_active_or_422(product_id)
                quantity = _positive(raw.get("cantidad", raw.get("quantity")), "sale_quantity")
                reserved_for_line = float(reserved_stock_by_product.get(product_id, 0))
                if quantity > _available_product_stock(product_id) + reserved_for_line:
                    raise HTTPException(422, {"code": "stock_unavailable", "message": "product_stock_unavailable"})
                unit_price = raw.get("precio_unitario", raw.get("unit_price"))
                if unit_price in {None, ""}:
                    unit_price_value = _suggested_unit_price(product, customer_type, quantity)
                else:
                    unit_price_value = _non_negative(unit_price, "precio_unitario")
                if unit_price_value == 0:
                    warnings.append("price_zero")
                unit_cost = _non_negative(product.get("costo_unitario", 0), "costo_unitario")
                line_total = round(quantity * unit_price_value, 4)
                line_profit = round((unit_price_value - unit_cost) * quantity, 4)
                total += line_total
                profit_total += line_profit
                prepared_items.append(
                    {
                        "product": product,
                        "product_id": product_id,
                        "cantidad": quantity,
                        "precio_unitario": unit_price_value,
                        "costo_unitario": unit_cost,
                        "ganancia_unitaria": round(unit_price_value - unit_cost, 4),
                        "line_total": line_total,
                        "line_profit": line_profit,
                    }
                )
            sale_id = _next_commercial_id("sale")
            sale = _timestamps(
                {
                    "id": sale_id,
                    "numero_documento": _required_text(body, "numero_documento") if body.get("numero_documento") else f"VTA-{sale_id:04d}",
                    "cliente_id": customer_id or None,
                    "tipo_cliente": customer_type,
                    "fecha_venta": _optional_text(body, "fecha_venta", _iso()),
                    "responsable_id": int(body.get("responsable_id") or user["id"]),
                    "observacion": _optional_text(body, "observacion"),
                    "estado": "confirmada",
                    "total": round(total, 4),
                    "ganancia_total": round(profit_total, 4),
                    "warnings": sorted(set(warnings)),
                },
                creating=True,
            )
            SALES[sale_id] = sale
            for item in prepared_items:
                product = item.pop("product")
                product["cantidad_stock"] = round(float(product.get("cantidad_stock", 0)) - float(item["cantidad"]), 4)
                product["updated_at"] = _iso()
                sale_item_id = _next_commercial_id("sale_item")
                sale_item = _timestamps({"id": sale_item_id, "sale_id": sale_id, **item}, creating=True)
                SALE_ITEMS[sale_item_id] = sale_item
                _record_product_movement(product, "VENTA", float(sale_item["cantidad"]), float(sale_item["costo_unitario"]), f"sale:{sale_id}", user["id"])
            _audit(request, user["id"], "sale_created", "sales", sale_id, "HITO-005")
            return _sale_public(sale)


        def _order_lines_for(order_id: int) -> list[dict[str, Any]]:
            return [item for item in PURCHASE_ORDER_ITEMS.values() if item["order_id"] == order_id]


        def _order_public(order: dict[str, Any]) -> dict[str, Any]:
            return {**order, "items": _order_lines_for(order["id"])}


        def _replace_order_items(order: dict[str, Any], raw_items: Any) -> None:
            if not isinstance(raw_items, list) or not raw_items:
                raise HTTPException(422, {"code": "validation_error", "message": "purchase_order_items_required"})
            for item_id in [item_id for item_id, item in PURCHASE_ORDER_ITEMS.items() if item["order_id"] == order["id"]]:
                del PURCHASE_ORDER_ITEMS[item_id]
            total = 0.0
            for raw in raw_items:
                if not isinstance(raw, dict):
                    raise HTTPException(422, {"code": "validation_error", "message": "purchase_order_item_invalid"})
                supply_id = int(raw.get("supply_id", 0))
                supply = _active_supply(supply_id)
                quantity = _positive(raw.get("cantidad_solicitada", raw.get("cantidad")), "cantidad_solicitada")
                price = _non_negative(raw.get("precio_unitario", raw.get("unit_price")), "precio_unitario")
                item_id = _next_commercial_id("purchase_item")
                PURCHASE_ORDER_ITEMS[item_id] = _timestamps(
                    {
                        "id": item_id,
                        "order_id": order["id"],
                        "supply_id": supply_id,
                        "nombre_insumo": supply["nombre"],
                        "cantidad_solicitada": quantity,
                        "precio_unitario": price,
                        "cantidad_recibida": 0,
                    },
                    creating=True,
                )
                total += quantity * price
            order["total_estimado"] = round(total, 4)
            order["updated_at"] = _iso()


        @app.get("/api/v1/customers")
        def list_customers(tipo_cliente: str | None = None, estado: str | None = None, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "customers.read")
            customers = list(CUSTOMERS.values())
            if tipo_cliente:
                customers = [item for item in customers if item.get("tipo_cliente") == tipo_cliente]
            if estado:
                customers = [item for item in customers if item.get("estado") == estado]
            return ok(customers)


        @app.post("/api/v1/customers")
        def create_customer(request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "customers.create")
            fiscal_id = _required_text(body, "identificador_fiscal")
            _ensure_unique(CUSTOMERS, "identificador_fiscal", fiscal_id)
            email = _optional_email(body.get("email", ""))
            customer_id = _next_commercial_id("customer")
            customer = _timestamps(
                {
                    "id": customer_id,
                    "nombre": _required_text(body, "nombre"),
                    "identificador_fiscal": fiscal_id,
                    "email": email,
                    "telefono": _optional_text(body, "telefono"),
                    "direccion": _optional_text(body, "direccion"),
                    "tipo_cliente": _customer_type(body.get("tipo_cliente")),
                    "forma_pago": _optional_text(body, "forma_pago", "contado"),
                    "limite_credito": _non_negative(body.get("limite_credito", 0), "limite_credito"),
                    "estado": "activo",
                },
                creating=True,
            )
            CUSTOMERS[customer_id] = customer
            _audit(request, user["id"], "customer_created", "customers", customer_id, "HITO-005")
            return ok(customer)


        @app.get("/api/v1/customers/{id}")
        def get_customer(id: int, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "customers.read")
            customer = _customer_or_404(id)
            history = [_sale_public(sale) for sale in SALES.values() if sale.get("cliente_id") == id]
            return ok({**customer, "sales": history})


        @app.put("/api/v1/customers/{id}")
        def update_customer(id: int, request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "customers.update")
            customer = _customer_or_404(id)
            if customer.get("estado") == "eliminado":
                raise HTTPException(422, {"code": "state_conflict", "message": "customer_deleted"})
            if "identificador_fiscal" in body:
                fiscal_id = _required_text(body, "identificador_fiscal")
                if fiscal_id != customer["identificador_fiscal"] and _customer_has_sales(id):
                    raise HTTPException(422, {"code": "state_conflict", "message": "customer_fiscal_locked_by_sales"})
                _ensure_unique(CUSTOMERS, "identificador_fiscal", fiscal_id, id)
                customer["identificador_fiscal"] = fiscal_id
            for field in ["nombre", "telefono", "direccion", "forma_pago"]:
                if field in body:
                    customer[field] = _optional_text(body, field)
            if "email" in body:
                customer["email"] = _optional_email(body.get("email", ""))
            if "tipo_cliente" in body:
                customer["tipo_cliente"] = _customer_type(body.get("tipo_cliente"))
            if "limite_credito" in body:
                customer["limite_credito"] = _non_negative(body.get("limite_credito"), "limite_credito")
            _timestamps(customer)
            _audit(request, user["id"], "customer_updated", "customers", id, "HITO-005")
            return ok(customer)


        @app.patch("/api/v1/customers/{id}/toggle-status")
        def toggle_customer_status(id: int, request: Request, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "customers.update")
            customer = _customer_or_404(id)
            customer["estado"] = "inactivo" if customer.get("estado") == "activo" else "activo"
            customer["updated_at"] = _iso()
            _audit(request, user["id"], "customer_status_toggled", "customers", id, customer["estado"])
            return ok(customer)


        @app.get("/api/v1/sales")
        def list_sales(cliente_id: int | None = None, estado: str | None = None, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "sales.read")
            sales = [_sale_public(sale) for sale in SALES.values()]
            if cliente_id is not None:
                sales = [item for item in sales if item.get("cliente_id") == cliente_id]
            if estado:
                sales = [item for item in sales if item.get("estado") == estado]
            return ok(sales)


        @app.post("/api/v1/sales")
        def create_sale(request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "sales.create")
            return ok(_create_sale_from_lines(request, user, body))


        @app.post("/api/v1/sales/{id}/void")
        def void_sale(id: int, request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "sales.create")
            reason = _required_text(body, "motivo", "reason")
            sale = _get(SALES, id, "sale")
            if sale.get("estado") != "confirmada":
                raise HTTPException(422, {"code": "state_conflict", "message": "sale_not_voidable"})
            for item in _sale_items_for(id):
                product = _product_or_404(int(item["product_id"]))
                product["cantidad_stock"] = round(float(product.get("cantidad_stock", 0)) + float(item["cantidad"]), 4)
                product["updated_at"] = _iso()
                _record_product_movement(product, "DEVOLUCION", float(item["cantidad"]), float(item["costo_unitario"]), f"sale_void:{id}", user["id"])
            sale["estado"] = "anulada"
            sale["motivo_anulacion"] = reason
            sale["updated_at"] = _iso()
            _audit(request, user["id"], "sale_voided", "sales", id, reason)
            return ok(_sale_public(sale))


        @app.get("/api/v1/reservations")
        def list_reservations(estado: str | None = None, product_id: int | None = None, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "reservations.manage")
            reservations = list(STOCK_RESERVATIONS.values())
            if estado:
                reservations = [item for item in reservations if item.get("estado") == estado]
            if product_id is not None:
                reservations = [item for item in reservations if item.get("product_id") == product_id]
            return ok(reservations)


        @app.post("/api/v1/reservations")
        def create_reservation(request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "reservations.create")
            customer = _active_customer(int(body.get("cliente_id", body.get("customer_id", 0))))
            product = _product_active_or_422(int(body.get("product_id", 0)))
            quantity = _positive(body.get("cantidad_reservada", body.get("cantidad")), "cantidad_reservada")
            if quantity > _available_product_stock(product["id"]):
                raise HTTPException(422, {"code": "stock_unavailable", "message": "reservation_exceeds_free_stock"})
            price = body.get("precio")
            price_value = _suggested_unit_price(product, customer["tipo_cliente"], quantity) if price in {None, ""} else _non_negative(price, "precio")
            reservation_id = _next_commercial_id("reservation")
            reservation = _timestamps(
                {
                    "id": reservation_id,
                    "cliente_id": customer["id"],
                    "product_id": product["id"],
                    "cantidad_reservada": quantity,
                    "fecha_entrega_prometida": _required_text(body, "fecha_entrega_prometida"),
                    "precio": price_value,
                    "estado": "activa",
                },
                creating=True,
            )
            STOCK_RESERVATIONS[reservation_id] = reservation
            _audit(request, user["id"], "reservation_created", "stock_reservations", reservation_id, "HITO-005")
            return ok(reservation)


        @app.post("/api/v1/reservations/{id}/release")
        def release_reservation(id: int, request: Request, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "reservations.manage")
            reservation = _get(STOCK_RESERVATIONS, id, "reservation")
            if reservation.get("estado") != "activa":
                raise HTTPException(422, {"code": "state_conflict", "message": "reservation_not_active"})
            reservation["estado"] = "liberada"
            reservation["updated_at"] = _iso()
            _audit(request, user["id"], "reservation_released", "stock_reservations", id, "HITO-005")
            return ok(reservation)


        @app.post("/api/v1/reservations/{id}/consume")
        def consume_reservation(id: int, request: Request, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "reservations.manage")
            reservation = _get(STOCK_RESERVATIONS, id, "reservation")
            if reservation.get("estado") != "activa":
                raise HTTPException(422, {"code": "state_conflict", "message": "reservation_not_active"})
            product = _product_active_or_422(int(reservation["product_id"]))
            quantity = float(reservation["cantidad_reservada"])
            if quantity > float(product.get("cantidad_stock", 0)):
                raise HTTPException(422, {"code": "stock_unavailable", "message": "reservation_stock_missing"})
            sale = _create_sale_from_lines(
                request,
                user,
                {
                    "cliente_id": reservation["cliente_id"],
                    "items": [{"product_id": product["id"], "cantidad": quantity, "precio_unitario": reservation["precio"]}],
                    "observacion": f"reservation:{id}",
                },
                reserved_stock_by_product={product["id"]: quantity},
            )
            reservation["estado"] = "consumida"
            reservation["sale_id"] = sale["id"]
            reservation["updated_at"] = _iso()
            _audit(request, user["id"], "reservation_consumed", "stock_reservations", id, f"sale={sale['id']}")
            return ok({"reservation": reservation, "sale": sale})


        @app.get("/api/v1/purchase-orders")
        def list_purchase_orders(estado: str | None = None, proveedor_id: int | None = None, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "purchase-orders.read")
            orders = [_order_public(order) for order in PURCHASE_ORDERS.values()]
            if estado:
                orders = [item for item in orders if item.get("estado") == estado]
            if proveedor_id is not None:
                orders = [item for item in orders if item.get("proveedor_id") == proveedor_id]
            return ok(orders)


        @app.post("/api/v1/purchase-orders")
        def create_purchase_order(request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "purchase-orders.create")
            supplier = _active_supplier(int(body.get("proveedor_id", body.get("supplier_id", 0))))
            order_id = _next_commercial_id("purchase_order")
            order = _timestamps(
                {
                    "id": order_id,
                    "numero_orden": _required_text(body, "numero_orden") if body.get("numero_orden") else f"OC-{order_id:04d}",
                    "proveedor_id": supplier["id"],
                    "fecha_emision": _optional_text(body, "fecha_emision", _iso()),
                    "fecha_esperada_recepcion": _optional_text(body, "fecha_esperada_recepcion"),
                    "observacion": _optional_text(body, "observacion"),
                    "total_estimado": 0,
                    "estado": "borrador",
                },
                creating=True,
            )
            PURCHASE_ORDERS[order_id] = order
            _replace_order_items(order, body.get("items", body.get("lineas", [])))
            _audit(request, user["id"], "purchase_order_created", "purchase_orders", order_id, "HITO-005")
            return ok(_order_public(order))


        @app.get("/api/v1/purchase-orders/{id}")
        def get_purchase_order(id: int, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "purchase-orders.read")
            return ok(_order_public(_get(PURCHASE_ORDERS, id, "purchase_order")))


        @app.put("/api/v1/purchase-orders/{id}")
        def update_purchase_order(id: int, request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "purchase-orders.create")
            order = _get(PURCHASE_ORDERS, id, "purchase_order")
            if order.get("estado") not in ORDER_EDITABLE_STATES:
                raise HTTPException(422, {"code": "state_conflict", "message": "purchase_order_not_editable"})
            if "proveedor_id" in body or "supplier_id" in body:
                supplier = _active_supplier(int(body.get("proveedor_id", body.get("supplier_id", 0))))
                order["proveedor_id"] = supplier["id"]
            for field in ["fecha_emision", "fecha_esperada_recepcion", "observacion"]:
                if field in body:
                    order[field] = _optional_text(body, field)
            if "items" in body or "lineas" in body:
                _replace_order_items(order, body.get("items", body.get("lineas", [])))
            _timestamps(order)
            _audit(request, user["id"], "purchase_order_updated", "purchase_orders", id, "HITO-005")
            return ok(_order_public(order))


        @app.post("/api/v1/purchase-orders/{id}/send")
        def send_purchase_order(id: int, request: Request, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "purchase-orders.create")
            order = _get(PURCHASE_ORDERS, id, "purchase_order")
            if order.get("estado") != "borrador":
                raise HTTPException(422, {"code": "state_conflict", "message": "purchase_order_not_sendable"})
            if not _order_lines_for(id):
                raise HTTPException(422, {"code": "validation_error", "message": "purchase_order_items_required"})
            order["estado"] = "enviada"
            order["updated_at"] = _iso()
            _audit(request, user["id"], "purchase_order_sent", "purchase_orders", id, "HITO-005")
            return ok(_order_public(order))


        @app.post("/api/v1/purchase-orders/{id}/receive")
        def receive_purchase_order(id: int, request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "purchase-orders.receive")
            order = _get(PURCHASE_ORDERS, id, "purchase_order")
            if order.get("estado") not in ORDER_RECEIVABLE_STATES:
                raise HTTPException(422, {"code": "state_conflict", "message": "purchase_order_not_receivable"})
            raw_items = body.get("items", body.get("lineas", []))
            if not isinstance(raw_items, list) or not raw_items:
                raise HTTPException(422, {"code": "validation_error", "message": "receipt_items_required"})
            receipt_movements: list[dict[str, Any]] = []
            for raw in raw_items:
                supply_id = int(raw.get("supply_id", 0))
                incoming = _positive(raw.get("cantidad_recibida", raw.get("cantidad")), "cantidad_recibida")
                line = next((item for item in _order_lines_for(id) if item["supply_id"] == supply_id), None)
                if line is None:
                    raise HTTPException(422, {"code": "validation_error", "message": "supply_not_in_order"})
                pending = float(line["cantidad_solicitada"]) - float(line.get("cantidad_recibida", 0))
                if incoming > pending and not bool(body.get("allow_over_receive", False)):
                    raise HTTPException(422, {"code": "state_conflict", "message": "receipt_exceeds_pending"})
                supply = _active_supply(supply_id)
                unit_cost = _non_negative(raw.get("precio_unitario", line["precio_unitario"]), "precio_unitario")
                supply["stock_actual"] = round(float(supply.get("stock_actual", 0)) + incoming, 4)
                supply["costo_unitario"] = unit_cost
                supply["updated_at"] = _iso()
                line["cantidad_recibida"] = round(float(line.get("cantidad_recibida", 0)) + incoming, 4)
                line["updated_at"] = _iso()
                entry_id = _next_inventory_id("entry")
                entry = _timestamps(
                    {
                        "id": entry_id,
                        "supply_id": supply_id,
                        "cantidad": incoming,
                        "costo_unitario": unit_cost,
                        "proveedor_id": order["proveedor_id"],
                        "referencia": f"purchase_order:{id}",
                        "stock_actual": supply["stock_actual"],
                    },
                    creating=True,
                )
                SUPPLY_ENTRIES[entry_id] = entry
                movement_id = _next_inventory_id("movement")
                movement = {
                    "id": movement_id,
                    "supply_id": supply_id,
                    "tipo_movimiento": "ENTRADA",
                    "cantidad": incoming,
                    "costo_unitario": unit_cost,
                    "saldo_resultante": supply["stock_actual"],
                    "referencia": f"purchase_order:{id}",
                    "user_id": user["id"],
                    "created_at": _iso(),
                }
                SUPPLY_MOVEMENTS[movement_id] = movement
                _evaluate_stock_alert(supply)
                receipt_movements.append(movement)
            all_received = all(float(item.get("cantidad_recibida", 0)) >= float(item["cantidad_solicitada"]) for item in _order_lines_for(id))
            order["estado"] = "recibida" if all_received else "parcialmente_recibida"
            order["updated_at"] = _iso()
            _audit(request, user["id"], "purchase_order_received", "purchase_orders", id, order["estado"])
            return ok({"order": _order_public(order), "movements": receipt_movements})


        @app.post("/api/v1/purchase-orders/{id}/cancel")
        def cancel_purchase_order(id: int, request: Request, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "purchase-orders.cancel")
            order = _get(PURCHASE_ORDERS, id, "purchase_order")
            if order.get("estado") == "recibida":
                raise HTTPException(422, {"code": "state_conflict", "message": "received_order_not_cancelable"})
            order["estado"] = "cancelada"
            order["updated_at"] = _iso()
            _audit(request, user["id"], "purchase_order_cancelled", "purchase_orders", id, "HITO-005")
            return ok(_order_public(order))
        """
    ).strip()
    return hito4 + "\n\n" + commerce_block


def _hito6_backend_main() -> str:
    hito5 = _hito5_backend_main().replace('"milestone": "HITO-005"', '"milestone": "HITO-006"')
    analytics_block = dedent(
        """

        # HITO-006 dashboard, KPIs reales, alertas operacionales y reportes exportables.
        REPORT_TYPES = {
            "produccion": "Produccion",
            "ventas": "Ventas",
            "inventario": "Inventario",
            "kardex": "Kardex",
            "mermas": "Mermas",
            "compras": "Compras",
            "auditoria": "Auditoria",
        }
        REPORT_FORMATS = {
            "csv": "text/csv",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "pdf": "application/pdf",
        }
        EXPORT_JOBS: dict[int, dict[str, Any]] = {}
        NEXT_ANALYTICS_ID = {"export_job": 1}


        def _next_analytics_id(kind: str) -> int:
            value = NEXT_ANALYTICS_ID[kind]
            NEXT_ANALYTICS_ID[kind] += 1
            return value


        def _grant_permissions(role_name: str, permissions: set[str]) -> None:
            role = ROLES.get(role_name)
            if not role:
                return
            current = set(role.get("permissions", []))
            if "*" in current:
                return
            role["permissions"] = sorted(current | permissions)


        _grant_permissions("auditor", {"reports.read", "reports.export"})
        _grant_permissions("ventas", {"reports.read"})
        _grant_permissions("compras", {"reports.read"})
        _grant_permissions("produccion", {"reports.read"})
        _grant_permissions("inventario", {"reports.read"})


        def _confirmed_sales() -> list[dict[str, Any]]:
            return [sale for sale in SALES.values() if sale.get("estado") == "confirmada"]


        def _month_key(value: Any) -> str:
            return str(value or _iso())[:7]


        def _round(value: float) -> float:
            return round(float(value), 4)


        def _chart_from_pairs(pairs: list[tuple[str, float]]) -> list[dict[str, Any]]:
            totals: dict[str, float] = {}
            for label, value in pairs:
                totals[label] = totals.get(label, 0.0) + float(value)
            return [{"label": label, "value": _round(value)} for label, value in sorted(totals.items())]


        def _operational_alerts() -> list[dict[str, Any]]:
            alerts: list[dict[str, Any]] = []
            for supply in SUPPLIES.values():
                if supply.get("estado") != "activo":
                    continue
                current = float(supply.get("stock_actual", 0))
                minimum = float(supply.get("stock_minimo", 0))
                if current <= minimum:
                    alerts.append(
                        {
                            "type": "stock",
                            "severity": "critical" if current <= 0 else "warning",
                            "entity": "supplies",
                            "entity_id": supply["id"],
                            "message": "stock_below_minimum",
                            "current": _round(current),
                            "threshold": _round(minimum),
                        }
                    )
            for record in WASTE_RECORDS.values():
                batch = PRODUCTION_BATCHES.get(int(record.get("batch_id") or 0))
                produced = float(batch.get("cantidad_producida", 0)) if batch else 0
                lost = float(record.get("cantidad_perdida", 0))
                pct = (lost / produced * 100) if produced > 0 else 0
                if pct > 5:
                    alerts.append(
                        {
                            "type": "merma",
                            "severity": "warning",
                            "entity": "waste_records",
                            "entity_id": record["id"],
                            "message": "waste_above_five_percent",
                            "current": _round(pct),
                            "threshold": 5,
                        }
                    )
            for order in PURCHASE_ORDERS.values():
                if order.get("estado") in {"enviada", "parcialmente_recibida"}:
                    alerts.append(
                        {
                            "type": "compra",
                            "severity": "info",
                            "entity": "purchase_orders",
                            "entity_id": order["id"],
                            "message": "purchase_order_pending_receipt",
                            "current": order.get("estado"),
                            "threshold": "recibida",
                        }
                    )
            today = _iso()[:10]
            for reservation in STOCK_RESERVATIONS.values():
                promised = str(reservation.get("fecha_entrega_prometida", ""))[:10]
                if reservation.get("estado") == "activa" and promised and promised < today:
                    alerts.append(
                        {
                            "type": "reserva",
                            "severity": "warning",
                            "entity": "stock_reservations",
                            "entity_id": reservation["id"],
                            "message": "reservation_past_promised_date",
                            "current": promised,
                            "threshold": today,
                        }
                    )
            return alerts


        def _dashboard_payload(fecha_inicio: str | None = None, fecha_fin: str | None = None, bodega_id: int | None = None) -> dict[str, Any]:
            completed_batches = [batch for batch in PRODUCTION_BATCHES.values() if batch.get("estado") == "completado"]
            confirmed_sales = _confirmed_sales()
            active_reservations = [reservation for reservation in STOCK_RESERVATIONS.values() if reservation.get("estado") == "activa"]
            pending_orders = [order for order in PURCHASE_ORDERS.values() if order.get("estado") in {"enviada", "parcialmente_recibida"}]
            alerts = _operational_alerts()
            product_stock = sum(float(product.get("cantidad_stock", 0)) for product in FINISHED_PRODUCTS.values())
            reserved_stock = sum(float(reservation.get("cantidad_reservada", 0)) for reservation in active_reservations)
            kpis = {
                "litros_producidos": _round(sum(float(batch.get("cantidad_producida", 0)) for batch in completed_batches)),
                "lotes_completados": len(completed_batches),
                "unidades_producto_stock": _round(product_stock),
                "stock_libre": _round(max(product_stock - reserved_stock, 0)),
                "ventas_confirmadas": len(confirmed_sales),
                "monto_ventas": _round(sum(float(sale.get("total", 0)) for sale in confirmed_sales)),
                "margen_bruto": _round(sum(float(sale.get("ganancia_total", 0)) for sale in confirmed_sales)),
                "ordenes_pendientes": len(pending_orders),
                "mermas_total": _round(sum(float(record.get("costo_total", 0)) for record in WASTE_RECORDS.values())),
                "alertas_operacionales": len(alerts),
            }
            charts = {
                "ventas_por_mes": _chart_from_pairs([(_month_key(sale.get("created_at")), float(sale.get("total", 0))) for sale in confirmed_sales]),
                "stock_por_producto": [
                    {"label": product.get("nombre", product.get("sku", str(product["id"]))), "value": _round(product.get("cantidad_stock", 0))}
                    for product in FINISHED_PRODUCTS.values()
                ],
                "produccion_por_receta": _chart_from_pairs([(str(batch.get("recipe_id")), float(batch.get("cantidad_producida", 0))) for batch in completed_batches]),
                "mermas_por_tipo": _chart_from_pairs([(str(record.get("tipo_merma", "otro")), float(record.get("costo_total", 0))) for record in WASTE_RECORDS.values()]),
            }
            return {
                "filters": {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin, "bodega_id": bodega_id},
                "kpis": kpis,
                "charts": charts,
                "alerts": alerts,
                "data_source": "operational_memory_store",
                "hito7_scope_excluded": ["equipment", "expenses", "monthly-goals", "backups", "deploy"],
            }


        def _report_catalog() -> list[dict[str, Any]]:
            return [
                {"type": report_type, "name": name, "formats": sorted(REPORT_FORMATS)}
                for report_type, name in REPORT_TYPES.items()
            ]


        def _sale_items_for_report() -> list[dict[str, Any]]:
            return list(SALE_ITEMS.values())


        def _report_rows(report_type: str) -> list[dict[str, Any]]:
            if report_type == "produccion":
                return [
                    {
                        "id": batch["id"],
                        "numero_lote": batch.get("numero_lote"),
                        "estado": batch.get("estado"),
                        "cantidad_producida": batch.get("cantidad_producida", 0),
                        "costo_total": batch.get("costo_total", 0),
                    }
                    for batch in PRODUCTION_BATCHES.values()
                ]
            if report_type == "ventas":
                return [
                    {
                        "id": sale["id"],
                        "cliente_id": sale.get("cliente_id"),
                        "estado": sale.get("estado"),
                        "total": sale.get("total", 0),
                        "ganancia_total": sale.get("ganancia_total", 0),
                    }
                    for sale in SALES.values()
                ]
            if report_type == "inventario":
                supply_rows = [
                    {"tipo": "insumo", "id": item["id"], "nombre": item.get("nombre"), "stock": item.get("stock_actual", 0)}
                    for item in SUPPLIES.values()
                ]
                product_rows = [
                    {"tipo": "producto", "id": item["id"], "nombre": item.get("nombre"), "stock": item.get("cantidad_stock", 0)}
                    for item in FINISHED_PRODUCTS.values()
                ]
                return supply_rows + product_rows
            if report_type == "kardex":
                supply_rows = [
                    {
                        "tipo": "insumo",
                        "entity_id": item.get("supply_id"),
                        "movimiento": item.get("tipo_movimiento"),
                        "cantidad": item.get("cantidad"),
                        "referencia": item.get("referencia"),
                    }
                    for item in SUPPLY_MOVEMENTS.values()
                ]
                product_rows = [
                    {
                        "tipo": "producto",
                        "entity_id": item.get("product_id"),
                        "movimiento": item.get("tipo_movimiento"),
                        "cantidad": item.get("cantidad"),
                        "referencia": item.get("referencia"),
                    }
                    for item in PRODUCT_MOVEMENTS.values()
                ]
                return supply_rows + product_rows
            if report_type == "mermas":
                return [
                    {
                        "id": item["id"],
                        "tipo_entidad": item.get("tipo_entidad"),
                        "entidad_id": item.get("entidad_id"),
                        "cantidad_perdida": item.get("cantidad_perdida"),
                        "costo_total": item.get("costo_total"),
                    }
                    for item in WASTE_RECORDS.values()
                ]
            if report_type == "compras":
                return [
                    {
                        "id": order["id"],
                        "numero_orden": order.get("numero_orden"),
                        "proveedor_id": order.get("proveedor_id"),
                        "estado": order.get("estado"),
                        "total_estimado": order.get("total_estimado", 0),
                    }
                    for order in PURCHASE_ORDERS.values()
                ]
            if report_type == "auditoria":
                return list(AUDIT_LOGS)
            raise HTTPException(422, {"code": "validation_error", "message": "report_type_invalid"})


        def _csv_escape(value: Any) -> str:
            text = str(value if value is not None else "")
            if any(char in text for char in [",", '"', "\\n"]):
                return '"' + text.replace('"', '""') + '"'
            return text


        def _csv_content(rows: list[dict[str, Any]]) -> str:
            if not rows:
                return ""
            headers = sorted({key for row in rows for key in row})
            lines = [",".join(headers)]
            lines.extend(",".join(_csv_escape(row.get(header, "")) for header in headers) for row in rows)
            return "\\n".join(lines)


        def _export_content(report_type: str, fmt: str, rows: list[dict[str, Any]]) -> str:
            if fmt == "csv":
                return _csv_content(rows)
            if fmt == "xlsx":
                return "local-xlsx-workbook\\nreport=" + report_type + "\\nrows=" + str(len(rows))
            if fmt == "pdf":
                return "local-pdf-report\\nreport=" + report_type + "\\nrows=" + str(len(rows))
            raise HTTPException(422, {"code": "validation_error", "message": "report_format_invalid"})


        @app.get("/api/v1/dashboard")
        def dashboard(fecha_inicio: str | None = None, fecha_fin: str | None = None, bodega_id: int | None = None, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "reports.read")
            return ok(_dashboard_payload(fecha_inicio, fecha_fin, bodega_id))


        @app.get("/api/v1/reports")
        def list_reports(user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "reports.read")
            permissions = _permissions_for(user)
            can_see_all = "*" in permissions or "audit.read" in permissions
            jobs = list(EXPORT_JOBS.values()) if can_see_all else [job for job in EXPORT_JOBS.values() if job.get("user_id") == user["id"]]
            return ok({"reports": _report_catalog(), "export_jobs": jobs})


        @app.post("/api/v1/reports/export")
        def export_report(request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "reports.export")
            report_type = str(body.get("tipo_reporte", body.get("type", ""))).strip().lower()
            fmt = str(body.get("formato", body.get("format", "csv"))).strip().lower()
            if report_type not in REPORT_TYPES:
                raise HTTPException(422, {"code": "validation_error", "message": "report_type_invalid"})
            if report_type == "auditoria":
                _ensure_permission(user, "audit.read")
            if fmt not in REPORT_FORMATS:
                raise HTTPException(422, {"code": "validation_error", "message": "report_format_invalid"})
            rows = _report_rows(report_type)
            job_id = _next_analytics_id("export_job")
            filename = f"{report_type}-{job_id:04d}.{fmt}"
            job = _timestamps(
                {
                    "id": job_id,
                    "user_id": user["id"],
                    "tipo_reporte": report_type,
                    "formato": fmt,
                    "filtros": body.get("filtros", {}),
                    "estado": "completado",
                    "archivo_url": f"local://exports/{filename}",
                    "row_count": len(rows),
                    "completed_at": _iso(),
                },
                creating=True,
            )
            EXPORT_JOBS[job_id] = job
            _audit(request, user["id"], "report_exported", "export_jobs", job_id, f"{report_type}.{fmt}")
            return ok(
                {
                    "job": job,
                    "filename": filename,
                    "mime_type": REPORT_FORMATS[fmt],
                    "content": _export_content(report_type, fmt, rows),
                    "rows": rows,
                }
            )
        """
    ).strip()
    return hito5 + "\n\n" + analytics_block


def _hito7_backend_main() -> str:
    hito6 = _hito6_backend_main().replace('"milestone": "HITO-006"', '"milestone": "HITO-007"')
    close_block = dedent(
        """

        # HITO-007 cierre: equipos, finanzas, metas, backups locales y preparacion de deploy.
        from app.jobs.scheduler import job_policy, should_run

        HITO6_OPERATIONAL_ALERTS = _operational_alerts
        HITO6_DASHBOARD_PAYLOAD = _dashboard_payload
        HITO6_REPORT_ROWS = _report_rows

        EQUIPMENT_STATES = {"operativo", "mantenimiento", "fuera_servicio", "descartado"}
        EQUIPMENT_TYPES: dict[int, dict[str, Any]] = {
            1: {"id": 1, "nombre": "Fermentador", "descripcion": "Equipo productivo", "intervalo_revision_dias": 30},
            2: {"id": 2, "nombre": "Bomba", "descripcion": "Movimiento de liquidos", "intervalo_revision_dias": 45},
        }
        EQUIPMENT: dict[int, dict[str, Any]] = {}
        EQUIPMENT_MOVEMENTS: dict[int, dict[str, Any]] = {}
        EXPENSE_CATEGORIES: dict[int, dict[str, Any]] = {
            1: {"id": 1, "nombre": "Insumos indirectos", "descripcion": "Gastos operativos generales"},
            2: {"id": 2, "nombre": "Mantencion", "descripcion": "Mantencion de equipos e instalaciones"},
            3: {"id": 3, "nombre": "Servicios", "descripcion": "Servicios basicos y operacionales"},
        }
        OPERATIONAL_EXPENSES: dict[int, dict[str, Any]] = {}
        MONTHLY_GOALS: dict[str, dict[str, Any]] = {}
        BACKUP_RUNS: dict[int, dict[str, Any]] = {}
        NEXT_HITO7_ID = {"equipment": 1, "equipment_movement": 1, "expense": 1, "backup": 1}


        def _next_hito7_id(kind: str) -> int:
            value = NEXT_HITO7_ID[kind]
            NEXT_HITO7_ID[kind] += 1
            return value


        def _date_text(value: Any | None = None) -> str:
            return str(value or _iso())[:10]


        def _parse_date(value: Any, field: str) -> datetime:
            try:
                return datetime.strptime(str(value)[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                raise HTTPException(422, {"code": "validation_error", "message": f"{field}_invalid"})


        def _add_days(value: Any, days: int) -> str:
            return (_parse_date(value or _date_text(), "date") + timedelta(days=int(days))).date().isoformat()


        def _month_value(raw_value: Any) -> str:
            value = str(raw_value or "").strip()
            if not re.fullmatch(r"20[0-9]{2}-(0[1-9]|1[0-2])", value):
                raise HTTPException(422, {"code": "validation_error", "message": "month_invalid"})
            return value


        def _equipment_type(type_id: int) -> dict[str, Any]:
            item = EQUIPMENT_TYPES.get(type_id)
            if not item:
                raise HTTPException(422, {"code": "validation_error", "message": "equipment_type_required"})
            return item


        def _equipment_public(item: dict[str, Any]) -> dict[str, Any]:
            payload = dict(item)
            payload["tipo"] = EQUIPMENT_TYPES.get(int(item.get("tipo_id", 0)), {}).get("nombre", "")
            payload["revision_vencida"] = str(item.get("proxima_revision", ""))[:10] < _date_text() and item.get("estado") != "descartado"
            payload["movements"] = [movement for movement in EQUIPMENT_MOVEMENTS.values() if movement.get("equipment_id") == item["id"]]
            return payload


        def _equipment_or_404(item_id: int) -> dict[str, Any]:
            item = EQUIPMENT.get(item_id)
            if not item:
                raise HTTPException(404, {"code": "not_found", "message": "equipment_not_found"})
            return item


        def _expense_or_404(item_id: int) -> dict[str, Any]:
            item = OPERATIONAL_EXPENSES.get(item_id)
            if not item or item.get("deleted_at"):
                raise HTTPException(404, {"code": "not_found", "message": "expense_not_found"})
            return item


        def _expense_public(item: dict[str, Any]) -> dict[str, Any]:
            payload = dict(item)
            payload["categoria_nombre"] = EXPENSE_CATEGORIES.get(int(item.get("categoria_id", 0)), {}).get("nombre", "")
            return payload


        def _goal_actuals() -> dict[str, float]:
            kpis = HITO6_DASHBOARD_PAYLOAD().get("kpis", {})
            confirmed_sales = _confirmed_sales()
            revenue = float(kpis.get("monto_ventas", 0))
            margin = float(kpis.get("margen_bruto", 0))
            return {
                "litros_produccion": _round(float(kpis.get("litros_producidos", 0))),
                "monto_ventas": _round(revenue),
                "num_clientes": len({sale.get("cliente_id") for sale in confirmed_sales}),
                "margen_promedio_pct": _round((margin / revenue * 100) if revenue > 0 else 0),
            }


        def _goal_progress(goal: dict[str, Any]) -> dict[str, Any]:
            actual = _goal_actuals()
            progress = {}
            for key in ["litros_produccion", "monto_ventas", "num_clientes", "margen_promedio_pct"]:
                target = float(goal.get(key, 0) or 0)
                current = float(actual.get(key, 0) or 0)
                progress[key] = {
                    "target": _round(target),
                    "actual": _round(current),
                    "pct": _round(min((current / target * 100) if target > 0 else 0, 999)),
                }
            return progress


        def _backup_public(item: dict[str, Any]) -> dict[str, Any]:
            payload = dict(item)
            payload["external_write"] = False
            payload["deploy_executed"] = False
            return payload


        def _grant_hito7_permissions() -> None:
            ROLES["mantenimiento"] = {
                "id": 8,
                "nombre": "mantenimiento",
                "estado": "activo",
                "permissions": ["equipment.read", "equipment.create", "equipment.movement", "reports.read"],
            }
            ROLES["finanzas"] = {
                "id": 9,
                "nombre": "finanzas",
                "estado": "activo",
                "permissions": ["expenses.read", "expenses.create", "reports.read", "reports.export"],
            }
            _grant_permissions("produccion", {"equipment.read", "equipment.movement"})
            _grant_permissions("auditor", {"equipment.read", "expenses.read"})


        _grant_hito7_permissions()
        REPORT_TYPES["financiero"] = "Financiero"


        def _operational_alerts() -> list[dict[str, Any]]:
            alerts = HITO6_OPERATIONAL_ALERTS()
            today = _date_text()
            for item in EQUIPMENT.values():
                if item.get("estado") == "descartado":
                    continue
                next_revision = str(item.get("proxima_revision", ""))[:10]
                if next_revision and next_revision < today:
                    alerts.append(
                        {
                            "type": "equipo",
                            "severity": "warning",
                            "entity": "equipment",
                            "entity_id": item["id"],
                            "message": "equipment_review_overdue",
                            "current": next_revision,
                            "threshold": today,
                        }
                    )
            return alerts


        def _dashboard_payload(fecha_inicio: str | None = None, fecha_fin: str | None = None, bodega_id: int | None = None) -> dict[str, Any]:
            payload = HITO6_DASHBOARD_PAYLOAD(fecha_inicio, fecha_fin, bodega_id)
            expenses = [expense for expense in OPERATIONAL_EXPENSES.values() if not expense.get("deleted_at")]
            total_expenses = sum(float(expense.get("monto", 0)) for expense in expenses)
            revenue = float(payload["kpis"].get("monto_ventas", 0))
            gross_margin = float(payload["kpis"].get("margen_bruto", 0))
            payload["kpis"]["gastos_operativos"] = _round(total_expenses)
            payload["kpis"]["flujo_caja_operativo"] = _round(revenue - total_expenses)
            payload["kpis"]["margen_neto"] = _round(gross_margin - total_expenses)
            payload["kpis"]["equipos_revision_vencida"] = len([alert for alert in payload["alerts"] if alert.get("type") == "equipo"])
            payload["charts"]["gastos_por_categoria"] = _chart_from_pairs(
                [
                    (EXPENSE_CATEGORIES.get(int(expense.get("categoria_id", 0)), {}).get("nombre", "Sin categoria"), float(expense.get("monto", 0)))
                    for expense in expenses
                ]
            )
            current_month = _date_text()[:7]
            goal = MONTHLY_GOALS.get(current_month)
            payload["monthly_goal"] = {"month": current_month, "progress": _goal_progress(goal) if goal else {}}
            payload["hito7_scope_excluded"] = []
            payload["deployment_status"] = {
                "dockerized": True,
                "ec2_ready": True,
                "proxy_tls_prepared": True,
                "deploy_executed": False,
                "real_secrets_used": False,
            }
            return payload


        def _report_rows(report_type: str) -> list[dict[str, Any]]:
            if report_type == "financiero":
                expenses = [_expense_public(item) for item in OPERATIONAL_EXPENSES.values() if not item.get("deleted_at")]
                goals = [
                    {"month": month, **goal, "progress": _goal_progress(goal)}
                    for month, goal in sorted(MONTHLY_GOALS.items())
                ]
                return [
                    {"tipo": "gasto", **expense}
                    for expense in expenses
                ] + [
                    {"tipo": "meta", **goal}
                    for goal in goals
                ]
            return HITO6_REPORT_ROWS(report_type)


        @app.get("/api/v1/equipment")
        def list_equipment(estado: str | None = None, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "equipment.read")
            items = [_equipment_public(item) for item in EQUIPMENT.values() if not estado or item.get("estado") == estado]
            return ok({"types": list(EQUIPMENT_TYPES.values()), "equipment": items})


        @app.post("/api/v1/equipment")
        def create_equipment(request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "equipment.create")
            codigo = _required_text(body, "codigo")
            _ensure_unique(EQUIPMENT, "codigo", codigo)
            type_info = _equipment_type(int(body.get("tipo_id", body.get("equipment_type_id", 1))))
            state = str(body.get("estado", "operativo") or "operativo")
            if state not in EQUIPMENT_STATES:
                raise HTTPException(422, {"code": "validation_error", "message": "equipment_state_invalid"})
            last_review = _date_text(body.get("ultima_mantencion") or body.get("fecha_compra"))
            item_id = _next_hito7_id("equipment")
            item = _timestamps(
                {
                    "id": item_id,
                    "codigo": codigo,
                    "nombre": _required_text(body, "nombre"),
                    "tipo_id": type_info["id"],
                    "marca": _optional_text(body, "marca"),
                    "modelo": _optional_text(body, "modelo"),
                    "serie": _optional_text(body, "serie"),
                    "fecha_compra": _date_text(body.get("fecha_compra")),
                    "costo_adquisicion": _non_negative(body.get("costo_adquisicion", 0), "costo_adquisicion"),
                    "estado": state,
                    "ultima_mantencion": last_review,
                    "proxima_revision": _date_text(body.get("proxima_revision") or _add_days(last_review, int(type_info["intervalo_revision_dias"]))),
                    "responsable_id": user["id"],
                },
                creating=True,
            )
            EQUIPMENT[item_id] = item
            _audit(request, user["id"], "equipment_created", "equipment", item_id, "HITO-007")
            return ok(_equipment_public(item))


        @app.get("/api/v1/equipment/{id}")
        def get_equipment(id: int, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "equipment.read")
            return ok(_equipment_public(_equipment_or_404(id)))


        @app.put("/api/v1/equipment/{id}")
        def update_equipment(id: int, request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "equipment.create")
            item = _equipment_or_404(id)
            if "codigo" in body:
                codigo = _required_text(body, "codigo")
                _ensure_unique(EQUIPMENT, "codigo", codigo, id)
                item["codigo"] = codigo
            for field in ["nombre", "marca", "modelo", "serie"]:
                if field in body:
                    item[field] = _optional_text(body, field)
            if "tipo_id" in body or "equipment_type_id" in body:
                item["tipo_id"] = _equipment_type(int(body.get("tipo_id", body.get("equipment_type_id"))))["id"]
            if "estado" in body:
                state = str(body["estado"])
                if state not in EQUIPMENT_STATES:
                    raise HTTPException(422, {"code": "validation_error", "message": "equipment_state_invalid"})
                item["estado"] = state
            if "costo_adquisicion" in body:
                item["costo_adquisicion"] = _non_negative(body["costo_adquisicion"], "costo_adquisicion")
            if "ultima_mantencion" in body:
                item["ultima_mantencion"] = _date_text(body["ultima_mantencion"])
            if "proxima_revision" in body:
                item["proxima_revision"] = _date_text(body["proxima_revision"])
            _timestamps(item)
            _audit(request, user["id"], "equipment_updated", "equipment", id, "HITO-007")
            return ok(_equipment_public(item))


        @app.post("/api/v1/equipment/{id}/movements")
        def create_equipment_movement(id: int, request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "equipment.movement")
            item = _equipment_or_404(id)
            if item.get("estado") == "descartado":
                raise HTTPException(422, {"code": "state_conflict", "message": "discarded_equipment_rejects_movements"})
            movement_type = str(body.get("tipo_movimiento", body.get("tipo", ""))).strip()
            if movement_type not in {"mantencion", "revision", "traslado", "descarte", "reparacion"}:
                raise HTTPException(422, {"code": "validation_error", "message": "equipment_movement_type_invalid"})
            movement_id = _next_hito7_id("equipment_movement")
            movement = _timestamps(
                {
                    "id": movement_id,
                    "equipment_id": id,
                    "tipo_movimiento": movement_type,
                    "descripcion": _required_text(body, "descripcion"),
                    "costo": _non_negative(body.get("costo", 0), "costo"),
                    "fecha": _date_text(body.get("fecha")),
                    "responsable_id": user["id"],
                },
                creating=True,
            )
            EQUIPMENT_MOVEMENTS[movement_id] = movement
            if movement_type in {"mantencion", "revision", "reparacion"}:
                item["ultima_mantencion"] = movement["fecha"]
                item["proxima_revision"] = _add_days(movement["fecha"], int(_equipment_type(int(item["tipo_id"]))["intervalo_revision_dias"]))
                item["estado"] = "operativo"
            if movement_type == "descarte":
                item["estado"] = "descartado"
            _timestamps(item)
            _audit(request, user["id"], "equipment_movement_created", "equipment_movements", movement_id, movement_type)
            return ok({"equipment": _equipment_public(item), "movement": movement})


        @app.get("/api/v1/equipment/{id}/movements")
        def list_equipment_movements(id: int, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "equipment.read")
            _equipment_or_404(id)
            return ok([movement for movement in EQUIPMENT_MOVEMENTS.values() if movement.get("equipment_id") == id])


        @app.get("/api/v1/expenses")
        def list_expenses(user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "expenses.read")
            expenses = [_expense_public(item) for item in OPERATIONAL_EXPENSES.values() if not item.get("deleted_at")]
            total = _round(sum(float(item.get("monto", 0)) for item in expenses))
            return ok({"categories": list(EXPENSE_CATEGORIES.values()), "expenses": expenses, "total": total})


        @app.post("/api/v1/expenses")
        def create_expense(request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "expenses.create")
            category_id = int(body.get("categoria_id", body.get("category_id", 1)))
            if category_id not in EXPENSE_CATEGORIES:
                raise HTTPException(422, {"code": "validation_error", "message": "expense_category_required"})
            expense_id = _next_hito7_id("expense")
            item = _timestamps(
                {
                    "id": expense_id,
                    "concepto": _required_text(body, "concepto"),
                    "categoria_id": category_id,
                    "monto": _positive(body.get("monto"), "monto"),
                    "fecha": _date_text(body.get("fecha")),
                    "proveedor": _optional_text(body, "proveedor"),
                    "documento_referencia": _optional_text(body, "documento_referencia"),
                    "responsable_id": user["id"],
                    "deleted_at": None,
                },
                creating=True,
            )
            OPERATIONAL_EXPENSES[expense_id] = item
            _audit(request, user["id"], "expense_created", "operational_expenses", expense_id, "HITO-007")
            return ok(_expense_public(item))


        @app.put("/api/v1/expenses/{id}")
        def update_expense(id: int, request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "expenses.create")
            item = _expense_or_404(id)
            if "concepto" in body:
                item["concepto"] = _required_text(body, "concepto")
            if "categoria_id" in body or "category_id" in body:
                category_id = int(body.get("categoria_id", body.get("category_id")))
                if category_id not in EXPENSE_CATEGORIES:
                    raise HTTPException(422, {"code": "validation_error", "message": "expense_category_required"})
                item["categoria_id"] = category_id
            if "monto" in body:
                item["monto"] = _positive(body["monto"], "monto")
            for field in ["fecha", "proveedor", "documento_referencia"]:
                if field in body:
                    item[field] = _date_text(body[field]) if field == "fecha" else _optional_text(body, field)
            _timestamps(item)
            _audit(request, user["id"], "expense_updated", "operational_expenses", id, "HITO-007")
            return ok(_expense_public(item))


        @app.delete("/api/v1/expenses/{id}")
        def delete_expense(id: int, request: Request, user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "expenses.create")
            item = _expense_or_404(id)
            if item.get("documento_referencia"):
                raise HTTPException(422, {"code": "state_conflict", "message": "expense_with_document_not_deletable"})
            item["deleted_at"] = _iso()
            _audit(request, user["id"], "expense_deleted", "operational_expenses", id, "soft_delete")
            return ok({"status": "deleted", "id": id})


        @app.get("/api/v1/monthly-goals")
        def list_monthly_goals(user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "reports.read")
            return ok([
                {"month": month, **goal, "progress": _goal_progress(goal)}
                for month, goal in sorted(MONTHLY_GOALS.items())
            ])


        @app.put("/api/v1/monthly-goals/{month}")
        def upsert_monthly_goal(month: str, request: Request, body: dict[str, Any] = Body(...), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "admin.settings")
            month_key = _month_value(month)
            goal = _timestamps(
                {
                    "month": month_key,
                    "litros_produccion": _non_negative(body.get("litros_produccion", body.get("litros", 0)), "litros_produccion"),
                    "monto_ventas": _non_negative(body.get("monto_ventas", body.get("ventas", 0)), "monto_ventas"),
                    "num_clientes": int(_non_negative(body.get("num_clientes", body.get("clientes", 0)), "num_clientes")),
                    "margen_promedio_pct": _non_negative(body.get("margen_promedio_pct", body.get("margen", 0)), "margen_promedio_pct"),
                    "responsable_id": user["id"],
                },
                creating=month_key not in MONTHLY_GOALS,
            )
            MONTHLY_GOALS[month_key] = goal
            _audit(request, user["id"], "monthly_goal_upserted", "monthly_goals", None, month_key)
            return ok({"goal": goal, "progress": _goal_progress(goal)})


        @app.get("/api/v1/jobs")
        def list_jobs(user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "admin.settings")
            policy = job_policy()
            return ok({"policy": policy, "low_activity_backup_enabled": should_run("low_activity_backup")})


        @app.get("/api/v1/backups")
        def list_backups(user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "admin.settings")
            return ok({"backups": [_backup_public(item) for item in BACKUP_RUNS.values()], "policy": job_policy()})


        @app.post("/api/v1/backups")
        def create_backup(request: Request, body: dict[str, Any] = Body(default={}), user: dict[str, Any] = Depends(_current_user)):
            _ensure_permission(user, "admin.settings")
            if not should_run("low_activity_backup"):
                raise HTTPException(422, {"code": "state_conflict", "message": "backup_job_disabled"})
            backup_id = _next_hito7_id("backup")
            item = _timestamps(
                {
                    "id": backup_id,
                    "job": str(body.get("job", "low_activity_backup")),
                    "estado": "completado",
                    "archivo_url": f"local://sandbox/backups/brewmaster-{backup_id:04d}.sql.gz",
                    "retention_days": int(body.get("retention_days", 14)),
                    "restore_tested": False,
                    "external_write": False,
                    "deploy_executed": False,
                },
                creating=True,
            )
            BACKUP_RUNS[backup_id] = item
            _audit(request, user["id"], "backup_registered", "backups", backup_id, "local_sandbox_only")
            return ok(_backup_public(item))
        """
    ).strip()
    return hito6 + "\n\n" + close_block


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


def _rules_py(milestone_id: str | None = None) -> str:
    if (milestone_id or "").strip().upper() == "HITO-005":
        return _rules_py("HITO-004") + "\n\n" + dedent(
            """
            def line_profit(unit_price: float, unit_cost: float, quantity: float) -> float:
                ensure_positive(quantity, "quantity")
                ensure_non_negative(unit_price, "unit_price")
                ensure_non_negative(unit_cost, "unit_cost")
                return round((float(unit_price) - float(unit_cost)) * float(quantity), 4)


            def suggested_unit_price(base_price: float, discount_pct: float, quantity: float, dozen_price: float = 0) -> float:
                ensure_positive(quantity, "quantity")
                base = ensure_non_negative(base_price, "base_price")
                discount = ensure_non_negative(discount_pct, "discount_pct")
                if discount > 100:
                    raise ValueError("discount_pct_invalid")
                if quantity >= 12 and float(dozen_price or 0) > 0:
                    return round(ensure_non_negative(dozen_price, "dozen_price") / 12, 4)
                return round(base * (1 - discount / 100), 4)


            def purchase_order_state_after_receipt(requested: float, received: float) -> str:
                ensure_positive(requested, "requested")
                ensure_non_negative(received, "received")
                if received > requested:
                    raise ValueError("receipt_exceeds_pending")
                return "recibida" if received == requested else "parcialmente_recibida"
            """
        ).strip()
    if (milestone_id or "").strip().upper() == "HITO-004":
        return dedent(
            """
            from __future__ import annotations

            import hashlib
            import re
            from dataclasses import dataclass


            EMAIL_RE = re.compile(r"^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$")
            MIN_ALERT_INTERVAL_HOURS = 24
            MAX_EMAIL_ATTEMPTS = 5
            QUALITY_RESULTS = {"aprobado", "rechazado"}


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


            def ensure_positive(value: float, field: str) -> float:
                number = float(value)
                if number <= 0:
                    raise ValueError(f"{field}_must_be_greater_than_zero")
                return number


            def ensure_non_negative(value: float, field: str) -> float:
                number = float(value)
                if number < 0:
                    raise ValueError(f"{field}_must_be_greater_or_equal_zero")
                return number


            def available_stock(current_stock: float, active_reservations: float = 0) -> float:
                value = float(current_stock) - float(active_reservations)
                return value if value > 0 else 0


            def normalize_email_list(values: list[str] | str) -> list[str]:
                raw_values = values
                if isinstance(raw_values, str):
                    raw_values = [item.strip() for item in raw_values.split(",")]
                if not isinstance(raw_values, list):
                    raise ValueError("email_list_invalid")
                normalized: list[str] = []
                for value in raw_values:
                    email = str(value or "").strip().lower()
                    if not email:
                        continue
                    if not EMAIL_RE.match(email):
                        raise ValueError("email_invalid")
                    if email not in normalized:
                        normalized.append(email)
                return normalized


            def should_send_stock_alert(current_stock: float, minimum_stock: float, hours_since_last_alert: float | None) -> bool:
                current = float(current_stock)
                minimum = float(minimum_stock)
                if current <= 0:
                    return True
                if current >= minimum:
                    return False
                return hours_since_last_alert is None or hours_since_last_alert >= MIN_ALERT_INTERVAL_HOURS


            def validate_alert_configuration(enabled: bool, recipients: list[str] | str) -> list[str]:
                normalized = normalize_email_list(recipients)
                if enabled and not normalized:
                    raise ValueError("alert_recipients_required")
                return normalized


            def email_status_after_attempt(current_attempts: int, success: bool, max_attempts: int = MAX_EMAIL_ATTEMPTS) -> dict[str, object]:
                attempts = int(current_attempts) + 1
                if success:
                    return {"status": "sent", "attempts": attempts, "final_error": False}
                if attempts >= max_attempts:
                    return {"status": "failed", "attempts": attempts, "final_error": True}
                return {"status": "queued", "attempts": attempts, "final_error": False}


            def local_secret_marker(raw_secret: str, username: str) -> str:
                if not raw_secret:
                    raise ValueError("smtp_secret_required")
                digest = hashlib.sha256(f"{username}:{raw_secret}".encode("utf-8")).hexdigest()
                return f"local-encrypted:{digest}"


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


            def batch_supply_consumption(recipe_quantity: float, recipe_volume: float, produced_liters: float) -> float:
                ensure_positive(recipe_quantity, "recipe_quantity")
                ensure_positive(recipe_volume, "recipe_volume")
                ensure_positive(produced_liters, "produced_liters")
                return round(float(recipe_quantity) * float(produced_liters) / float(recipe_volume), 4)


            def validate_quality_result(result: str, rejection_reason: str = "") -> str:
                normalized = str(result or "").strip()
                if normalized not in QUALITY_RESULTS:
                    raise ValueError("quality_result_invalid")
                if normalized == "rechazado" and not str(rejection_reason or "").strip():
                    raise ValueError("quality_rejection_reason_required")
                return normalized


            def waste_total(quantity: float, unit_cost: float) -> float:
                return round(ensure_positive(quantity, "waste_quantity") * ensure_non_negative(unit_cost, "waste_unit_cost"), 4)
            """
        ).strip()
    if (milestone_id or "").strip().upper() == "HITO-003":
        return dedent(
            """
            from __future__ import annotations

            import hashlib
            import re


            EMAIL_RE = re.compile(r"^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$")
            MIN_ALERT_INTERVAL_HOURS = 24
            MAX_EMAIL_ATTEMPTS = 5


            def ensure_positive(value: float, field: str) -> float:
                number = float(value)
                if number <= 0:
                    raise ValueError(f"{field}_must_be_greater_than_zero")
                return number


            def ensure_non_negative(value: float, field: str) -> float:
                number = float(value)
                if number < 0:
                    raise ValueError(f"{field}_must_be_greater_or_equal_zero")
                return number


            def normalize_email_list(values: list[str] | str) -> list[str]:
                raw_values = values
                if isinstance(raw_values, str):
                    raw_values = [item.strip() for item in raw_values.split(",")]
                if not isinstance(raw_values, list):
                    raise ValueError("email_list_invalid")
                normalized: list[str] = []
                for value in raw_values:
                    email = str(value or "").strip().lower()
                    if not email:
                        continue
                    if not EMAIL_RE.match(email):
                        raise ValueError("email_invalid")
                    if email not in normalized:
                        normalized.append(email)
                return normalized


            def should_send_stock_alert(current_stock: float, minimum_stock: float, hours_since_last_alert: float | None) -> bool:
                current = float(current_stock)
                minimum = float(minimum_stock)
                if current <= 0:
                    return True
                if current >= minimum:
                    return False
                return hours_since_last_alert is None or hours_since_last_alert >= MIN_ALERT_INTERVAL_HOURS


            def validate_alert_configuration(enabled: bool, recipients: list[str] | str) -> list[str]:
                normalized = normalize_email_list(recipients)
                if enabled and not normalized:
                    raise ValueError("alert_recipients_required")
                return normalized


            def email_status_after_attempt(current_attempts: int, success: bool, max_attempts: int = MAX_EMAIL_ATTEMPTS) -> dict[str, object]:
                attempts = int(current_attempts) + 1
                if success:
                    return {"status": "sent", "attempts": attempts, "final_error": False}
                if attempts >= max_attempts:
                    return {"status": "failed", "attempts": attempts, "final_error": True}
                return {"status": "queued", "attempts": attempts, "final_error": False}


            def local_secret_marker(raw_secret: str, username: str) -> str:
                if not raw_secret:
                    raise ValueError("smtp_secret_required")
                digest = hashlib.sha256(f"{username}:{raw_secret}".encode("utf-8")).hexdigest()
                return f"local-encrypted:{digest}"
            """
        ).strip()
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


def _inventory_service_py(milestone_id: str | None = None) -> str:
    if (milestone_id or "").strip().upper() == "HITO-002":
        return dedent(
            """
            from __future__ import annotations

            from typing import Any


            ACTIVE_STATES = {"activo", "en_prueba"}


            def ensure_non_negative(value: float, field: str) -> float:
                number = float(value)
                if number < 0:
                    raise ValueError(f"{field}_must_be_non_negative")
                return number


            def ensure_positive(value: float, field: str) -> float:
                number = ensure_non_negative(value, field)
                if number <= 0:
                    raise ValueError(f"{field}_must_be_positive")
                return number


            def ensure_active(record: dict[str, Any], label: str) -> dict[str, Any]:
                if record.get("estado") not in ACTIVE_STATES:
                    raise ValueError(f"{label}_inactive")
                return record


            def recipe_estimated_cost(ingredients: list[dict[str, float]]) -> float:
                if not ingredients:
                    raise ValueError("recipe_ingredients_required")
                total = 0.0
                for ingredient in ingredients:
                    quantity = ensure_positive(float(ingredient["cantidad"]), "ingredient_quantity")
                    unit_cost = ensure_non_negative(float(ingredient["costo_unitario"]), "ingredient_unit_cost")
                    total += quantity * unit_cost
                return round(total, 4)


            def can_inactivate_supply(supply_id: int, recipes: list[dict[str, Any]]) -> bool:
                for recipe in recipes:
                    if recipe.get("estado") not in ACTIVE_STATES:
                        continue
                    if any(int(item.get("supply_id", 0)) == supply_id for item in recipe.get("ingredientes", [])):
                        return False
                return True
            """
        ).strip()
    if (milestone_id or "").strip().upper() == "HITO-003":
        return dedent(
            """
            from __future__ import annotations

            from typing import Any

            from app.domain.rules import ensure_non_negative, ensure_positive, should_send_stock_alert


            ACTIVE_STATES = {"activo", "en_prueba"}


            def ensure_active(record: dict[str, Any], label: str) -> dict[str, Any]:
                if record.get("estado") not in ACTIVE_STATES:
                    raise ValueError(f"{label}_inactive")
                return record


            def recipe_estimated_cost(ingredients: list[dict[str, float]]) -> float:
                if not ingredients:
                    raise ValueError("recipe_ingredients_required")
                total = 0.0
                for ingredient in ingredients:
                    quantity = ensure_positive(float(ingredient["cantidad"]), "ingredient_quantity")
                    unit_cost = ensure_non_negative(float(ingredient["costo_unitario"]), "ingredient_unit_cost")
                    total += quantity * unit_cost
                return round(total, 4)


            def can_inactivate_supply(supply_id: int, recipes: list[dict[str, Any]]) -> bool:
                for recipe in recipes:
                    if recipe.get("estado") not in ACTIVE_STATES:
                        continue
                    if any(int(item.get("supply_id", 0)) == supply_id for item in recipe.get("ingredientes", [])):
                        return False
                return True


            def register_supply_entry(stock: float, quantity: float, unit_cost: float, minimum_stock: float, hours_since_last_alert: float | None) -> dict[str, object]:
                current_stock = ensure_non_negative(stock, "stock")
                entry_quantity = ensure_positive(quantity, "quantity")
                cost = ensure_non_negative(unit_cost, "unit_cost")
                resulting_stock = round(current_stock + entry_quantity, 4)
                alert_needed = should_send_stock_alert(resulting_stock, minimum_stock, hours_since_last_alert)
                recovered = resulting_stock >= float(minimum_stock)
                return {
                    "stock_actual": resulting_stock,
                    "movement": "ENTRADA",
                    "cantidad": entry_quantity,
                    "costo_unitario": cost,
                    "saldo_resultante": resulting_stock,
                    "alert_needed": alert_needed,
                    "reset_last_alert": recovered,
                }


            def low_stock_items(supplies: list[dict[str, Any]]) -> list[dict[str, Any]]:
                return [
                    supply
                    for supply in supplies
                    if supply.get("estado") == "activo"
                    and float(supply.get("stock_actual", 0)) < float(supply.get("stock_minimo", 0))
                ]
            """
        ).strip()
    if (milestone_id or "").strip().upper() == "HITO-005":
        return _inventory_service_py("HITO-003") + "\n\n" + dedent(
            """
            def reserve_stock(current_stock: float, active_reservations: float, quantity: float) -> dict[str, float | str]:
                requested = ensure_positive(quantity, "quantity")
                free_stock = max(float(current_stock) - float(active_reservations), 0)
                if requested > free_stock:
                    raise ValueError("stock_unavailable")
                return {"reserved": requested, "available_after": round(free_stock - requested, 4), "status": "activa"}
            """
        ).strip()
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


def _production_service_py(milestone_id: str | None = None) -> str:
    if (milestone_id or "").strip().upper() in {"HITO-004", "HITO-005"}:
        return dedent(
            """
            from __future__ import annotations

            from typing import Any

            from app.domain.rules import (
                CostInput,
                batch_cost,
                batch_supply_consumption,
                ensure_non_negative,
                ensure_positive,
                validate_quality_result,
                waste_total,
            )


            def planned_consumption(recipe: dict[str, Any], produced_liters: float) -> list[dict[str, float | int | str]]:
                recipe_volume = ensure_positive(recipe["volumen_por_lote"], "recipe_volume")
                items: list[dict[str, float | int | str]] = []
                for ingredient in recipe.get("ingredientes", []):
                    quantity = batch_supply_consumption(float(ingredient["cantidad"]), recipe_volume, produced_liters)
                    items.append(
                        {
                            "supply_id": int(ingredient["supply_id"]),
                            "nombre_insumo": str(ingredient.get("nombre_insumo", "")),
                            "cantidad_usada": quantity,
                            "costo_unitario": ensure_non_negative(float(ingredient.get("costo_unitario", 0)), "costo_unitario"),
                        }
                    )
                return items


            def stock_failures(requirements: list[dict[str, Any]], current_stock: dict[int, float]) -> list[dict[str, float | int]]:
                failures: list[dict[str, float | int]] = []
                for item in requirements:
                    supply_id = int(item["supply_id"])
                    required = float(item["cantidad_usada"])
                    available = float(current_stock.get(supply_id, 0))
                    if required > available:
                        failures.append({"supply_id": supply_id, "required": required, "available": available})
                return failures


            def complete_batch(cost_input: CostInput, stock_ok: bool) -> dict[str, object]:
                if not stock_ok:
                    raise ValueError("stock_unavailable")
                ensure_positive(cost_input.produced_liters, "produced_liters")
                return {"state": "completado", "cost": batch_cost(cost_input), "kardex": "SALIDA_PRODUCCION"}


            def quality_payload(result: str, rejection_reason: str = "") -> dict[str, str]:
                return {"resultado": validate_quality_result(result, rejection_reason), "motivo_rechazo": rejection_reason}


            def waste_payload(entity_type: str, quantity: float, unit_cost: float, reason: str) -> dict[str, object]:
                if entity_type not in {"insumo", "producto"}:
                    raise ValueError("waste_entity_invalid")
                if not reason.strip():
                    raise ValueError("waste_reason_required")
                return {
                    "tipo_entidad": entity_type,
                    "cantidad_perdida": ensure_positive(quantity, "waste_quantity"),
                    "costo_total": waste_total(quantity, unit_cost),
                    "motivo_detallado": reason.strip(),
                    "movement": "MERMA",
                }
            """
        ).strip()
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
        from app.domain.rules import available_stock, ensure_non_negative, ensure_positive, line_profit, suggested_unit_price


        def confirm_sale(current_stock: float, active_reservations: float, quantity: float, unit_price: float, unit_cost: float) -> dict[str, float | str]:
            ensure_positive(quantity, "quantity")
            if quantity > available_stock(current_stock, active_reservations):
                raise ValueError("stock_unavailable")
            return {"movement": "VENTA", "remaining_stock": current_stock - quantity, "profit": line_profit(unit_price, unit_cost, quantity)}


        def price_for_customer_type(base_price: float, discount_pct: float, quantity: float, dozen_price: float = 0) -> dict[str, float | str]:
            price = suggested_unit_price(base_price, discount_pct, quantity, dozen_price)
            warning = "price_zero" if price == 0 else ""
            return {"precio_unitario": price, "warning": warning}


        def release_reservation(quantity: float) -> dict[str, float | str]:
            return {"released": ensure_positive(quantity, "quantity"), "status": "liberada"}


        def consume_reservation(quantity: float, unit_price: float, unit_cost: float) -> dict[str, float | str]:
            qty = ensure_positive(quantity, "quantity")
            price = ensure_non_negative(unit_price, "unit_price")
            cost = ensure_non_negative(unit_cost, "unit_cost")
            return {"consumed": qty, "status": "consumida", "profit": line_profit(price, cost, qty)}
        """
    ).strip()


def _purchasing_service_py() -> str:
    return dedent(
        """
        from app.domain.rules import ensure_non_negative, ensure_positive, purchase_order_state_after_receipt


        def receive_order(requested: float, already_received: float, incoming: float, allow_over_receive: bool = False) -> dict[str, float | str]:
            ensure_positive(incoming, "incoming")
            pending = requested - already_received
            if incoming > pending and not allow_over_receive:
                raise ValueError("state_conflict")
            new_received = already_received + incoming
            status = "recibida" if new_received >= requested else "parcialmente_recibida"
            return {"cantidad_recibida": new_received, "estado": status, "movement": "ENTRADA"}


        def order_line_total(quantity: float, unit_price: float) -> float:
            return round(ensure_positive(quantity, "quantity") * ensure_non_negative(unit_price, "unit_price"), 4)


        def editable_order_state(state: str) -> bool:
            return state == "borrador"


        def receipt_state(requested: float, received: float) -> str:
            return purchase_order_state_after_receipt(requested, received)
        """
    ).strip()


def _notifications_service_py(milestone_id: str | None = None) -> str:
    if (milestone_id or "").strip().upper() == "HITO-003":
        return dedent(
            """
            from __future__ import annotations

            from dataclasses import dataclass
            from datetime import datetime, timezone
            from typing import Any

            from app.domain.rules import email_status_after_attempt, normalize_email_list, should_send_stock_alert


            @dataclass
            class MockEmailSender:
                failures_before_success: int = 0
                attempts: int = 0

                def send(self, recipients: list[str], subject: str, body_html: str) -> bool:
                    if not recipients:
                        raise ValueError("recipients_required")
                    self.attempts += 1
                    return self.attempts > self.failures_before_success


            def now_iso() -> str:
                return datetime.now(timezone.utc).isoformat()


            def build_stock_alert(supply: dict[str, Any], hours_since_last_alert: float | None) -> dict[str, Any] | None:
                if not supply.get("enable_email_alerts"):
                    return None
                recipients = normalize_email_list(supply.get("alert_emails", []))
                if not recipients:
                    raise ValueError("alert_recipients_required")
                if not should_send_stock_alert(float(supply.get("stock_actual", 0)), float(supply.get("stock_minimo", 0)), hours_since_last_alert):
                    return None
                return {
                    "supply_id": supply["id"],
                    "recipients": recipients,
                    "subject": f"Stock bajo: {supply['nombre']}",
                    "body_html": f"<p>{supply['nombre']} bajo minimo configurado.</p>",
                    "status": "queued",
                    "attempts": 0,
                    "sent_at": None,
                    "error_message": "",
                    "final_error": False,
                }


            def process_notification(notification: dict[str, Any], sender: MockEmailSender, max_attempts: int = 5) -> dict[str, Any]:
                if notification.get("status") == "sent" or notification.get("final_error"):
                    return notification
                try:
                    success = sender.send(
                        list(notification.get("recipients", [])),
                        str(notification.get("subject", "")),
                        str(notification.get("body_html", "")),
                    )
                    status = email_status_after_attempt(int(notification.get("attempts", 0)), success, max_attempts)
                    notification.update(status)
                    notification["error_message"] = "" if success else "mock_smtp_error"
                    notification["sent_at"] = now_iso() if success else None
                    notification["updated_at"] = now_iso()
                    return notification
                except Exception as exc:
                    status = email_status_after_attempt(int(notification.get("attempts", 0)), False, max_attempts)
                    notification.update(status)
                    notification["error_message"] = str(exc)
                    notification["updated_at"] = now_iso()
                    return notification
            """
        ).strip()
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


def _scheduler_py(milestone_id: str | None = None) -> str:
    if (milestone_id or "").strip().upper() == "HITO-006":
        return dedent(
            """
            JOBS = [
                "stock_alerts",
                "email_retries",
                "reservation_expiration",
                "deferred_exports",
            ]


            def job_policy() -> dict[str, object]:
                return {
                    "scheduler": "APScheduler",
                    "jobs": JOBS,
                    "idempotent": True,
                    "blocking_main_flow": False,
                    "external_integrations": False,
                    "backup_jobs": False,
                }


            def should_run(job_name: str) -> bool:
                return job_name in JOBS
            """
        ).strip()
    if (milestone_id or "").strip().upper() in {"HITO-007", "HITO-008"}:
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
                return {
                    "scheduler": "APScheduler",
                    "jobs": JOBS,
                    "idempotent": True,
                    "blocking_main_flow": False,
                    "external_integrations": False,
                    "backup_jobs": True,
                    "backup_mode": "local_sandbox_metadata_only",
                    "deploy_executed": False,
                }


            def should_run(job_name: str) -> bool:
                return job_name in JOBS
            """
        ).strip()
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
            return {
                "scheduler": "APScheduler",
                "jobs": JOBS,
                "idempotent": True,
                "blocking_main_flow": False,
                "external_integrations": False,
                "backup_jobs": True,
            }


        def should_run(job_name: str) -> bool:
            return job_name in JOBS
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
