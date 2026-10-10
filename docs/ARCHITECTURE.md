# Architecture

```text
                       Nexora HQ
             venture registry + dashboard
                  /                \
        read-only adapter    read-only adapter
              /                    \
 AI Software Developer    AI Open Source Contributor
 factory + generated apps OSS discovery + contributions
```

## HQ owns
- Venture display metadata and registry.
- High-level cross-venture status and recent activity.
- Adapter connection state and freshness.

## Ventures own
- Their business logic, storage, credentials, logs, workflows and release lifecycle.
- All generated app details and previews remain in AI Software Developer.

## Implementation path
Start with a static shell. Add a server-side API before connecting credentials or private data. FastAPI and PostgreSQL are candidates, but should be selected when the API and persistence requirements are confirmed.

## Failure isolation
Each adapter fails independently. Show stale/error state and last successful timestamp; never silently present stale values as current. HTTP 200 alone is not proof of operational health.
