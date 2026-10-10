# Nexora HQ Roadmap

Nexora HQ is the parent-company visibility layer. It does not execute venture workloads or manage each venture's generated products.

## M0 — Repository foundation
- [x] Establish a separate HQ boundary and repository.
- [x] Document architecture, security, integration contract and roadmap.
- [x] Create a responsive dashboard shell with explicit unconnected states.
- [x] Add CI checks for dashboard structure and JavaScript syntax.
- [x] Validate the static site in the Pages workflow and enable Pages during first deployment when supported.
- [ ] Verify a successful GitHub Pages deployment.

## M1 — Complete HQ interface
- [x] Add Overview, Venture Registry, Activity and Settings views.
- [x] Add client-side venture search and responsive navigation.
- [x] Distinguish illustrative setup records from live external activity.
- [x] Add accessible status messages, reduced-motion support and mobile layouts.
- [ ] Run browser-based accessibility and interaction checks.

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
- [ ] Verify lint and backend tests pass in GitHub Actions and review production database/migration requirements.

## M3 — Operational control center
- [ ] Add authentication, authorization, session handling and audit logging before private production use.
- [ ] Add system health, stale-data indicators and error reporting.
- [ ] Add configuration management with validation and safe defaults.
- [ ] Add observability, backups and recovery guidance.

## M4 — Production readiness
- [ ] Review threat model, secrets handling, dependency updates and least privilege.
- [x] Add regression checks for primary accessible names, live status announcements, and external-only scripts.
- [ ] Manually test keyboard navigation, screen-reader behavior, contrast and responsive layouts.
- [x] Add a hardened self-hostable Docker/Compose deployment and container build validation.
- [ ] Verify CI and Pages deployment with actual successful workflow runs.
- [ ] Verify a deployment on an actual target host.
- [ ] Document local development, deployment, recovery and incident procedures.

## Later — Venture integrations and limits
- [ ] Integrate AI Software Developer through a read-only venture-level adapter.
- [ ] Integrate AI Open Source Contributor through its own read-only adapter.
- [ ] Test timeout, unavailable, malformed, stale and rate-limited upstream responses.
- [ ] Define operational limits and policies after the core system is stable.

## Acceptance rule
A milestone is complete only when its acceptance checks have run and their results are verified. A commit or a workflow definition alone is not proof of a successful deployment.
