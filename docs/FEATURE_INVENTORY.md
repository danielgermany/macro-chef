# Feature inventory (app overhaul scope)

**Repository reset:** The codebase was removed to rebuild from scratch; this file was kept as the scope checklist. Path references below describe the **previous** layout (`backend/`, `frontend/`, `scripts/`, etc.) and remain useful for parity during a new implementation.

This document is the **canonical checklist** of what Macro Chef did before the reset: user-visible capabilities, web surfaces, REST API, shared Python domain layer, integrations, and persistence.

**Maintenance:** As you add routes, pages, or capabilities in the new stack, update this file so it stays the single source of truth for product scope.

**Related material (re-create or replace as needed):** project README, consolidated documentation, technical specification (schema), and OpenAPI at `/docs` once a new backend exists.

---

## 1. Purpose

| Audience | Use |
|-----------|-----|
| Product / design | Scope and parity checks for a new UX or IA. |
| Engineering | Trace “where is this implemented?” across UI → API → `scripts/` → SQLite. |

---

## 2. Executive feature list (user-facing)

Features from the product narrative (`README.md` § Features, pre-reset), tagged by **where they were primarily delivered**.

| Capability | Web | API | Scripts / other |
|------------|:---:|:---:|:-----------------|
| Smart nutrition tracking (macro/micro targets) | Yes | Yes | `NutritionCalculator` |
| Meal recommendations (macros, inventory, budget, prefs) | Yes | Yes | `MealRecommender` |
| Meal logging and daily progress vs targets | Yes | Yes | `MealTracker` |
| Inventory management and expiration awareness | Yes | Yes | `InventoryManager` |
| Budget tracking (weekly/monthly, trends) | Yes | Yes | `BudgetTracker` |
| Body composition / metrics over time | Yes | Yes | `UserProfileManager` |
| Online recipe search (Spoonacular) | Yes | Yes | `SpoonacularAPI`, recommender |
| Hybrid / API-assisted pricing | Partial / backend | Partial | Scripts (see spec) |
| USDA cross-check / nutrition validation | Backend | Yes | `USDAAPI`, recommender |
| Weekly meal planning (generate / save) | Yes | Yes | `WeeklyPlanner` |
| Shopping lists from plans | Yes | Yes | `ShoppingListGenerator` |
| Micronutrient gap analysis | Partial | Partial | `NutritionCalculator` / analytics |
| JWT auth (register, login, profile) | Yes | Yes | `UserProfileManager` |
| Natural-language / Claude orchestration | No | No | `claude_interface.py` (CLI-style; not wired to FastAPI) |

**UI vs depth notes**

- **Recipes:** Web focuses on search and detail modal; local template catalog is driven by backend/scripts.
- **Nutrition:** Targets and trends in UI; advanced micronutrient reporting may be stronger in scripts/spec than in every chart on `/nutrition`.
- **Inventory auxiliary routes:** `GET /api/inventory/expiring` and `GET /api/inventory/summary` are defined **after** `GET /api/inventory/{item_id}` in the router; in FastAPI, path `expiring` may be interpreted as `{item_id}`. Verify behavior before relying on those URLs in the overhaul.

---

## 3. Web application surface

Base: Vite + React; routes from `frontend/src/App.tsx`. API base: `frontend/src/services/api.ts` (`VITE_API_URL`, default `http://localhost:8000`).

| Path | Page | Primary user jobs | Main clients (services / hooks) |
|------|------|-------------------|-----------------------------------|
| `/login` | Login | Sign in | `AuthContext` → `api` |
| `/register` | Register | Create account | `AuthContext` → `api` |
| `/dashboard` | Dashboard | Today’s macros, meals, quick actions, weight trend | `useDailyProgress`, `useDeleteMeal`, `useUser` |
| `/meals` | MealTracker | Log meals, recommendations, history, export CSV | `mealService`, `export` utils |
| `/recipes` | Recipes | Search Spoonacular, view details | `RecipeSearch` → `recipeService` |
| `/nutrition` | Nutrition | Targets, trends, daily context | `nutritionService`, `mealService` |
| `/inventory` | Inventory | CRUD items, filters, export CSV | `inventoryService`, `export` utils |
| `/planner` | WeeklyPlanner | Generate week, save plan, shopping list | `useWeeklyPlanner` → `planService` |
| `/budget` | Budget | Weekly/monthly summaries, trends, categories | `useBudget` → `budgetService` |
| `/settings` | Settings | Profile, metrics, preferences, security | `userService`, `useUser`, `api` |

