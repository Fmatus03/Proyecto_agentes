# BrewMaster Deployment Target

BrewMaster will be deployed to a single AWS EC2 VM that contains the whole system through Docker Compose.

The production deployment is allowed only when the WorkOrder explicitly uses `approved_deploy` and the run includes human approval, rollback plan, secret handling and evidence.

## Runtime Shape

- `proxy`: Nginx reverse proxy exposed on ports 80 and 443.
- `frontend`: React build served by Nginx.
- `backend`: FastAPI service under `/api/v1`.
- `db`: MariaDB/MySQL with a persistent Docker volume.
- `jobs`: included in the backend container or split later if operational load requires it.

## EC2 Requirements

- Security group exposes only 80 and 443 publicly.
- SSH is restricted to trusted IPs.
- Docker Engine and Docker Compose plugin are installed on the VM.
- `.env` is stored on the VM with restrictive permissions and is never committed.
- Database data uses a persistent volume and has a tested backup/restore process.

## Required Evidence Before Production

- `docker compose config` passes.
- Backend and frontend images build.
- API healthcheck responds.
- Frontend loads through the proxy.
- Database healthcheck passes.
- Alembic migrations complete.
- Backup and restore procedure is tested.
- Rollback procedure is documented and approved.

## GitHub Actions CI/CD

Workflow: `.github/workflows/brewmaster-ec2.yml`.

Required repository secrets:

- `BREWMASTER_ENV_PRODUCTION`: complete production `.env` content.
- `EC2_HOST`: EC2 public IP or DNS name.
- `EC2_USER`: SSH user, usually `ubuntu`.
- `EC2_PORT`: SSH port, usually `22`.
- `EC2_SSH_KEY`: complete private PEM content for the EC2 key pair.

Pipeline behavior:

- `validate` installs backend dependencies, runs pytest, builds the React frontend with pnpm, and validates Docker Compose syntax.
- `deploy` runs after validation, uploads a release tarball to `/opt/brewmaster/releases/<git-sha>`, writes `.env` from `BREWMASTER_ENV_PRODUCTION`, updates `/opt/brewmaster/current`, and runs `docker compose --env-file .env -f docker-compose.ec2.yml up -d --build`.

Operational notes:

- Do not commit `.env`, PEM keys, generated `dist`, or `node_modules`.
- Rotate any secret that has been pasted into chat, logs, screenshots, or issue trackers before production use.
- Keep EC2 security group SSH restricted to trusted IPs; expose only 80/443 publicly.
