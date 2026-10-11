# Nexora HQ

Nexora HQ is the parent-company control center for Nexora's ventures. It is a separate application and repository, not the execution engine for the ventures themselves.

## Ownership boundaries

- **Nexora HQ** owns the venture registry, company-level visibility, high-level activity, connection health and configuration.
- **AI Software Developer** owns autonomous software project execution, generated applications, previews and its internal workflows.
- **AI Open Source Contributor** owns its own open-source discovery and contribution workflows.
- HQ will monitor venture-level status through read-only adapters after each venture is stable. Generated apps remain managed by AI Software Developer.

## Run the full application locally

Requires Python 3.12+.

```bash
python -m venv .venv
# Activate the environment, then:
python -m pip install -r requirements.txt
uvicorn src.nexora_hq.app:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). The FastAPI application serves the dashboard and exposes:

- `GET /api/health` — HQ service health and database readiness.
- `GET /api/auth/status`, `POST /api/auth/login`, `POST /api/auth/logout` — session-based administrator sign-in.
- Registry and activity endpoints require a valid administrator session in production.
- `GET /api/ventures` — persisted venture registry.
- `POST /api/ventures` — register a venture in the HQ-owned registry; this does not connect to or modify the venture itself.
- `PATCH /api/ventures/{venture_id}` — update HQ-owned venture metadata and record the change in HQ activity.
- `GET /api/activity?limit=50` — HQ-owned activity records; limit must be between 1 and 100.
- `GET /docs` — interactive API documentation in development/test mode; disabled in production.

SQLite stores HQ registry and activity records in `data/nexora-hq.sqlite3` by default. Set `NEXORA_DB_PATH` to use a different path and `NEXORA_ENV` to `development`, `test`, or `production`. Runtime configuration is validated; production mode requires an admin password hash and a session-signing secret and rejects an in-memory database. The database is initialized with the two known ventures and clearly labeled HQ setup records. External venture integrations remain unconfigured. The health endpoint returns a degraded response when the database readiness probe fails.

For the static frontend alone, run `python -m http.server 4173 --directory apps/web` and open [http://localhost:4173](http://localhost:4173). Static hosting does not include the API; the UI stays in its explicit static-foundation state.

## Container deployment

See [the deployment guide](docs/DEPLOYMENT.md). With Docker installed, run `docker compose up --build -d`, then open [http://localhost:8000](http://localhost:8000). The container uses a persistent named volume for SQLite and runs with a non-root user and a read-only root filesystem. GitHub Pages publishes only the static frontend; it does not host this API.

## Validate

Requires Node.js 22 or compatible modern Node.js and Python 3.12+:

```bash
node --check apps/web/app.js
node --test tests/*.test.cjs
python -m compileall -q src tests
python -m ruff check src tests
python -m pytest -q
```

GitHub Actions validates frontend behavior, runs Chromium browser acceptance tests for sign-in/navigation/search/sign-out, checks Python compilation and lint, runs backend tests, builds the production image, and smoke-tests the authenticated running container on pull requests. A successful public Pages deployment or target-host deployment must still be verified in the repository's Actions tab and on the target host.

## Repository structure

- `apps/web/` — responsive dashboard: Overview, Venture Registry, Activity and Settings.
- `src/nexora_hq/` — FastAPI application and SQLite persistence layer.
- `docs/` — architecture, integration contract, security and roadmap.
- `schemas/` — example normalized venture status payload; not live data.
- `tests/` — frontend and backend regression tests.
- `.github/workflows/` — CI validation and GitHub Pages deployment workflow.

## Security principles

Never put tokens or credentials in browser code. Future venture adapters must run server-side, use least-privilege read-only access, apply timeouts, report source timestamps and freshness, and isolate upstream failures. HQ must not execute, mutate or take ownership of venture workloads. Configuration and authentication remain read-only/unimplemented until their own milestone is delivered.

## Delivery status

A workflow file is not proof of a successful deployment. Check actual workflow results before treating CI or Pages as verified. Authentication, production monitoring, recovery, and venture integrations are later milestones tracked in [the roadmap](docs/ROADMAP.md).
