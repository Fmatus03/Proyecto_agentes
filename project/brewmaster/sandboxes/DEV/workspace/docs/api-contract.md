# API contract

Respuesta exitosa: `{"data": {}, "meta": {"request_id": "REQ-TBD"}}`.

| method | path | handler |
|---|---|---|
| POST | `/api/v1/auth/login` | `auth.login` |
| POST | `/api/v1/auth/logout` | `auth.logout` |
| GET | `/api/v1/auth/me` | `auth.list` |
| POST | `/api/v1/auth/change-password` | `auth.change_password` |
| GET | `/api/v1/users` | `users.list` |
| POST | `/api/v1/users` | `users.create` |
| GET | `/api/v1/users/{id}` | `users.detail` |
| PUT | `/api/v1/users/{id}` | `users.update` |
| PATCH | `/api/v1/users/{id}/toggle-status` | `users.toggle_status` |
| GET | `/api/v1/suppliers` | `suppliers.list` |
| POST | `/api/v1/suppliers` | `suppliers.create` |
| PUT | `/api/v1/suppliers/{id}` | `suppliers.update` |
| PATCH | `/api/v1/suppliers/{id}/toggle-status` | `suppliers.toggle_status` |
| GET | `/api/v1/supplies` | `supplies.list` |
| POST | `/api/v1/supplies` | `supplies.create` |
| GET | `/api/v1/supplies/{id}` | `supplies.detail` |
| PUT | `/api/v1/supplies/{id}` | `supplies.update` |
| PATCH | `/api/v1/supplies/{id}/toggle-status` | `supplies.toggle_status` |
| GET | `/api/v1/supplies/{id}/kardex` | `supplies.detail` |
| GET | `/api/v1/supplies/low-stock` | `supplies.list` |
| POST | `/api/v1/supply-entries` | `supply_entries.create` |
| GET | `/api/v1/supply-entries` | `supply_entries.list` |
| GET | `/api/v1/recipes` | `recipes.list` |
| POST | `/api/v1/recipes` | `recipes.create` |
| GET | `/api/v1/recipes/{id}` | `recipes.detail` |
| PUT | `/api/v1/recipes/{id}` | `recipes.update` |
| POST | `/api/v1/recipes/{id}/clone` | `recipes.clone` |
| GET | `/api/v1/batches` | `batches.list` |
| POST | `/api/v1/batches` | `batches.create` |
| GET | `/api/v1/batches/{id}` | `batches.detail` |
| PUT | `/api/v1/batches/{id}` | `batches.update` |
| POST | `/api/v1/batches/{id}/complete` | `batches.complete` |
| POST | `/api/v1/batches/{id}/cancel` | `batches.cancel` |
| POST | `/api/v1/batches/{id}/quality-check` | `batches.quality_check` |
| GET | `/api/v1/products` | `products.list` |
| PUT | `/api/v1/products/{id}/price` | `products.update` |
| POST | `/api/v1/sales` | `sales.create` |
| GET | `/api/v1/sales` | `sales.list` |
| GET | `/api/v1/customers` | `customers.list` |
| POST | `/api/v1/customers` | `customers.create` |
