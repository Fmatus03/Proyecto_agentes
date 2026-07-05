# API contract

Respuesta exitosa: `{"data": {}, "meta": {"request_id": "REQ-TBD"}}`.

| method | path | handler |
|---|---|---|
| POST | `/api/v1/auth/login` | `auth.login` |
| POST | `/api/v1/auth/logout` | `auth.logout` |
| GET | `/api/v1/auth/me` | `auth.me` |
| POST | `/api/v1/auth/change-password` | `auth.change_password` |
| GET | `/api/v1/users` | `users.list` |
| POST | `/api/v1/users` | `users.create` |
| GET | `/api/v1/users/{id}` | `users.detail` |
| PUT | `/api/v1/users/{id}` | `users.update` |
| PATCH | `/api/v1/users/{id}/toggle-status` | `users.toggle_status` |
| GET | `/api/v1/audit-logs` | `audit_logs.list` |
| POST | `/api/v1/auth/password-reset/request` | `auth.password_reset_request` |
| POST | `/api/v1/auth/password-reset/confirm` | `auth.password_reset_confirm` |
