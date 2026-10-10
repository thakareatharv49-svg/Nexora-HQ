# Deployment Guide

## Recommended container deployment

Requirements: Docker Engine and Docker Compose plugin.

From the repository root, generate a password hash with `python -m src.nexora_hq.auth hash-password` and a session secret with `python -c "import secrets; print(secrets.token_urlsafe(48))"`. Copy `.env.example` to `.env` and fill in both values. Keep `.env` private and out of source control.

Then run:

```bash
docker compose up --build -d
docker compose ps
docker compose logs --tail=100 nexora-hq
```

Open `http://localhost:8000`. The application serves the dashboard and API from one origin. The container runs as a non-root user, drops Linux capabilities, disables privilege escalation, uses a read-only root filesystem, and keeps SQLite data in a named volume. Production requires administrator credentials; the dashboard presents a sign-in screen and protects registry/activity APIs with a signed session cookie.

The health check calls `/api/health`; it fails if the database is not ready. External venture integrations remain unconfigured. This is a self-hostable container baseline, not proof that a hosted production deployment exists.

## Updating

```bash
git pull
docker compose up --build -d
docker compose ps
```

Review the release notes and back up the data volume before updating a production deployment.

## SQLite backup and restore

For a consistent backup, stop writes or use SQLite's online backup API. A simple maintenance-window backup:

```bash
docker compose stop nexora-hq
docker run --rm -v nexora-data:/data -v "$PWD/backups:/backups" alpine sh -c 'cp /data/nexora-hq.sqlite3 /backups/nexora-hq.sqlite3'
docker compose start nexora-hq
```

Restore only with the service stopped, and retain a copy of the existing database before replacing it. Periodically test restoration in a separate environment. For high availability or heavy concurrent writes, evaluate a managed database before scaling.

## Production checklist

- Put the service behind HTTPS and a trusted reverse proxy.
- Restrict network access to the API and documentation endpoints according to your deployment.
- Configure admin credentials and add login-attempt rate limiting before exposing the service to the public internet.
- Configure backups, retention, monitoring, alerting, and tested restore procedures.
- Keep secrets outside the image and repository.
- Verify the container health state and test `/api/health`, `/api/ventures`, and `/api/activity` after deployment.
- Do not mark a deployment complete until the target host and its health checks are actually verified.

## Static GitHub Pages

The Pages workflow publishes only `apps/web/`. It does not host the FastAPI backend or SQLite database. A Pages-only deployment therefore remains in static-foundation mode until a separately hosted backend and an intentional secure connection are configured.
