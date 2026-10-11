# Architecture

Nexora HQ is the parent-company visibility layer. The current application uses a FastAPI server, SQLite persistence for HQ-owned records, and a static frontend served by the same app for local/self-hosted use.

```text
                       Nexora HQ
          dashboard + registry + HQ activity
                         |
                  read-only API
                  /            \
      AI Software Developer   AI Open Source Contributor
      factory + generated     OSS discovery + contributions
      apps and previews       owned by its venture
```

## HQ owns
- Venture display metadata and registry records.
- HQ-owned activity/audit records.
- Company-level connection state and health indicators.
- Future adapter connection state, freshness, and high-level venture status.

## Ventures own
- Their business logic, storage, credentials, logs, workflows, and release lifecycle.
- All generated app details and previews remain in AI Software Developer.
- Open-source discovery and contribution workflows remain in AI Open Source Contributor.

## Current runtime
- FastAPI exposes `/api/health`, `/api/ventures`, and `/api/activity`.
- SQLite stores the HQ registry and HQ activity records. The path is configurable with `NEXORA_DB_PATH`.
- The dashboard detects the same-origin HQ API when available; static hosting remains clearly marked as foundation-only.
- HQ has a configurable read-only adapter for AI Software Developer status, with explicit health values, bounded timeouts, service-token auth, and stale/error states. The integration remains disconnected until the venture-side `/api/hq/status` endpoint is implemented and configured. AI Open Source Contributor has no adapter yet.

## Failure isolation
Each future adapter must fail independently. Show stale/error state and last successful timestamp; never silently present stale values as current. HTTP 200 alone is not proof of operational health. The health endpoint checks database readiness separately from venture integration readiness.

## Next architecture steps
Finish the dedicated authenticated status endpoint in AI Software Developer, validate the end-to-end adapter in a running environment, then implement the independent read-only adapter for AI Open Source Contributor. Keep cross-venture credentials isolated and do not add controls that mutate venture workloads.
