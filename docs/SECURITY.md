# Security Model

## Current safeguards
- The API is read-only: no endpoint can mutate a venture or execute a workload.
- The browser contains no tokens or credentials.
- Production requires an environment-supplied scrypt password hash and a 32+ character session-signing secret.
- Successful administrator sign-in and sign-out events are persisted in the HQ activity log; rejected sign-ins emit a generic warning without logging the submitted password.
- The admin session uses a signed, eight-hour cookie marked HttpOnly, SameSite=Strict, and Secure in production.
- Registry and activity endpoints require an authenticated admin session in production; health and authentication status expose no registry data.
- The FastAPI runtime sets a restrictive Content Security Policy, frame denial, MIME-sniffing protection, referrer policy, and restrictive browser feature policy.
- Interactive API docs and the OpenAPI schema are disabled in production mode.
- Runtime configuration is validated; production mode rejects an in-memory database.
- The health endpoint reports database readiness separately from venture integration readiness.
- Unexpected API errors return a generic message; the log entry includes only the exception class, not the exception message or request data.
- SQLite is used only for HQ-owned registry and activity records.

## Before private production use
- Add login-attempt rate limiting and a richer administrative identity model before exposing authentication to the public internet.
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
