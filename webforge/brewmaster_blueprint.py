from __future__ import annotations

from typing import Any

from .brewmaster_spec import load_brewmaster_spec

HITO_001_ENTITY_NAMES = {
    "users",
    "roles",
    "permissions",
    "role_permissions",
    "audit_logs",
    "settings",
    "password_reset_tokens",
}
HITO_001_SCREEN_IDS = {"P-01", "P-02", "P-30"}
HITO_001_VALIDATION_IDS = {f"V{index:03d}" for index in range(1, 25)}
HITO_001_PERMISSION_CODES = {"admin.users", "audit.read"}
HITO_001_ENDPOINTS: list[dict[str, Any]] = [
    {
        "api_id": "API-001",
        "method": "POST",
        "path": "/api/v1/auth/login",
        "handler": "auth.login",
        "description": "iniciar sesion, retorna token JWT.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": True,
    },
    {
        "api_id": "API-002",
        "method": "POST",
        "path": "/api/v1/auth/logout",
        "handler": "auth.logout",
        "description": "cerrar sesion autenticada y auditar salida.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": True,
    },
    {
        "api_id": "API-003",
        "method": "GET",
        "path": "/api/v1/auth/me",
        "handler": "auth.me",
        "description": "obtener usuario autenticado.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": False,
        "action_endpoint": True,
    },
    {
        "api_id": "API-004",
        "method": "POST",
        "path": "/api/v1/auth/change-password",
        "handler": "auth.change_password",
        "description": "cambiar contrasena validando la actual.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": True,
    },
    {
        "api_id": "API-005",
        "method": "GET",
        "path": "/api/v1/users",
        "handler": "users.list",
        "description": "listar usuarios con filtros por rol y estado.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-006",
        "method": "POST",
        "path": "/api/v1/users",
        "handler": "users.create",
        "description": "crear usuario con rol activo, solo admin.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": False,
    },
    {
        "api_id": "API-007",
        "method": "GET",
        "path": "/api/v1/users/{id}",
        "handler": "users.detail",
        "description": "obtener detalle de usuario.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-008",
        "method": "PUT",
        "path": "/api/v1/users/{id}",
        "handler": "users.update",
        "description": "editar usuario y auditar cambio critico.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": False,
    },
    {
        "api_id": "API-009",
        "method": "PATCH",
        "path": "/api/v1/users/{id}/toggle-status",
        "handler": "users.toggle_status",
        "description": "activar o desactivar usuario.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": True,
    },
    {
        "api_id": "API-082",
        "method": "GET",
        "path": "/api/v1/audit-logs",
        "handler": "audit_logs.list",
        "description": "consultar auditoria funcional con permiso audit.read.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-085",
        "method": "POST",
        "path": "/api/v1/auth/password-reset/request",
        "handler": "auth.password_reset_request",
        "description": "solicitar restablecimiento sin filtrar existencia de usuario.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": True,
    },
    {
        "api_id": "API-086",
        "method": "POST",
        "path": "/api/v1/auth/password-reset/confirm",
        "handler": "auth.password_reset_confirm",
        "description": "confirmar token valido y guardar hash nuevo.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": True,
    },
]


def _is_hito_001(milestone_id: str | None) -> bool:
    normalized = (milestone_id or "").strip().upper()
    return normalized in {"HITO-001", "HITO-1", "1"}


