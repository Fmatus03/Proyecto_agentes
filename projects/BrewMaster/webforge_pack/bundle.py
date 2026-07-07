from __future__ import annotations

from .backend import (
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
from .blueprint import brewmaster_blueprint, brewmaster_coverage
from .docs import (
    _api_contract_md,
    _architecture_md,
    _backend_dockerfile,
    _deployment_md,
    _docker_compose_yml,
    _env_example,
    _frontend_dockerfile,
    _json,
    _nginx_conf,
    _permissions,
    _readme,
    _test_strategy_md,
    _traceability_md,
)
from .frontend import _app_jsx, _client_js, _frontend_package_json, _index_html, _main_jsx, _routes_js, _screen_views_jsx, _screens_js
from .tests import _test_auth_foundation_py, _test_contracts_py, _test_domain_rules_py, _test_master_catalog_py

def brewmaster_bundle(milestone_id: str | None = None) -> list[dict[str, str]]:
    blueprint = brewmaster_blueprint(milestone_id)
    coverage = brewmaster_coverage(milestone_id)
    is_hito_001 = blueprint.get("milestone_id") == "HITO-001"
    is_hito_002 = blueprint.get("milestone_id") == "HITO-002"
    is_hito_003 = blueprint.get("milestone_id") == "HITO-003"
    is_hito_004 = blueprint.get("milestone_id") == "HITO-004"
    is_hito_005 = blueprint.get("milestone_id") == "HITO-005"
    is_hito_006 = blueprint.get("milestone_id") == "HITO-006"
    normalized_milestone = (milestone_id or "").strip().upper()
    hito7_or_later = normalized_milestone in {"HITO-007", "HITO-008"}
    include_deployment = normalized_milestone in {"", "HITO-007", "HITO-008"}
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
        "backend/pyproject.toml": _backend_pyproject(blueprint.get("milestone_id")),
        "backend/app/main.py": _backend_main(blueprint),
        "backend/app/core/responses.py": _responses_py(),
        "backend/app/core/security.py": _security_py(),
        "backend/app/domain/catalog.py": _catalog_py(blueprint),
        "backend/app/db/models.py": _models_py(blueprint),
        "backend/app/db/session.py": _session_py(),
        "backend/alembic/env.py": _alembic_env_py(),
        "backend/alembic/versions/0001_brewmaster_schema.py": _migration_py(blueprint),
        "frontend/index.html": _index_html(),
        "frontend/package.json": _frontend_package_json(),
        "frontend/src/main.jsx": _main_jsx(),
        "frontend/src/App.jsx": _app_jsx(blueprint),
        "frontend/src/api/client.js": _client_js(blueprint),
        "frontend/src/routes.js": _routes_js(blueprint),
        "frontend/src/screens/ScreenViews.jsx": _screen_views_jsx(blueprint),
        "frontend/src/screens/catalog.js": _screens_js(blueprint),
        "tests/test_contracts.py": _test_contracts_py(blueprint),
    }
    if is_hito_001:
        files["tests/test_auth_foundation.py"] = _test_auth_foundation_py()
    elif is_hito_002:
        files.update(
            {
                "backend/app/services/inventory.py": _inventory_service_py("HITO-002"),
                "tests/test_auth_foundation.py": _test_auth_foundation_py(),
                "tests/test_master_catalog.py": _test_master_catalog_py(),
            }
        )
    elif is_hito_003:
        files.update(
            {
                "backend/app/domain/rules.py": _rules_py("HITO-003"),
                "backend/app/services/inventory.py": _inventory_service_py("HITO-003"),
                "backend/app/services/notifications.py": _notifications_service_py("HITO-003"),
                "tests/test_auth_foundation.py": _test_auth_foundation_py(),
                "tests/test_master_catalog.py": _test_master_catalog_py(),
                "tests/test_domain_rules.py": _test_domain_rules_py("HITO-003"),
            }
        )
    elif is_hito_004:
        files.update(
            {
                "backend/app/domain/rules.py": _rules_py("HITO-004"),
                "backend/app/services/inventory.py": _inventory_service_py("HITO-003"),
                "backend/app/services/notifications.py": _notifications_service_py("HITO-003"),
                "backend/app/services/production.py": _production_service_py("HITO-004"),
                "tests/test_auth_foundation.py": _test_auth_foundation_py(),
                "tests/test_master_catalog.py": _test_master_catalog_py(),
                "tests/test_domain_rules.py": _test_domain_rules_py("HITO-004"),
            }
        )
    elif is_hito_005:
        files.update(
            {
                "backend/app/domain/rules.py": _rules_py("HITO-005"),
                "backend/app/services/inventory.py": _inventory_service_py("HITO-005"),
                "backend/app/services/notifications.py": _notifications_service_py("HITO-003"),
                "backend/app/services/production.py": _production_service_py("HITO-005"),
                "backend/app/services/sales.py": _sales_service_py(),
                "backend/app/services/purchasing.py": _purchasing_service_py(),
                "tests/test_auth_foundation.py": _test_auth_foundation_py(),
                "tests/test_master_catalog.py": _test_master_catalog_py(),
                "tests/test_domain_rules.py": _test_domain_rules_py("HITO-005"),
            }
        )
    elif is_hito_006:
        files.update(
            {
                "backend/app/domain/rules.py": _rules_py("HITO-005"),
                "backend/app/services/inventory.py": _inventory_service_py("HITO-005"),
                "backend/app/services/notifications.py": _notifications_service_py("HITO-003"),
                "backend/app/services/production.py": _production_service_py("HITO-005"),
                "backend/app/services/sales.py": _sales_service_py(),
                "backend/app/services/purchasing.py": _purchasing_service_py(),
                "backend/app/jobs/scheduler.py": _scheduler_py("HITO-006"),
                "tests/test_auth_foundation.py": _test_auth_foundation_py(),
                "tests/test_master_catalog.py": _test_master_catalog_py(),
                "tests/test_domain_rules.py": _test_domain_rules_py("HITO-006"),
            }
        )
    else:
        files.update(
            {
                "backend/app/domain/rules.py": _rules_py("HITO-005" if hito7_or_later else None),
                "backend/app/services/inventory.py": _inventory_service_py("HITO-005" if hito7_or_later else None),
                "backend/app/services/production.py": _production_service_py("HITO-005" if hito7_or_later else None),
                "backend/app/services/sales.py": _sales_service_py(),
                "backend/app/services/purchasing.py": _purchasing_service_py(),
                "backend/app/services/notifications.py": _notifications_service_py("HITO-003" if hito7_or_later else None),
                "backend/app/jobs/scheduler.py": _scheduler_py(normalized_milestone or None),
                "tests/test_auth_foundation.py": _test_auth_foundation_py(),
                "tests/test_master_catalog.py": _test_master_catalog_py(),
                "tests/test_domain_rules.py": _test_domain_rules_py(normalized_milestone or None),
            }
        )
        if include_deployment:
            files.update(
                {
                    "docker-compose.yml": _docker_compose_yml(),
                    ".env.example": _env_example(),
                    "backend/Dockerfile": _backend_dockerfile(),
                    "frontend/Dockerfile": _frontend_dockerfile(),
                    "deploy/nginx.conf": _nginx_conf(),
                    "docs/deployment.md": _deployment_md(),
                }
            )
    return [{"path": path, "content": content} for path, content in files.items()]
