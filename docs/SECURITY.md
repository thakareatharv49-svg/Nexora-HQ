# Security Model

- Keep credentials server-side; never bundle them into browser assets.
- Use repository-scoped, read-only permissions wherever possible.
- Use environment variables or a secret manager; commit only empty placeholders.
- Set explicit request timeouts and bounded retries.
- Redact tokens, authorization headers and sensitive URLs from logs.
- Validate every adapter payload before rendering.
- Add authentication and authorization before exposing non-public venture data.
- Include source and retrieval timestamp for traceability.
- Dashboard controls must not mutate venture state.
