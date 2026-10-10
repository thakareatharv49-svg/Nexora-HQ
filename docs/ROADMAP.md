# Nexora HQ Roadmap

## M0 — Repository foundation
- [x] Establish a separate HQ boundary and repository.
- [x] Create responsive dashboard shell with honest unconnected states.
- [x] Document architecture, security, contracts and roadmap.
- [ ] Validate shell and establish CI.

## M1 — Registry and API
- [ ] Define and validate venture registry schema.
- [ ] Add backend health and registry endpoints.
- [ ] Add environment-based configuration validation.
- [ ] Add linting, unit tests and CI.

## M2 — AI Software Developer adapter
- [ ] Confirm stable venture-level health/status/activity API.
- [ ] Implement read-only adapter with timeouts and freshness.
- [ ] Test unavailable, stale, malformed and rate-limited responses.
- [ ] Display venture-level data only; generated apps remain within that venture.

## M3 — AI Open Source Contributor adapter
- [ ] Confirm its separate stable status contract.
- [ ] Implement adapter and failure-isolation tests.
- [ ] Display source timestamps and connection state.

## M4 — Production hardening
- [ ] Authentication, authorization and audit logging.
- [ ] Secret management, monitoring, backups and recovery.
- [ ] Deployment pipeline and staging end-to-end tests.

## Acceptance criteria
- Demo data is never represented as live.
- Each venture shows connection state and last update.
- One adapter failing does not break other cards.
- HQ cannot trigger missions, publish apps or mutate venture state.
- Generated apps are not individual HQ ventures.