Layout / chrome: `frontend/src/components/layout/Layout.tsx`, sidebar routes aligned with the table above.

---

## 4. REST API inventory

Prefix `/api` from `backend/app/main.py`. **Depends on** lists the script-layer class from `backend/app/services/__init__.py` (or obvious dependency).

### Auth — `/api/auth`

| Method | Path | Purpose | Depends on |
|--------|------|---------|------------|
| POST | `/register` | Register user | `UserProfileManager` |
| POST | `/login` | OAuth2 form login | `UserProfileManager` |
| POST | `/login-json` | JSON login (web) | `UserProfileManager` |
| GET | `/me` | Current user (JWT) | `UserProfileManager` |
| PATCH | `/change-password` | Change password | `UserProfileManager` |
| PATCH | `/change-email` | Change email | `UserProfileManager` |

### Users — `/api/users`

| Method | Path | Purpose | Depends on |
|--------|------|---------|------------|
| POST | `/` | Create user (legacy / admin-style) | `UserProfileManager` |
| GET | `/{user_id}` | Get user profile | `UserProfileManager` |
| PATCH | `/{user_id}` | Update profile | `UserProfileManager` |
| POST | `/{user_id}/metrics` | Log body metrics | `UserProfileManager` |
| GET | `/{user_id}/metrics` | Metrics history | `UserProfileManager` |
| GET | `/{user_id}/progress` | Progress summary | `UserProfileManager` |

### Meals — `/api/meals`

| Method | Path | Purpose | Depends on |
|--------|------|---------|------------|
| POST | `/log` | Log a meal | `MealTracker` |
| GET | `/progress` | Daily progress | `MealTracker` |
| GET | `/history` | Meal history (filters) | `MealTracker` |
| GET | `/weekly-summary` | Weekly summary | `MealTracker` |
| DELETE | `/{meal_id}` | Delete meal log | `MealTracker` |
| PATCH | `/{meal_id}/rating` | Rate meal | `MealTracker` |
| GET | `/recommendations` | Meal recommendations | `MealRecommender` |

### Nutrition — `/api/nutrition`

| Method | Path | Purpose | Depends on |
|--------|------|---------|------------|
| POST | `/targets` | Generate/store targets | `NutritionCalculator` |
| GET | `/targets` | Today’s targets | `NutritionCalculator` |
| GET | `/targets/{target_date}` | Targets for date | `NutritionCalculator` |

### Inventory — `/api/inventory`

| Method | Path | Purpose | Depends on |
|--------|------|---------|------------|
| GET | `/` | List items (`user_id`, optional filters) | `InventoryManager` |
| POST | `/` | Add item | `InventoryManager` |
| GET | `/{item_id}` | Get item | `InventoryManager` |
| PATCH | `/{item_id}` | Update item | `InventoryManager` |
| DELETE | `/{item_id}` | Delete item | `InventoryManager` |
| POST | `/{item_id}/use` | Consume quantity | `InventoryManager` |
| GET | `/expiring` | Expiring soon | `InventoryManager` |
| GET | `/summary` | Summary stats | `InventoryManager` |

### Plans — `/api/plans`

| Method | Path | Purpose | Depends on |
|--------|------|---------|------------|
| POST | `/generate` | Generate weekly plan | `WeeklyPlanner` |
| POST | `/` | Save plan | `WeeklyPlanner` |
| GET | `/` | List saved plans | `WeeklyPlanner` |
| GET | `/{plan_id}` | Get plan | `WeeklyPlanner` |
| GET | `/{plan_id}/shopping-list` | Shopping list | `ShoppingListGenerator` |

### Budget — `/api/budget`

| Method | Path | Purpose | Depends on |
|--------|------|---------|------------|
| GET | `/weekly` | Weekly summary | `BudgetTracker` |
| GET | `/monthly` | Monthly summary | `BudgetTracker` |
| GET | `/trends` | Spending trends | `BudgetTracker` |
| GET | `/categories` | Category breakdown | `BudgetTracker` |

### Recipes — `/api/recipes`

| Method | Path | Purpose | Depends on |
|--------|------|---------|------------|
| GET | `/search` | Search (local + Spoonacular) | `MealRecommender` |
| GET | `/{recipe_id}` | Recipe details | `SpoonacularAPI` |

