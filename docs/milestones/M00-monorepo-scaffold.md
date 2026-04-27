# Milestone M00 — Monorepo scaffold

## What we built

- **npm workspaces** at the repo root so `apps/*` and `packages/*` install together.
- **`apps/web`**: Vite + React + TypeScript — placeholder UI.
- **`apps/api`**: Hono + `@hono/node-server` — `/` and `/health` routes on port 3000 by default.
- **`packages/domain`**: empty shared package for future nutrition/planning logic (pure TS, no side effects).

## Why these choices

| Choice | Reason |
|--------|--------|
| Workspaces | One `npm install`, shared tooling, clear boundaries between UI and API. |
| Vite | Fast dev server for the SPA; aligns with the tech stack plan. |
| Hono | Small TypeScript-first HTTP layer; easy to add Zod + OpenAPI later. |
| `packages/domain` | Keeps testable rules separate from HTTP and React so calculators stay reusable. |

## Map to FEATURE_INVENTORY

Not feature-complete yet — this milestone only establishes **delivery skeleton**. Later milestones attach routes from [FEATURE_INVENTORY.md](../FEATURE_INVENTORY.md) §4 (REST) and pages from §3.

## Try it

```bash
npm install
cd apps/api && npm run dev    # GET http://localhost:3000/health
cd apps/web && npm run dev    # open http://localhost:5173
```

## Next

- PostgreSQL + ORM + `User` model with tenant-safe FKs.
- Auth (session or JWT) and `/api/me`.
- Wire `web` → `api` with env-based base URL and CORS.
