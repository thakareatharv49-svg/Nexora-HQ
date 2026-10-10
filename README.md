# Nexora HQ

Nexora HQ is the parent-company control center for Nexora's ventures. It is a separate application and repository, not the execution engine for the ventures themselves.

## Ownership boundaries

- **Nexora HQ** owns the venture registry, company-level visibility, high-level activity, connection health and configuration.
- **AI Software Developer** owns autonomous software project execution, generated applications, previews and its internal workflows.
- **AI Open Source Contributor** owns its own open-source discovery and contribution workflows.
- HQ will monitor venture-level status through read-only adapters after each venture is stable. Generated apps remain managed by AI Software Developer.

## Run the dashboard locally

From the repository root:

```bash
python -m http.server 4173 --directory apps/web
```

Open [http://localhost:4173](http://localhost:4173).

The static interface currently runs in **foundation mode**. It marks external ventures as not connected and labels setup records as illustrative. It does not fabricate live status, metrics or external activity.

## Validate the static dashboard

Requires Node.js 22 or compatible modern Node.js:

```bash
node --check apps/web/app.js
node --test tests/*.test.cjs
```

GitHub Actions runs these checks for pull requests and pushes to the main and feature branches.

## Repository structure

- `apps/web/` — responsive dashboard: Overview, Venture Registry, Activity and Settings.
- `docs/` — architecture, integration contract, security and roadmap.
- `schemas/` — example normalized venture status payload; not live data.
- `tests/` — static dashboard regression tests.
- `.github/workflows/` — CI validation and GitHub Pages deployment workflow.

## Security principles

Never put tokens or credentials in browser code. Future venture adapters must run server-side, use least-privilege read-only access, apply timeouts, report source timestamps and freshness, and isolate upstream failures. HQ must not execute, mutate or take ownership of venture workloads.

## Delivery status

A workflow file is not proof of a successful deployment. Check the repository's Actions tab for verified CI and Pages results. Backend persistence, authentication, operational monitoring and venture integrations are future milestones tracked in [the roadmap](docs/ROADMAP.md).
