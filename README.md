# Macro Chef

Monorepo for the rebuilt Macro Chef app. Product scope lives in [docs/FEATURE_INVENTORY.md](docs/FEATURE_INVENTORY.md). Architecture notes: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). MVP v1 (users, JWT auth, meal logging): [docs/MVP.md](docs/MVP.md).

## Structure

| Path | Role |
|------|------|
| `apps/web` | React (Vite) SPA |
| `apps/api` | HTTP API (Hono) |
| `packages/domain` | Shared pure TypeScript domain logic (nutrition, planning, etc.) |

## Prerequisites

- Node.js 20+

## Setup

```bash
npm install
cp .env.example .env   # set DATABASE_URL, JWT_SECRET (≥32 chars), PORT if needed
docker compose up -d    # optional: local PostgreSQL (see docker-compose.yml)
cd apps/api && npx prisma migrate deploy && cd ../..
```

The API reads env from the repo root or `apps/api/.env`. For the web app, set `VITE_API_URL` (e.g. `http://localhost:3000`) if not using the default in code.

## Development

From repository root:

```bash
# Terminal 1 — API (default http://localhost:3000)
cd apps/api && npm run dev

# Terminal 2 — Web (default http://localhost:5173)
cd apps/web && npm run dev
```

## Builds

```bash
npm run build
```
