# Architecture (living document)

This file explains **how the Macro Chef monorepo fits together**. Update it whenever you add a deployment unit, database, cache, or auth mechanism.

## High-level layout

```text
apps/web     →  Browser (React / Vite)
apps/api     →  HTTP server (Hono on Node)
packages/domain →  Shared logic (no I/O): formulas, validation helpers
```

Target deployment shape (later): static hosting for `web`, Node process for `api`, managed **PostgreSQL** for persistence. Multi-user data must be scoped by authenticated **user id** on every domain query.

## Happy path (MVP)

1. Browser loads the SPA from `apps/web` (Vite dev server, typically `http://localhost:5173`).
2. User registers or logs in; **API** (`apps/api`, Hono) hashes the password, persists **`User`** in **PostgreSQL** via Prisma, and returns a **JWT access token** (`accessToken` in JSON).
3. The SPA stores the token (see `apps/web/src/lib/api.ts`) and sends **`Authorization: Bearer …`** on protected requests (`GET /api/auth/me`, `/api/meals`).
4. **Auth middleware** verifies the JWT and attaches **`userId`** to the request context.
5. Meal handlers read/write **`MealLog`** rows **only** for `context.userId` — e.g. `WHERE userId = …` — never trusting a client-supplied user id.

Timezone note: **`eatenAt`** is UTC; **`mealDate`** is the UTC calendar date used for list-by-day queries (see [MVP.md](MVP.md)).

## Packages

| Package | Responsibility |
|---------|----------------|
| `@macro-chef/web` | UI, routing, TanStack Query |
| `@macro-chef/api` | Routes, validation (Zod later), calls DB + external APIs |
| `@macro-chef/domain` | Pure functions: nutrition math, recommendation helpers — **no** `fetch`, no DB |

## Related docs

- [FEATURE_INVENTORY.md](FEATURE_INVENTORY.md) — product and API parity checklist  
- [milestones/M00-monorepo-scaffold.md](milestones/M00-monorepo-scaffold.md) — first milestone note  
