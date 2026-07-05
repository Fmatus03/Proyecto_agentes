# Arquitectura BrewMaster HITO-001

Capas:

- Frontend React + Bootstrap limitado a login, recuperacion de contrasena y panel de usuarios/auditoria.
- API REST FastAPI bajo `/api/v1` con respuesta JSON uniforme y `request_id`.
- Seguridad local con hash PBKDF2, JWT HS256 expirable y RBAC por rol.
- Persistencia contractual SQLAlchemy/Alembic acotada a usuarios, roles, permisos, auditoria y tokens de restablecimiento.
- Auditoria funcional en memoria para el MVP local del hito, sin datos reales ni escrituras externas.

Controles de fabrica:

- El bundle se materializa solo por el arnes P12/INV en el sandbox DEV.
- La promocion a QA ocurre despues de validadores y gate incremental.
- Los modulos de hitos posteriores quedan explicitamente diferidos y no exponen endpoints ejecutables.
