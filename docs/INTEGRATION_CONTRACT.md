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


## AI Software Developer status endpoint

HQ's first adapter is configured with `NEXORA_AI_SOFTWARE_DEVELOPER_URL` and `NEXORA_AI_SOFTWARE_DEVELOPER_TOKEN`. It performs only an authenticated `GET /api/hq/status` request and never calls mission mutation, repository, or publishing routes.

The source response must be JSON with all of these fields:

- `service`: exactly `ai-software-developer`
- `status`: explicit `operational`, `degraded`, `down`, or `unknown`
- `active_missions`, `queued_missions`, `completed_missions`, `blocked_missions`: non-negative integers
- `updated_at`: ISO-8601 timestamp for the source snapshot

HQ uses a short request timeout, rejects redirects, validates the payload, and never treats an HTTP 200 response by itself as proof of health. The dashboard shows both the check time and source snapshot time. A source snapshot older than two minutes is marked stale. The service token is stored only in server-side environment configuration and is never returned to the browser.

The HQ-side adapter is implemented first; end-to-end live monitoring remains incomplete until the dedicated source endpoint is available and configured in AI Software Developer.
