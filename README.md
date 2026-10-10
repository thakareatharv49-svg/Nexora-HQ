# Nexora HQ

Nexora HQ is the parent-company control center for Nexora's ventures. It is separate from each venture repository.

## Boundaries
- **Nexora HQ**: venture registry, cross-venture status, high-level activity, integration freshness.
- **AI Software Developer**: autonomous factory, mission execution, generated applications and previews.
- **AI Open Source Contributor**: open-source discovery and contribution workflows.
- HQ monitors ventures, not every generated app, and is read-only by design.

## Run the dashboard
From the repository root:
```bash
python -m http.server 4173 --directory apps/web
``
Open http://localhost:4173.

The dashboard is a static foundation. It clearly marks integrations as unconnected; it does not invent live data.

## Structure
- `apps/web/`: responsive dashboard shell.
- `docs/`: architecture, integration contract, security and roadmap.
- `schemas/`: example normalized venture status payload.

## Security
Never put tokens in browser code. Future adapters must be server-side, read-only, time-bounded, and report source timestamps and freshness.