def _hito_001_blueprint() -> dict[str, Any]:
    spec = load_brewmaster_spec()
    screen_overrides = {
        "P-30": {
            "id": "P-30",
            "name": "Configuracion de usuarios, roles y auditoria",
            "module": "Configuracion",
            "route": "/settings/security",
        }
    }
    screens = [
        screen_overrides.get(screen["id"], screen)
        for screen in spec.screens
        if screen["id"] in HITO_001_SCREEN_IDS
    ]
    entities = [entity for entity in spec.entities if entity["name"] in HITO_001_ENTITY_NAMES]
    validations = [item for item in spec.validations if item["id"] in HITO_001_VALIDATION_IDS]
    permissions = [permission for permission in spec.permissions if permission in HITO_001_PERMISSION_CODES]
    return {
        "blueprint_id": "brewmaster.sdd.hito1.v1",
        "milestone_id": "HITO-001",
        "milestone_name": "Fundamentos",
        "source_spec": spec.source_path,
        "scope": {
            "source": "J.12 Hito 1",
            "includes": [
                "Auth JWT",
                "usuarios",
                "roles",
                "permisos",
                "auditoria",
                "estructura base del proyecto",
            ],
            "deferred_milestones": ["HITO-002", "HITO-003", "HITO-004", "HITO-005", "HITO-006", "HITO-007"],
            "deferred_modules": [
                "proveedores",
                "insumos",
                "bodegas",
                "recetas",
                "inventario",
                "produccion",
                "ventas",
                "compras",
                "dashboard",
                "finanzas",
                "alertas SMTP",
            ],
        },
        "spec_model": {
            "parsed": spec.parsed,
            "use_case_count": 2,
            "business_rule_count": 10,
            "validation_count": len(validations),
            "permission_count": len(permissions),
            "non_functional_count": len(spec.non_functional),
        },
        "architecture_source": "fabricas_agentes_ia.md",
        "stack": {
            "frontend": "React + Bootstrap",
            "backend": "Python 3 + FastAPI",
            "orm": "SQLAlchemy + Alembic contract",
            "database": "MySQL or MariaDB",
            "auth": "JWT with expiring local HS256 tokens",
        },
        "factory_controls": {
            "entrypoint": "harness.run_agent(agent_id, state)",
            "side_effects": "all generated implementation files pass through DEV sandbox materializer",
            "context": "authorized specification and architecture sources only",
            "memory": "project scoped propose-only memory",
            "gates": ["schema", "budget", "project_isolation", "frontend_template", "sandbox", "tests", "security", "coverage"],
            "determinism": "local deterministic generation, no external cost",
        },
        "modules": [
            {
                "id": "MOD-001",
                "name": "Seguridad, usuarios y auditoria",
                "use_cases": ["CU-001", "CU-031"],
                "screens": ["P-01", "P-02", "P-30"],
                "entities": sorted(HITO_001_ENTITY_NAMES),
                "acceptance": "login JWT, recuperacion de contrasena, CRUD usuarios, RBAC y auditoria funcional",
            }
        ],
        "screens": screens,
        "entities": [entity["name"] for entity in entities],
        "entity_models": entities,
        "endpoints": HITO_001_ENDPOINTS,
        "validations": validations,
        "permissions": permissions,
        "business_rules": [
            item
            for item in spec.business_rules
            if item["id"] in {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 60}
        ],
        "transactional_rules": [
            "login_success_returns_expiring_jwt_and_failed_login_is_audited",
            "protected_endpoint_requires_active_user_and_role_permission",
            "user_create_update_toggle_are_admin_only_and_audited",
            "password_change_requires_current_password_and_stores_hash",
            "password_reset_token_is_single_use_expiring_and_audited",
            "audit_log_read_is_limited_to_admin_or_auditor",
        ],
        "non_functional": {
            "source_requirements": spec.non_functional,
            "security": ["password hash", "expiring JWT", "RBAC on protected Hito 1 endpoints"],
            "audit": "critical Hito 1 writes include actor, date, entity, action and IP",
            "observability": ["request_id", "user_id", "module", "structured audit events"],
            "privacy": ["password hashes only", "reset token stored hashed"],
        },
    }


def brewmaster_blueprint(milestone_id: str | None = None) -> dict[str, Any]:
    if _is_hito_001(milestone_id):
        return _hito_001_blueprint()
    spec = load_brewmaster_spec()
    endpoints = spec.endpoints
    entity_models = spec.entities
    entities = [entity["name"] for entity in entity_models]
    return {
        "blueprint_id": "brewmaster.sdd.mvp.v1",
        "source_spec": spec.source_path,
        "spec_model": {
            "parsed": spec.parsed,
            "use_case_count": len(spec.use_cases),
            "business_rule_count": len(spec.business_rules),
            "validation_count": len(spec.validations),
            "permission_count": len(spec.permissions),
            "non_functional_count": len(spec.non_functional),
        },
        "architecture_source": "fabricas_agentes_ia.md",
        "stack": {
            "frontend": "React + Bootstrap",
            "backend": "Python 3 + FastAPI",
            "orm": "SQLAlchemy + Alembic",
            "database": "MySQL or MariaDB",
            "jobs": "APScheduler",
            "auth": "JWT with refresh token",
            "reports": ["CSV", "XLSX", "PDF"],
        },
        "factory_controls": {
            "entrypoint": "harness.run_agent(agent_id, state)",
            "side_effects": "all generated implementation files pass through DEV sandbox materializer",
            "context": "authorized specification and architecture sources only",
            "memory": "project scoped propose-only memory",
            "gates": ["schema", "budget", "project_isolation", "frontend_template", "sandbox", "tests", "security", "coverage"],
            "determinism": "local deterministic generation, no external cost",
        },
        "modules": spec.modules,
        "screens": spec.screens,
        "entities": entities,
        "entity_models": entity_models,
        "endpoints": endpoints,
        "validations": spec.validations,
        "permissions": spec.permissions,
        "business_rules": spec.business_rules,
        "transactional_rules": [
            "complete_batch_validates_stock_consumes_supplies_creates_finished_product_and_calculates_cost_atomically",
            "supply_entry_updates_stock_and_kardex_atomically",
            "sale_validates_available_stock_decrements_inventory_and_writes_kardex_atomically",
            "purchase_order_receive_generates_supply_entry_and_updates_order_atomically",
            "reservation_uses_current_stock_minus_active_reservations",
            "waste_record_decrements_inventory_and_writes_kardex_atomically",
            "email_alerts_are_enqueued_and_retried_asynchronously",
            "state_change_actions_are_idempotent_or_reject_current_state_conflict",
        ],
        "non_functional": {
            "source_requirements": spec.non_functional,
            "security": ["bcrypt", "expiring JWT", "RBAC on every endpoint"],
            "audit": "100 percent critical writes include actor, date, entity, action and IP",
            "performance": ["paginated listings", "SQL aggregations for dashboard", "background heavy exports"],
            "observability": ["request_id", "user_id", "module", "latency", "structured logs"],
            "privacy": ["financial data hidden without permission", "SMTP credential encrypted at rest"],
        },
    }

