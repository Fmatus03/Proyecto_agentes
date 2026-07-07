# Despliegue BrewMaster en AWS EC2

Objetivo:

- Ejecutar BrewMaster completo en una VM EC2 mediante Docker Compose.
- Mantener frontend, backend, base de datos, proxy reverso y jobs dentro de la VM.
- Bloquear deploy productivo hasta contar con aprobacion humana, rollback y evidencia de pruebas.

Servicios esperados:

- `frontend`: React compilado y servido por Nginx.
- `backend`: FastAPI bajo `/api/v1`.
- `db`: MariaDB/MySQL con volumen persistente.
- `proxy`: Nginx como entrada HTTP/HTTPS.

Reglas operativas:

- No versionar secretos reales.
- Usar `.env` local protegido en la VM y `.env.example` en git.
- Ejecutar migraciones Alembic antes de habilitar trafico.
- Validar healthchecks antes de cerrar el deploy.
- Probar backup/restore y rollback en cada cierre mayor.

Puertos:

- Exponer publicamente solo 80/443 en el security group.
- Mantener base de datos y backend en red interna Docker.

Evidencia requerida:

- `docker compose config` sin errores.
- Build de imagenes exitoso.
- Smoke test HTTP de frontend y API.
- Log de migraciones.
- Backup restaurable.
- Plan de rollback firmado/aprobado.
