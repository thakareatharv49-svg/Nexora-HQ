# Nexora HQ Roadmap

Nexora HQ is the parent-company visibility layer. It does not execute venture workloads or manage each venture's generated products.

## M0 — Repository foundation
- [x] Establish a separate HQ boundary and repository.
- [x] Document architecture, security, integration contract and roadmap.
- [x] Create a responsive dashboard shell with explicit unconnected states.
- [x] Add CI checks for dashboard structure and JavaScript syntax.
- [x] Make Pages publishing conditional on repository Pages configuration and avoid false CI failures when publishing is not enabled.
- [ ] Verify a successful GitHub Pages deployment from its actual workflow result.

## M1 — Complete HQ interface
- [x] Add Overview, Venture Registry, Activity and Settings views.
- [x] Add client-side venture search and responsive navigation.
- [x] Distinguish illustrative setup records from live external activity.
- [x] Add accessible status messages, reduced-motion support and mobile layouts.
- [x] Add automated checks for accessible names, live status announcements and external-only scripts.
- [x] Verify browser sign-in, invalid-password handling, navigation, search and sign-out in [CI run #40](https://github.com/thakareatharv49-svg/Nexora-HQ/actions/runs/38095067863).
- [x] Verify mobile navigation, responsive layout, and keyboard focus trapping in [CI run #44](https://github.com/thakareatharv49-svg/Nexora-HQ/actions/runs/38095336591).
- [ ] Run manual browser, keyboard, screen-reader, contrast and responsive checks.

## M2 — Backend and persistence
- [x] Select and document the initial backend/runtime (FastAPI + SQLite).
- [x] Implement health, venture registry and HQ activity endpoints.
- [x] Persist registry records and HQ activity records.
- [x] Validate activity query limits and response schemas.
- [x] Add API regression tests for health, persistence, validation and dashboard serving.
- [x] Connect the dashboard to same-origin HQ API endpoints while retaining static-hosting fallback.
- [x] Add validated runtime environment configuration and a database readiness probe.
- [x] Add degraded-health behavior and generic error responses that avoid exposing exception details.
- [x] Add tests for invalid configuration and database-unavailable health.
- [x] Verify frontend tests, Python compilation, Ruff, backend tests, Docker build and live container smoke test in [CI run #34](https://github.com/thakareatharv49-svg/Nexora-HQ/actions/runs/38094301034).
- [x] Verify authenticated production registry/activity access and sign-in behavior in [CI run #37](https://github.com/thakareatharv49-svg/Nexora-HQ/actions/runs/38094769516).
- [ ] Review production database migration and long-term persistence requirements.

## M3 — Operational control center
- [x] Add production admin authentication, signed eight-hour sessions, and authorization on registry/activity APIs.
- [x] Persist administrator sign-in and sign-out events in the HQ activity log.
- [ ] Add login-attempt rate limiting and a richer admin identity model before public internet exposure.
- [x] Add system health, database readiness and safe error responses.
- [ ] Add stale-data and last-success indicators after venture adapters exist.
- [x] Add runtime configuration validation and safe defaults.
- [x] Document database backup and restore procedures.
- [x] Add integrity-checked SQLite backup/restore helpers, explicit overwrite protection, rollback copies, and regression tests.
- [x] Add an operations and incident-response runbook.
- [ ] Add monitoring and alerting.

## M4 — Production readiness
- [x] Require production password hashes and session secrets through environment configuration; keep them out of browser assets.
- [ ] Review the full threat model, dependency update policy and least privilege for a real deployment.
- [x] Add a hardened self-hostable Docker/Compose deployment and container build validation.
- [x] Smoke-test the running container as a non-root user and verify primary API routes in CI.
- [x] Document local development, container deployment, backup and recovery steps.
- [ ] Verify a successful GitHub Pages deployment from its actual workflow result.
- [ ] Verify a deployment on an actual target host.
- [ ] Complete manual accessibility and browser acceptance testing.

## Later — Venture integrations and limits
- [ ] Integrate AI Software Developer through a read-only venture-level adapter.
- [ ] Integrate AI Open Source Contributor through its own read-only adapter.
- [ ] Test timeout, unavailable, malformed, stale and rate-limited upstream responses.
- [ ] Define operational limits and policies after the core system is stable.

## Acceptance rule
A milestone is complete only when its acceptance checks have run and their results are verified. A commit or a workflow definition alone is not proof of a successful deployment.
