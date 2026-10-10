# Security Model

## Current safeguards
- The API is read-only: no endpoint can mutate a venture or execute a workload.
- The browser contains no tokens or credentials.
- Runtime configuration is validated; production mode rejects an in-memory database.
- The health endpoint reports database readiness separately from venture integration readiness.
- Unexpected API errors return a generic message; the log entry includes only the exception class, not the exception message or request data.
- SQLite is used only for HQ-owned registry and activity records.

## Before private production use
- Add authentication, authorization, session protections, and an auditable administrative identity model.
- Keep credentials server-side in a secret manager; never commit them or bundle them into browser assets.
- Use repository-scoped, read-only permissions wherever possible.
- Set explicit request timeouts and bounded retries for each future adapter.
- Redact tokens, authorization headers, and sensitive URLs from logs.
- Validate every adapter payload before rendering and include source/retrieval timestamps and freshness.
- Add database backups, restore tests, retention policy, dependency review, and incident procedures.
- Require HTTPS and review deployment-specific headers and access controls.

## Venture boundaries
- HQ may display venture-level status and activity only.
- Generated applications, previews, project execution, credentials, and releases remain owned by AI Software Developer.
- Open-source discovery and contribution execution remain owned by AI Open Source Contributor.
- Dashboard controls must not mutate venture state. Limits and policies are intentionally deferred until the core system is stable.
