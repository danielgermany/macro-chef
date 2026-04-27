# Milestone M01 — MVP: data model, auth, meal logging

## What shipped

- **Prisma schema** in `apps/api/prisma/schema.prisma`: `User` (unique email, password hash, optional display name), `MealLog` (FK to user, `eatenAt`, denormalized `mealDate`, name, optional macro fields).
- **Migrations** under `apps/api/prisma/migrations/`; deploy with `npx prisma migrate deploy` against `DATABASE_URL`.
- **Auth routes** (`apps/api/src/routes/auth.ts`): register, login, logout stub, me — JWT via `jose`, bcrypt password hashing.
- **Auth middleware** (`apps/api/src/middleware/auth.ts`): Bearer JWT → `userId` on context for protected routes.
- **Meal routes** (`apps/api/src/routes/meals.ts`): create, list by date, delete with ownership checks only via authenticated user id.
- **Web** (`apps/web`): Login, Register, Meals pages; TanStack Query; token in `localStorage`; API base URL from `VITE_API_URL` or default `http://localhost:3000`.
- **CORS**: API allows SPA origin `http://localhost:5173` with bearer tokens.

## Request flow (happy path)

1. User submits register or login; API returns JSON with **`accessToken`** (JWT).
2. SPA stores token and sends **`Authorization: Bearer <token>`** on `/api/auth/me` and `/api/meals`.
3. Middleware verifies JWT and sets **`userId`** on the request context.
4. Meal handlers use **only** `userId` from context for `INSERT` and `WHERE` clauses — no client-supplied tenant id.

## Verification

- Integration test `apps/api/src/meals.integration.test.ts` (skipped unless `DATABASE_URL` + valid `JWT_SECRET`): asserts **tenant isolation** — user B cannot read user A’s meals.

## Related

- [../MVP.md](../MVP.md)
