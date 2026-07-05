from __future__ import annotations

from .brewmaster_backend import (
    _alembic_env_py,
    _backend_main,
    _backend_pyproject,
    _catalog_py,
    _inventory_service_py,
    _migration_py,
    _models_py,
    _notifications_service_py,
    _production_service_py,
    _purchasing_service_py,
    _responses_py,
    _rules_py,
    _sales_service_py,
    _scheduler_py,
    _security_py,
    _session_py,
)
from .brewmaster_blueprint import brewmaster_blueprint, brewmaster_coverage
from .brewmaster_docs import (
    _api_contract_md,
    _architecture_md,
    _json,
    _permissions,
    _readme,
    _test_strategy_md,
    _traceability_md,
)
from .brewmaster_frontend import _app_jsx, _client_js, _frontend_package_json, _routes_js, _screens_js
from .brewmaster_tests import _test_auth_foundation_py, _test_contracts_py, _test_domain_rules_py

def brewmaster_bundle(milestone_id: str | None = None) -> list[dict[str, str]]:
    blueprint = brewmaster_blueprint(milestone_id)
    coverage = brewmaster_coverage(milestone_id)
    is_hito_001 = blueprint.get("milestone_id") == "HITO-001"
    files = {
        "README.md": _readme(blueprint),
        "docs/architecture.md": _architecture_md(blueprint),
        "docs/api-contract.md": _api_contract_md(blueprint),
        "docs/traceability.md": _traceability_md(blueprint),
        "docs/test-strategy.md": _test_strategy_md(blueprint),
        "contracts/brewmaster-blueprint.json": _json(blueprint),
        "contracts/coverage.json": _json(coverage),
        "contracts/permissions.json": _json(_permissions(blueprint)),
        "contracts/domain-model.json": _json({"entities": blueprint["entities"], "modules": blueprint["modules"]}),
        "backend/pyproject.toml": _backend_pyproject(),
        "backend/app/main.py": _backend_main(blueprint),
        "backend/app/core/responses.py": _responses_py(),
        "backend/app/core/security.py": _security_py(),
        "backend/app/domain/catalog.py": _catalog_py(blueprint),
        "backend/app/db/models.py": _models_py(blueprint),
        "backend/app/db/session.py": _session_py(),
        "backend/alembic/env.py": _alembic_env_py(),
        "backend/alembic/versions/0001_brewmaster_schema.py": _migration_py(blueprint),
        "frontend/package.json": _frontend_package_json(),
        "frontend/src/App.jsx": _app_jsx(blueprint),
        "frontend/src/api/client.js": _client_js(),
        "frontend/src/routes.js": _routes_js(),
        "frontend/src/screens/catalog.js": _screens_js(blueprint),
        "tests/test_contracts.py": _test_contracts_py(blueprint),
    }
    if is_hito_001:
        files["tests/test_auth_foundation.py"] = _test_auth_foundation_py()
    else:
        files.update(
            {
                "backend/app/domain/rules.py": _rules_py(),
                "backend/app/services/inventory.py": _inventory_service_py(),
                "backend/app/services/production.py": _production_service_py(),
                "backend/app/services/sales.py": _sales_service_py(),
                "backend/app/services/purchasing.py": _purchasing_service_py(),
                "backend/app/services/notifications.py": _notifications_service_py(),
                "backend/app/jobs/scheduler.py": _scheduler_py(),
                "tests/test_domain_rules.py": _test_domain_rules_py(),
            }
        )
    return [{"path": path, "content": content} for path, content in files.items()]
