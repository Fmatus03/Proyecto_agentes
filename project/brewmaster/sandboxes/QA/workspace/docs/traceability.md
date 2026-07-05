# Trazabilidad HITO-001

| requisito | evidencia generada | prueba |
|---|---|---|
| J.12 Hito 1 Fundamentos | backend/app/main.py, backend/app/core/security.py, contracts/permissions.json | tests/test_auth_foundation.py |
| FUN-001 Autenticar usuario | /api/v1/auth/login, /api/v1/auth/me | login valido, invalido e inactivo |
| FUN-002 Recuperar contrasena | /api/v1/auth/password-reset/request, /api/v1/auth/password-reset/confirm | token local de un uso |
| FUN-003 Gestionar usuarios roles permisos | /api/v1/users* | admin requerido, correo unico, rol activo |
| FUN-004 Registrar auditoria funcional | /api/v1/audit-logs | eventos de login, usuarios y contrasena |
| FUN-038 RBAC por endpoint | core/security.py | 401/403 sin datos parciales |