### Meta (no `/api` prefix)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | API welcome |
| GET | `/health` | Health check |

---

## 5. Domain / script layer (`scripts/`)

Python package `scripts` (editable install from repo root per `requirements.txt`) held business logic consumed by FastAPI via `backend/app/services/__init__.py`.

### Wired into the API (`app.services`)

| Module | Class / entry | Role |
|--------|----------------|------|
| `scripts/user_profile.py` | `UserProfileManager` | Users, auth fields, metrics, progress |
| `scripts/nutrition_calculator.py` | `NutritionCalculator` | Targets, micronutrients |
| `scripts/meal_tracker.py` | `MealTracker` | Logging, progress, history |
| `scripts/meal_recommender.py` | `MealRecommender` | Recommendations, recipe search orchestration |
| `scripts/inventory_manager.py` | `InventoryManager` | Inventory CRUD, expiry, summary |
| `scripts/weekly_planner.py` | `WeeklyPlanner` | Plan generation and persistence |
| `scripts/shopping_list.py` | `ShoppingListGenerator` | Lists from plans |
| `scripts/budget_tracker.py` | `BudgetTracker` | Spending summaries and trends |
| `scripts/spoonacular_api.py` | `SpoonacularAPI` | External recipes / nutrition |
| `scripts/usda_api.py` | `USDAAPI` | USDA FoodData Central |

### Auxiliary / CLI / tooling (not in `app.services` re-export)

| Path | Role |
|------|------|
| `scripts/db_setup.py` | Initialize SQLite schema |
| `scripts/db_manager.py` | Low-level DB access |
| `scripts/analytics.py` | Insights / reports |
| `scripts/claude_interface.py` | Claude-driven orchestration (not exposed as REST) |
| `scripts/populate_meal_templates.py` | Seed / template data |
| `scripts/test_online_recipe_integration.py` | Integration checks |
| `scripts/migrations/` | One-time SQLite migrations (`scripts/migrations/README.md`) |
| `scripts/dev/` | Local helpers (e.g. restart backend) |

---

## 6. Integrations and configuration

| Integration | Config / secrets | Used from |
|-------------|------------------|-----------|
| Spoonacular | `SPOONACULAR_API_KEY` — `backend/app/config.py`, `config/config.py` | `SpoonacularAPI`, meal recommender, recipes router |
| USDA FoodData Central | `USDA_API_KEY` (optional) | `USDAAPI`, validation paths in recommender/nutrition flows per codebase |
| JWT | `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES` | `backend/app/auth/` |
| CORS | `CORS_ORIGINS` | `backend/app/config.py` |
| SQLite | `DATABASE_URL` (default relative SQLite file) | `backend/app/database.py` |
| Frontend API URL | `VITE_API_URL` | Vite env → `frontend/src/services/api.ts` |

RDA and nutrition constants for calculators: `config/config.py`.

---

## 7. Data and persistence

- **Engine:** SQLite (path defaults under repo `database/`; see `DATABASE_URL` in backend settings).
- **Full schema, tables, and field-level spec:** pre-reset `SPECIFICATION.md` at repo root — do not duplicate here; recreate or restore from git history if needed.

**Core entities (migration checklist for an overhaul)**

- [ ] User profile (identity, goals, prefs, equipment, budget)
- [ ] Auth fields on user (email, password hash) where applicable
- [ ] Body metrics history
- [ ] Nutrition targets (by date)
- [ ] Meal logs and meal templates / recipes
- [ ] Inventory items
- [ ] Weekly plans (saved) and linkage to shopping lists
- [ ] Budget / purchase / spending records (as defined in spec)
- [ ] Cached or auxiliary JSON (`data/` per spec)

---

## 8. Overhaul appendix

### Known gaps / tech debt (seed list — extend as needed)

- Inventory router: static paths like `/expiring` and `/summary` may conflict with `/{item_id}` depending on registration order; confirm and fix if broken.
- Backend tests: occasional SQLite connection `ResourceWarning` on teardown; close connections explicitly if tightening CI.
- Pydantic v2: `class Config` deprecation on several schemas (migrate to `ConfigDict` when touching those files).

### Open product questions

- (Add bullets: multi-household, mobile/offline, subscription billing, etc.)

### OpenAPI

- With the backend running: `http://localhost:8000/docs` for interactive schemas generated from FastAPI.
