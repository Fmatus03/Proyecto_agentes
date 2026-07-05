# Estrategia de pruebas HITO-001

Unitarias:

- Hash de contrasena PBKDF2 no almacena texto plano.
- JWT HS256 expirable rechaza firma alterada o vencida.
- `require_permission` acepta comodin admin y bloquea permiso ausente.

Integracion local:

- Login exitoso retorna JWT y `auth/me` responde con usuario activo.
- Credenciales invalidas o usuario inactivo retornan HTTP 401 y generan auditoria.
- Usuario no admin recibe HTTP 403 al listar usuarios.
- Admin crea usuario con correo unico y rol activo; duplicado se rechaza.
- Cambio y restablecimiento de contrasena actualizan hash y auditan.
- Auditor o admin consulta `/api/v1/audit-logs`; otros roles no reciben datos parciales.
