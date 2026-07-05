from __future__ import annotations

from typing import Any

from .brewmaster_spec import load_brewmaster_spec

def brewmaster_blueprint() -> dict[str, Any]:
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

def brewmaster_coverage() -> dict[str, Any]:
    blueprint = brewmaster_blueprint()
    modules = blueprint["modules"]
    screens = blueprint["screens"]
    endpoints = blueprint["endpoints"]
    entities = blueprint["entities"]
    validations = blueprint.get("validations", [])
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
