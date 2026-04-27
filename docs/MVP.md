# MVP v1: Users, auth, meal logging (“eaten”)

This milestone delivers Postgre-backed **users** and **meal logs**, **JWT authentication**, and minimal **API + web** flows to register, sign in, and record meals as eaten for the signed-in user only.

## Goals

- **Data model:** `User` and `MealLog` in PostgreSQL; each meal row has `userId` → `User` with cascade delete and index `(userId, mealDate)`.
- **Auth:** `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/logout` (client clears token), `GET /api/auth/me`. Passwords stored hashed (bcrypt); responses issue a **JWT** (`Authorization: Bearer`).
- **Meals:** Authenticated `POST /api/meals`, `GET /api/meals?date=YYYY-MM-DD`, optional `DELETE /api/meals/:id`. **Never** trust a client-supplied user id; identity comes only from the JWT middleware.

## Out of scope (defer)

Nutrition targets, recommendations, inventory, planner, budget, Spoonacular/USDA integrations — track against [FEATURE_INVENTORY.md](FEATURE_INVENTORY.md).

## Environment variables

| Variable | Where | Purpose |
|----------|-------|---------|
| `DATABASE_URL` | API (`apps/api`, root `.env`) | PostgreSQL connection string |
| `JWT_SECRET` | API | HS256 signing secret (≥ 32 chars in validation) |
| `PORT` | API | Listen port (default `3000`) |
| `VITE_API_URL` | Web (`apps/web`) | Base URL for API calls (e.g. `http://localhost:3000`; defaults in client code if unset) |

Copy `.env.example` at repo root and adjust. Run Postgres (see root `docker-compose.yml`), then from `apps/api`:

```bash
npx prisma migrate deploy
```

## API summary

| Method | Path | Notes |
|--------|------|-------|
| POST | `/api/auth/register` | Body: email, password, optional displayName |
| POST | `/api/auth/login` | Body: email, password |
| POST | `/api/auth/logout` | No-op server-side for JWT; client removes token |
| GET | `/api/auth/me` | Bearer required |
| POST | `/api/meals` | Bearer required; body includes name, optional macros, optional eatenAt |
| GET | `/api/meals?date=YYYY-MM-DD` | Bearer required; lists meals for that calendar **UTC** day |
| DELETE | `/api/meals/:id` | Bearer required; ownership enforced |

## Timezone rule

`eatenAt` is stored in UTC. **`mealDate`** is the UTC calendar date derived from `eatenAt` (or from client-supplied `eatenAt` when posting), so “today” queries align with UTC unless extended later.

## Related docs

- [milestones/M01-mvp-data-auth-meals.md](milestones/M01-mvp-data-auth-meals.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