def brewmaster_coverage(milestone_id: str | None = None) -> dict[str, Any]:
    blueprint = brewmaster_blueprint(milestone_id)
    modules = blueprint["modules"]
    screens = blueprint["screens"]
    endpoints = blueprint["endpoints"]
    entities = blueprint["entities"]
    validations = blueprint.get("validations", [])
    if blueprint.get("milestone_id") == "HITO-001":
        endpoint_paths = {endpoint["path"] for endpoint in endpoints}
        acceptance_gate = {
            "is_hito_001_scope": blueprint.get("milestone_id") == "HITO-001",
            "has_only_foundation_module": {module["id"] for module in modules} == {"MOD-001"},
            "has_foundation_screens": {screen["id"] for screen in screens} == HITO_001_SCREEN_IDS,
            "has_hito1_endpoints": endpoint_paths
            == {endpoint["path"] for endpoint in HITO_001_ENDPOINTS},
            "has_api_v1": all(endpoint["path"].startswith("/api/v1") for endpoint in endpoints),
            "has_security_entities": set(entities) == HITO_001_ENTITY_NAMES,
            "has_v001_v024": {item["id"] for item in validations} == HITO_001_VALIDATION_IDS,
            "has_hito1_permissions": set(blueprint.get("permissions", [])) == HITO_001_PERMISSION_CODES,
            "defers_future_modules": bool(blueprint.get("scope", {}).get("deferred_milestones")),
            "no_future_endpoint_paths": not any(
                fragment in path
                for path in endpoint_paths
                for fragment in [
                    "/suppliers",
                    "/supplies",
                    "/recipes",
                    "/batches",
                    "/products",
                    "/sales",
                    "/customers",
                    "/purchase-orders",
                    "/equipment",
                    "/expenses",
                    "/reports/export",
                    "/settings/smtp",
                    "/monthly-goals",
                ]
            ),
        }
        return {
            "status": "pass" if all(acceptance_gate.values()) else "partial",
            "milestone_id": "HITO-001",
            "module_count": len(modules),
            "screen_count": len(screens),
            "endpoint_count": len(endpoints),
            "entity_count": len(entities),
            "validation_count": len(validations),
            "permission_count": len(blueprint.get("permissions", [])),
            "critical_transaction_count": len(blueprint["transactional_rules"]),
            "module_coverage": {module["id"]: module["acceptance"] for module in modules},
            "screen_ids": [screen["id"] for screen in screens],
            "action_endpoints": [endpoint for endpoint in endpoints if endpoint.get("action_endpoint")],
            "acceptance_gate": acceptance_gate,
        }
    return {
        "status": "pass"
        if len(screens) == 30 and len(endpoints) == 40 and len(validations) == 100
        else "partial",
        "module_count": len(modules),
        "screen_count": len(screens),
        "endpoint_count": len(endpoints),
        "entity_count": len(entities),
        "validation_count": len(validations),
        "permission_count": len(blueprint.get("permissions", [])),
        "critical_transaction_count": len(blueprint["transactional_rules"]),
        "module_coverage": {module["id"]: module["acceptance"] for module in modules},
        "screen_ids": [screen["id"] for screen in screens],
        "action_endpoints": [endpoint for endpoint in endpoints if endpoint.get("action_endpoint")],
        "acceptance_gate": {
            "has_30_screens": len(screens) == 30,
            "has_40_spec_endpoints": len(endpoints) == 40,
            "has_v001_v100": len(validations) == 100 and {item["id"] for item in validations} == {f"V{index:03d}" for index in range(1, 101)},
            "has_all_macro_requirements": {module["id"] for module in modules}
            >= {"REQ-INS", "REQ-REC", "REQ-PROD", "REQ-PRO", "REQ-VTA", "REQ-COM", "REQ-EQU", "REQ-FIN", "REQ-REP", "REQ-ALT"},
            "has_api_v1": all(endpoint["path"].startswith("/api/v1") for endpoint in endpoints),
            "has_transactional_rules": len(blueprint["transactional_rules"]) >= 8,
        },
    }
