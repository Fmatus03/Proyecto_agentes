# Trazabilidad HITO-008

| requisito | evidencia generada | prueba |
|---|---|---|
| HITO-001 Fundamentos conservados | backend/app/main.py, backend/app/core/security.py | tests/test_auth_foundation.py |
| HITO-002 Maestros conservados | proveedores, insumos, bodegas, recetas, presentaciones | tests/test_master_catalog.py |
| HITO-003 Inventario y SMTP conservados | supply-entries, Kardex, low-stock, settings/smtp, notifications | tests/test_domain_rules.py |
| HITO-004 Produccion conservada | batches, quality-check, waste-records, products, product Kardex | tests/test_domain_rules.py |
| HITO-005 Ventas y compras conservadas | customers, sales, reservations, purchase-orders | tests/test_domain_rules.py |
| HITO-006 Dashboard/reportes/scheduler conservados | dashboard, reports/export, jobs operacionales | tests/test_domain_rules.py |
| HITO-007 Cierre conservado | equipment, expenses, monthly-goals, jobs, backups, deploy docs | tests/test_domain_rules.py, tests/test_contracts.py |
| SCR-001..SCR-030 pantallas separadas | frontend/src/screens/catalog.js, frontend/src/screens/ScreenViews.jsx | tests/test_contracts.py, pnpm build |
| Navegacion frontend | frontend/src/App.jsx, frontend/src/routes.js | tests/test_contracts.py, pnpm build |
| Cliente API local | frontend/src/api/client.js consume solo `/api/v1` | tests/test_contracts.py |
| Estados loading/error/vacio | ScreenViews.jsx helpers `useResources`, `ScreenFrame`, `EmptyState` | tests/test_contracts.py |
