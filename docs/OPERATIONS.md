# Nexora HQ Operations

This runbook covers HQ-owned service operations only. HQ does not execute or recover venture workloads.

## Health checks

- `GET /api/health` returns `status: ok` when the HQ database is reachable.
- A `503` with `status: degraded` means the database readiness probe failed.
- `venture_integrations: not_configured` is expected until read-only adapters are approved and implemented.
- Healthy HQ does not prove that either venture is healthy.

## Create a consistent backup

Run maintenance while the service is stopped when practical. The helper uses SQLite's backup API, validates the copy, and publishes it atomically.

```bash
python -c "from src.nexora_hq.maintenance import backup_database; print(backup_database('data/nexora-hq.sqlite3', 'backups/nexora-hq.sqlite3'))"
```

Store backups outside the repository, restrict filesystem permissions, and define a retention policy. Never commit production database files.

## Restore and rollback

Stop the HQ service before restoring. Restore to a new path first when possible:

```bash
python -c "from src.nexora_hq.maintenance import restore_database; print(restore_database('backups/nexora-hq.sqlite3', 'data/nexora-hq-restored.sqlite3'))"
```

Replacing an existing database requires explicit `overwrite=True`. A timestamped pre-restore copy is created before replacement:

```bash
python -c "from src.nexora_hq.maintenance import restore_database; print(restore_database('backups/nexora-hq.sqlite3', 'data/nexora-hq.sqlite3', overwrite=True))"
```

Verify health and expected records before considering recovery complete. Do not restore into a database file actively used by a running service.

## Incident checklist

1. Record the timestamp, status code, deployed version, and symptoms.
2. Check process/container health and recent logs; redact secrets and session cookies.
3. Preserve the original database before attempting repair.
4. Restore a validated copy to a separate path and check integrity and expected records.
5. Switch to the verified copy during a controlled maintenance window; recheck health and authenticated API behavior.
6. Document the cause and follow-up actions.

## GitHub Pages

The Pages workflow validates the static frontend on every relevant change. Publishing is conditional on Pages already being enabled for the repository. If it is not enabled, the workflow reports a warning and skips only the deployment steps; it does not attempt to change repository settings with a token that may not have administration permission.

To enable the optional static preview, open repository **Settings → Pages** and choose **GitHub Actions** as the build and deployment source. The static preview does not include FastAPI or SQLite. Use the container deployment documented in [DEPLOYMENT.md](DEPLOYMENT.md) for the complete application.

## Operational boundaries

- Keep credentials out of logs and browser code.
- Never store generated venture applications in the HQ database.
- Never describe disconnected venture state as live monitoring.
- Monitoring/alerting, retention policy, login rate limiting, and target-host deployment verification remain tracked work.
