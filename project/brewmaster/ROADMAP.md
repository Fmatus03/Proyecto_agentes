# ROADMAP brewmaster

WEBFORGE incremental roadmap. Each milestone is independently planned, validated and traced.

| id | name | dependencies | expected_artifacts | state |
|---|---|---|---|---|
| HITO-001 | Fundamentos | - | contracts/permissions.json, backend/app/core/security.py, backend/app/main.py, frontend/src/App.jsx, tests/test_contracts.py | approved |
| HITO-002 | Maestros | HITO-001 | backend/app/domain/catalog.py, backend/app/services/inventory.py, contracts/domain-model.json, frontend/src/screens/catalog.js, docs/architecture.md | approved |
| HITO-003 | Inventario | HITO-002 | backend/app/services/inventory.py, backend/app/services/notifications.py, backend/app/domain/rules.py, contracts/permissions.json, tests/test_domain_rules.py | approved |
| HITO-004 | Produccion | HITO-001, HITO-002, HITO-003 | backend/app/services/production.py, backend/app/domain/rules.py, contracts/coverage.json, docs/api-contract.md, tests/test_domain_rules.py | approved |
| HITO-005 | Ventas | HITO-001, HITO-002, HITO-003, HITO-004 | backend/app/services/sales.py, backend/app/services/purchasing.py, backend/app/services/inventory.py, docs/traceability.md, tests/test_domain_rules.py | approved |
| HITO-006 | Dashboard | HITO-001, HITO-002, HITO-003, HITO-004, HITO-005 | frontend/src/App.jsx, frontend/src/screens/catalog.js, backend/app/jobs/scheduler.py, docs/api-contract.md, docs/traceability.md, docs/test-strategy.md, contracts/coverage.json, tests/test_domain_rules.py | approved |
| HITO-007 | Cierre | HITO-001, HITO-002, HITO-003, HITO-004, HITO-005, HITO-006 | backend/app/services/purchasing.py, backend/app/jobs/scheduler.py, docker-compose.yml, deploy/nginx.conf, docs/deployment.md, docs/architecture.md, docs/traceability.md, docs/test-strategy.md, tests/test_contracts.py | approved |
| HITO-008 | Pantallas interactivas | HITO-001, HITO-002, HITO-003, HITO-004, HITO-005, HITO-006, HITO-007 | frontend/index.html, frontend/src/main.jsx, frontend/src/App.jsx, frontend/src/routes.js, frontend/src/api/client.js, frontend/src/screens/catalog.js, frontend/src/screens/ScreenViews.jsx, docs/traceability.md, docs/test-strategy.md, tests/test_contracts.py | approved |
