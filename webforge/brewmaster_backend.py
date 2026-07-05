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
        SENSITIVE_PERMISSIONS = {"costs:read", "financial:read", "smtp:update", "users:write"}


        def require_permission(user_permissions: set[str], required: str) -> None:
            if "*" in user_permissions or required in user_permissions:
                return
            raise PermissionError("permission_denied")


        def can_view_costs(user_permissions: set[str]) -> bool:
            return "*" in user_permissions or "costs:read" in user_permissions or "financial:read" in user_permissions
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
