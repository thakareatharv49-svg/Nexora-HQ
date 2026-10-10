# Nexora HQ Roadmap

Nexora HQ is the parent-company visibility layer. It does not execute venture workloads or manage each venture's generated products.

## M0 — Repository foundation
- [x] Establish a separate HQ boundary and repository.
- [x] Document architecture, security, integration contract and roadmap.
- [x] Create a responsive dashboard shell with explicit unconnected states.
- [x] Add CI checks for dashboard structure and JavaScript syntax.
- [ ] Verify a successful GitHub Pages deployment.

## M1 — Complete HQ interface
- [x] Add Overview, Venture Registry, Activity and Settings views.
- [x] Add client-side venture search and responsive navigation.
- [x] Distinguish illustrative setup records from live external activity.
- [x] Add accessible status messages, reduced-motion support and mobile layouts.
- [ ] Run browser-based accessibility and interaction checks.

## M2 — Backend and persistence
- [ ] Select and document the production backend/runtime.
- [ ] Implement health, venture registry and HQ activity endpoints.
- [ ] Persist registry records and audit events.
- [ ] Validate input, configuration and response schemas.
- [ ] Add API tests and database migration strategy.
- [ ] Integrate the interface with the API without fabricating fallback live data.

## M3 — Operational control center
- [ ] Add authentication, authorization, session handling and audit logging.
- [ ] Add system health, stale-data indicators and error reporting.
- [ ] Add configuration management with validation and safe defaults.
- [ ] Add observability, backups and recovery guidance.

## M4 — Production readiness
- [ ] Review threat model, secrets handling, dependency updates and least privilege.
- [ ] Test keyboard navigation, screen-reader labels, contrast and responsive layouts.
- [ ] Verify CI and Pages deployment with actual successful workflow runs.
- [ ] Document local development, deployment, recovery and incident procedures.

## Later — Venture integrations and limits
- [ ] Integrate AI Software Developer through a read-only venture-level adapter.
- [ ] Integrate AI Open Source Contributor through its own read-only adapter.
- [ ] Test timeout, unavailable, malformed, stale and rate-limited upstream responses.
- [ ] Define operational limits and policies after the core system is stable.

## Acceptance rule
A milestone is complete only when its acceptance checks have run and their results are verified. A commit or a workflow definition alone is not proof of a successful deployment.
