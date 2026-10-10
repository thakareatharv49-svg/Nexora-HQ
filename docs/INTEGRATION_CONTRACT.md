# Read-only Integration Contract

Adapters normalize venture data into this conceptual shape. Example values are illustrative, not live data.

```json
{
  "venture_id": "ai-software-developer",
  "display_name": "AI Software Developer",
  "status": "unknown",
  "integration": {
    "state": "not_configured",
    "checked_at": null,
    "last_success_at": null,
    "source": null
  },
  "summary": {
    "active_workflows": null,
    "recent_events": null
  },
  "recent_activity": []
}
```

## Allowed
- Read a dedicated health/status endpoint and limited activity feed.
- Validate and normalize returned data.
- Cache data with explicit freshness metadata.
- Report failures without leaking secrets.

## Not allowed
- Start/stop missions or workers.
- Create, edit, merge or close pull requests.
- Publish products or deployments.
- Read arbitrary files or fetch secrets.
- Infer health from HTTP status alone.

## Status
Venture status: `operational`, `degraded`, `down`, `unknown`.
Integration state: `not_configured`, `connected`, `stale`, `error`.
Every successful record should include source and timestamp.
