# Architecture (living document)

This file explains **how the Macro Chef monorepo fits together**. Update it whenever you add a deployment unit, database, cache, or auth mechanism.

## High-level layout

```text
apps/web     →  Browser (React / Vite)
apps/api     →  HTTP server (Hono on Node)
packages/domain →  Shared logic (no I/O): formulas, validation helpers
```

Target deployment shape (later): static hosting for `web`, Node process for `api`, managed **PostgreSQL** for persistence. Multi-user data must be scoped by authenticated **user id** on every domain query.

## Happy path (placeholder)

Until auth and DB land, the simplest trace is:

1. Browser loads the SPA from `apps/web`.
2. SPA calls `GET http://localhost:3000/health` on the API (configure `VITE_API_URL` when introduced).
3. API responds with JSON from `apps/api` without persistence.

Expand this section after register/login and Postgres exist: **cookie or JWT → middleware → handler → `WHERE user_id = …`**.

## Packages

| Package | Responsibility |
|---------|----------------|
| `@macro-chef/web` | UI, routing, TanStack Query (to be wired) |
| `@macro-chef/api` | Routes, validation (Zod later), calls DB + external APIs |
| `@macro-chef/domain` | Pure functions: nutrition math, recommendation helpers — **no** `fetch`, no DB |

## Related docs

- [FEATURE_INVENTORY.md](FEATURE_INVENTORY.md) — product and API parity checklist  
- [milestones/M00-monorepo-scaffold.md](milestones/M00-monorepo-scaffold.md) — first milestone note  
