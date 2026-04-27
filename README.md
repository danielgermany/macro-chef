# Macro Chef

Monorepo for the rebuilt Macro Chef app. Product scope lives in [docs/FEATURE_INVENTORY.md](docs/FEATURE_INVENTORY.md). Architecture notes: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

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
```

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
