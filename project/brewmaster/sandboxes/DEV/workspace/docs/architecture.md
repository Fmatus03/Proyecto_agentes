# Arquitectura BrewMaster

Capas:

- Frontend React + Bootstrap con rutas protegidas por rol, formularios validados, tablas paginadas y estados de carga, vacio y error.
- API REST FastAPI bajo `/api/v1`, respuestas JSON uniformes, RBAC por accion y `request_id` en cada respuesta.
- Dominio con servicios puros para stock, costo, ventas, compras, mermas y alertas.
- Persistencia SQLAlchemy/Alembic orientada a MySQL o MariaDB con indices y soft delete.
- Jobs APScheduler para alertas de stock, reintentos de correo, reservas vencidas, exportaciones y backups.
- Observabilidad con logs estructurados, auditoria funcional y metricas por modulo.

Controles de fabrica:

- Workflow antes que agentes: los archivos se producen como bundle cerrado y verificable.
- Arnes como frontera: la escritura ocurre solo por el materializador DEV.
- Permiso minimo: no hay deploy, secretos ni datos reales.
- Trazabilidad: `contracts/coverage.json` mapea modulos, pantallas, endpoints y reglas transaccionales.
