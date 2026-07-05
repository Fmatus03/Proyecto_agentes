# ROADMAP brewmaster

WEBFORGE incremental roadmap. Each milestone is independently planned, validated and traced.

| id | name | dependencies | expected_artifacts | state |
|---|---|---|---|---|
| HITO-001 | Fundamentos | - | contracts/permissions.json, backend/app/core/security.py, backend/app/main.py, frontend/src/App.jsx, tests/test_contracts.py | approved |
| HITO-002 | Maestros | HITO-001 | backend/app/domain/catalog.py, backend/app/services/inventory.py, contracts/domain-model.json, frontend/src/screens/catalog.js, docs/architecture.md | pending |
| HITO-003 | Inventario | HITO-002 | backend/app/services/inventory.py, backend/app/services/notifications.py, backend/app/domain/rules.py, contracts/permissions.json, tests/test_domain_rules.py | pending |
| HITO-004 | Produccion | HITO-003 | backend/app/services/production.py, backend/app/domain/rules.py, contracts/coverage.json, docs/api-contract.md, tests/test_domain_rules.py | pending |
| HITO-005 | Ventas | HITO-004 | backend/app/services/sales.py, backend/app/services/purchasing.py, backend/app/services/inventory.py, docs/traceability.md, tests/test_domain_rules.py | pending |
| HITO-006 | Dashboard | HITO-005 | frontend/src/App.jsx, frontend/src/screens/catalog.js, backend/app/jobs/scheduler.py, docs/api-contract.md, tests/test_domain_rules.py | pending |
| HITO-007 | Cierre | HITO-006 | backend/app/services/purchasing.py, backend/app/jobs/scheduler.py, docs/architecture.md, docs/traceability.md, docs/test-strategy.md, tests/test_contracts.py | pending |
