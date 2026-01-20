# Macro Chef - Complete Documentation

**Version:** 2.0  
**Last Updated:** January 2025

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Quick Start Guide](#quick-start-guide)
3. [GUI Application](#gui-application)
4. [Technical Specification](#technical-specification)
5. [Web Migration Plan](#web-migration-plan)
6. [Testing](#testing)
7. [Implementation Details](#implementation-details)
8. [Features & Integrations](#features--integrations)
9. [Backend API Setup](#backend-api-setup)
10. [Frontend Setup](#frontend-setup)

---

## Project Overview

### What is Macro Chef?

Macro Chef is an intelligent meal planning system that helps you maintain nutrition goals, minimize food waste, support athletic performance, and manage grocery budgets through smart recommendations and comprehensive tracking.

### Core Functionality

- **Smart Nutrition Tracking**: Automatically calculate daily macro and micronutrient targets based on your body metrics and goals (bulk/cut/maintain/recomp)
- **Intelligent Meal Recommendations**: AI-powered suggestions based on remaining macros, inventory, budget, preferences, and meal history with automatic online recipe search fallback
- **Meal Logging & Progress**: Track meals throughout the day with real-time progress vs targets
- **Inventory Management**: Track food on hand with expiration alerts and location-based organization
- **Budget Tracking**: Monitor grocery spending with weekly/monthly summaries, trends, and category breakdowns
- **Body Composition Tracking**: Log weight, body fat %, and measurements with progress analysis

### Advanced Features

- **Online Recipe Search**: Automatically searches Spoonacular when local database has <5 meals, with price cross-referencing and nutrition validation
- **Price Cross-Referencing**: Hybrid pricing using 70% shopping history + 30% API for realistic cost estimates
- **Nutrition Validation**: Cross-validates online recipes with USDA database, flags discrepancies >10%
- **Selective Recipe Caching**: Auto-saves online recipes to database when rated ≥3 stars
- **Weekly Meal Planning**: Generate complete 7-day meal plans with automatic recommendations and cost estimates
- **Shopping List Generation**: Smart shopping lists that check inventory and aggregate ingredients
- **Micronutrient Analysis**: Detect deficiencies in 9 key micronutrients with food recommendations
- **Analytics & Insights**: Comprehensive progress reports, adherence tracking, and spending analysis
- **Recipe Library**: Store and rate recipes with complete nutrition data and ingredient lists

### Tech Stack

- **Database**: SQLite (13 tables)
- **Backend**: Python 3.8+
- **APIs**: Spoonacular (recipes/nutrition), USDA FoodData Central (nutrition)
- **Interface**: Unified CLI with natural language support + GUI application (tkinter)
- **Web (New)**: FastAPI backend + React frontend (see [Web Migration Plan](#web-migration-plan))

### Key Principles

- **Cheap**: Budget-conscious recommendations
- **Fast**: Quick meal suggestions and prep
- **Easy**: Simple recipes, minimal complexity
- **Nutritious**: Macro and micronutrient optimization

---

## Quick Start Guide

### First-Time Setup

#### 1. Installation

```bash
# Clone and navigate
git clone <your-repo-url>
cd macro-chef

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

#### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys (optional but recommended)
# Get Spoonacular API key: https://spoonacular.com/food-api
```

#### 3. Initialize Database & Create Profile

```bash
# Initialize database
python scripts/db_setup.py

# Populate meal library (28 meals)
python scripts/populate_meal_templates.py

# Create your user profile (interactive)
python scripts/user_profile.py --create
```

You'll be asked:
- Name, age, sex
- Height (inches) and weight (lbs)
- Body fat % (optional but recommended)
- Goal: `cut`, `bulk`, `maintain`, or `recomp`
- Activity level: `sedentary`, `light`, `moderate`, `active`, `very_active`
- Training days per week (0-7)
- Cooking skill: `beginner`, `intermediate`, `advanced`
- Weekly grocery budget (USD)

**Example:**
```
Name: John
Age: 28
Sex: M
Height: 72 inches (6'0")
Weight: 180 lbs
Body fat: 15%
Goal: cut
Activity: moderate
Training days: 5
Cooking skill: intermediate
Weekly budget: $100
```

### Daily Workflow

#### Morning Check-in
```bash
python scripts/claude_interface.py daily
```

This shows:
- Today's nutrition targets
- Current progress
- Expiring inventory items
- Budget status
- Next meal recommendation

#### Log Your Meals

**Quick log:**
```bash
python scripts/meal_tracker.py --log \
  --name "Protein Oatmeal" \
  --calories 380 \
  --protein 30 \
  --carbs 48 \
  --fat 8 \
  --meal-time breakfast
```

**Interactive log** (searches meal templates):
```bash
python scripts/claude_interface.py log-meal
```

#### Get Meal Recommendations
```bash
# Auto-detect next meal
python scripts/claude_interface.py recommend

# Specific meal
python scripts/meal_recommender.py --recommend dinner --count 5

# With constraints
python scripts/meal_recommender.py --recommend lunch --max-time 20 --budget 4.00
```

#### Check Progress
```bash
# Dashboard overview
python scripts/claude_interface.py dashboard

# Today's progress
python scripts/meal_tracker.py --progress

# Weekly summary
python scripts/meal_tracker.py --weekly --days 7
```

### Weekly Planning

#### Plan Your Week
```bash
python scripts/claude_interface.py plan-week
```

This will:
1. Generate 7-day meal plan optimized for your goals
2. Show nutrition summary
3. Estimate weekly cost
4. Offer to save the plan
5. Generate shopping list

#### View Saved Plans
```bash
# List recent plans
python scripts/weekly_planner.py --list

# View specific plan
python scripts/weekly_planner.py --view 1

# Generate shopping list from saved plan
python scripts/weekly_planner.py --shopping-list 1
```

### Inventory & Shopping

#### Add to Inventory
```bash
python scripts/inventory_manager.py --add \
  --name "Chicken breast" \
  --quantity 2.5 \
  --unit lbs \
  --category protein \
  --location freezer \
  --days-until-expire 30
```

#### Check Inventory
```bash
# List all items
python scripts/inventory_manager.py --list

# Check expiring soon (7 days)
python scripts/inventory_manager.py --expiring --days 7

# Search
python scripts/inventory_manager.py --search chicken
```

#### Shopping Lists
```bash
# Generate from meals (by template ID)
python scripts/shopping_list.py --generate 1 2 3 --servings 1 2 1

# View shopping history
python scripts/shopping_list.py --history --days 30
```

### Budget Tracking

```bash
# Weekly budget
python scripts/budget_tracker.py --weekly

# Monthly budget
python scripts/budget_tracker.py --monthly

# Spending trends
python scripts/budget_tracker.py --trends --weeks 4

# Category breakdown
python scripts/budget_tracker.py --categories --days 30

# Price history for item
python scripts/budget_tracker.py --price-history "chicken"
```

### Analytics & Insights

```bash
# Comprehensive progress report
python scripts/analytics.py --progress-report --days 30

# Check for micronutrient deficiencies
python scripts/analytics.py --deficiencies --days 7 --save-alerts

# View active alerts
python scripts/analytics.py --alerts
```

Tracks 9 key micronutrients:
- Vitamin D, C, A
- Calcium, Iron, Magnesium, Potassium, Zinc
- Omega-3 fatty acids

### Tips & Best Practices

1. **Start Simple**
   - Use the unified CLI (`claude_interface.py`) for common tasks
   - Log meals consistently for accurate tracking
   - Check inventory before shopping

2. **Weekly Routine**
   - **Sunday**: Plan the week, generate shopping list
   - **Monday**: Go shopping, update inventory
   - **Daily**: Morning check-in, log meals, track progress
   - **Weekly**: Review progress report, adjust goals

3. **Meal Prep**
   - Filter for `batch-friendly` meals
   - Cook 2-3 days worth on Sunday
   - Update inventory after prep

4. **Budget Management**
   - Set realistic weekly budget ($75-150 for one person)
   - Check trends monthly
   - Look for budget-friendly meals (tagged `budget`)

5. **Body Metrics**
   ```bash
   # Log weight weekly
   python scripts/user_profile.py --log-metrics --weight 178 --body-fat 14.5
   
   # View progress
   python scripts/user_profile.py --progress --days 30
   ```

---

## GUI Application

### Quick Start (5-Minute Setup)

#### Step 1: Launch the GUI
```bash
# macOS/Linux
./launch_gui.sh

# Windows
launch_gui.bat

# Or directly:
python3 gui_app.py
```

#### Step 2: Create Your Profile
1. Click the **"Profile"** tab
2. Fill in your information (name, age, sex, height, weight, body fat %, goal, activity, training days, budget)
3. Click **"Save Profile"**
4. Click **"Generate Targets"**

You now have personalized daily nutrition targets!

#### Step 3: View Your Dashboard
1. Click the **"Dashboard"** tab
2. See your daily targets:
   - Total calories
   - Protein, carbs, fat, fiber
   - Quick stats

#### Step 4: Search Some Recipes
1. Click the **"Search Recipes"** tab
2. Type what you want (e.g., "chicken breast")
3. Adjust filters if needed (Max Calories, Min Protein, Max Prep Time)
4. Click **"Search"**

Browse results and save favorites!

### GUI Features

#### Dashboard Tab
- View daily nutrition targets (calories, protein, carbs, fat, fiber)
- Quick stats overview (meal count, inventory, goals)
- One-click refresh

#### Profile Tab
- Create and edit user profiles
- Set personal metrics (age, sex, height, weight, body fat %)
- Configure fitness goals (bulk, cut, maintain, recomp)
- Set activity level and training frequency
- Weekly budget tracking
- Generate daily nutrition targets

#### Meals Tab
- Browse saved meal templates
- View nutrition information (calories, macros)
- Get AI-powered meal recommendations based on your targets
- Filter by meal type

#### Inventory Tab
- Track food inventory
- Add items with quantity, category, and location
- Monitor expiration dates
- Search and filter items

#### Search Recipes Tab
- Search 570,000+ online recipes via Spoonacular API
- Filter by calories, protein, and prep time
- USDA nutrition validation
- See detailed nutrition breakdown
- Save recipes to your meal library

### Common Tasks

#### Add Food to Inventory
1. Go to **"Inventory"** tab
2. Fill in the form (Item Name, Quantity, Unit, Category, Location, Days Until Expiry)
3. Click **"Add Item"**

#### Get Meal Recommendation
1. Make sure you have:
   - Profile created
   - Targets generated
   - Some meals in database
2. Go to **"Meals"** tab
3. Click **"Get Recommendation"**
4. See personalized suggestion!

#### Update Your Weight
1. Go to **"Profile"** tab
2. Update weight value
3. Click **"Save Profile"**
4. Click **"Generate Targets"** to recalculate

### Understanding Your Targets

**Bulk** (Muscle gain):
- Calories: TDEE + 300
- Protein: 1.0g per lb bodyweight
- Focus: Gradual weight gain

**Cut** (Fat loss):
- Calories: TDEE - 500
- Protein: 1.2g per lb (preserve muscle)
- Focus: Sustainable deficit

**Maintain** (Maintenance):
- Calories: TDEE (no change)
- Protein: 0.8g per lb
- Focus: Consistency

**Recomp** (Body recomposition):
- Calories: TDEE (maintenance)
- Protein: 1.1g per lb (elevated)
- Focus: Build muscle, lose fat simultaneously

### Troubleshooting

**"No user profile loaded"**
→ Go to Profile tab, fill information, click Save

**"Please generate targets first"**
→ Go to Profile tab, click "Generate Targets"

**"No suitable meals found"**
→ Search recipes to add meals to database

**Search returns no results**
→ Check:
- Internet connection
- API keys in .env file
- Filters aren't too restrictive
- API quota not exceeded (150 free/day)

**GUI looks weird**
→ Update to latest tkinter or try different Python version

**Can't add inventory**
→ Ensure database initialized: `python3 scripts/db_setup.py`

### Keyboard Shortcuts

- **Tab**: Navigate between fields
- **Enter**: Submit forms
- **Refresh buttons**: Update data without restarting

---

## Technical Specification

### System Architecture

#### High-Level Flow
```
User → Claude Interface → Python Scripts → SQLite Database
                       ↓
                  External APIs (Spoonacular, USDA)
```

#### Directory Structure
```
macro-chef/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── database/
│   ├── meal_planner.db          # SQLite database (created by setup)
│   └── backups/                 # Automatic backups
│
├── config/
│   └── config.py                # Configuration management
│
├── scripts/
│   ├── db_setup.py              # Initialize database schema
│   ├── db_manager.py            # Base database operations
│   ├── user_profile.py          # User profile management
│   ├── nutrition_calculator.py  # Calculate macro/micro targets
│   ├── inventory_manager.py     # Inventory CRUD operations
│   ├── meal_recommender.py      # Intelligent meal suggestions
│   ├── meal_tracker.py          # Log meals and progress
│   ├── shopping_list.py         # Generate shopping lists
│   ├── budget_tracker.py        # Track spending
│   ├── spoonacular_api.py       # Spoonacular API integration
│   ├── usda_api.py              # USDA nutrition data
│   ├── analytics.py             # Generate insights and reports
│   └── claude_interface.py      # Main orchestrator for Claude
│
├── data/
│   ├── meal_templates.json      # Starter meal templates
│   └── nutrition_cache.json     # Cached nutrition data
│
├── backend/                     # FastAPI backend (new)
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── routers/
│   │   ├── schemas/
│   │   └── services/
│   └── requirements.txt
│
├── frontend/                    # React frontend (new)
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── types/
│   └── package.json
│
└── tests/
    ├── test_database.py
    ├── test_nutrition.py
    ├── test_api.py
    └── test_gui.py
```

### Database Schema

**13 Tables:**
1. `user_profile` - User metrics, goals, preferences
2. `body_metrics_history` - Weight, body fat tracking
3. `daily_nutrition_targets` - Daily macro/micro targets
4. `daily_nutrition_progress` - Meal logging
5. `inventory` - Food items on hand
6. `meal_templates` - Recipe library
7. `meal_ingredients` - Recipe ingredients
8. `shopping_history` - Purchase records
9. `budget_tracking` - Budget summaries
10. `food_nutrition_cache` - API data cache
11. `weekly_meal_plans` - Saved weekly plans
12. `weekly_meal_plan_items` - Plan meals
13. `micronutrient_deficiency_alerts` - Deficiency tracking

See [SPECIFICATION.md](SPECIFICATION.md) for complete schema details with SQL definitions.

### Key Calculations

#### BMR (Basal Metabolic Rate)
- **Katch-McArdle**: `370 + (21.6 × lean_body_mass_kg)` (if body fat % known)
- **Mifflin-St Jeor**: Gender-specific formula based on weight, height, age

#### TDEE (Total Daily Energy Expenditure)
- Applies activity multipliers (1.2x to 1.9x) to BMR
- Adjusts for training days

#### Macro Targets
- **Bulk**: 1.0g protein/lb bodyweight
- **Cut**: 1.2g protein/lb (muscle preservation)
- **Maintain**: 0.8g protein/lb
- **Recomp**: 1.1g protein/lb

#### Micronutrients
- RDA-based targets with athlete multipliers
- Tracks 9 key micronutrients

---

## Web Migration Plan

### Executive Summary

This document outlines a phased migration strategy to transform Macro Chef from a Tkinter desktop application to a modern web application using FastAPI (backend) and React (frontend). The migration preserves existing business logic while adding scalability, multi-user support, and a responsive UI.

**Estimated Timeline:** 4-6 weeks (part-time) or 2-3 weeks (full-time)

**Key Principles:**
- Preserve existing Python business logic (scripts/)
- Incremental migration (can run old + new simultaneously)
- Feature parity first, then enhancements

### Architecture Overview

#### Current Architecture (Tkinter)
```
┌─────────────────────────────────────────────────────┐
│                   gui_app.py                        │
│              (Tkinter GUI Layer)                    │
└──────────────────────┬──────────────────────────────┘
                       │ Direct Python calls
┌──────────────────────▼──────────────────────────────┐
│                  scripts/                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │UserProfile  │ │MealTracker  │ │Inventory    │   │
│  │Manager      │ │             │ │Manager      │   │
│  └─────────────┘ └─────────────┘ └─────────────┘   │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│            SQLite Database (local)                    │
└──────────────────────────────────────────────────────┘
```

#### New Architecture (Web)
```
┌─────────────────────────────────────────────────────┐
│              React Frontend (Browser)               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │Dashboard │ │Meals     │ │Inventory │            │
│  └──────────┘ └──────────┘ └──────────┘            │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP/REST API
┌──────────────────────▼──────────────────────────────┐
│            FastAPI Backend (Python)                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │Routers   │ │Schemas   │ │Services  │            │
│  └──────────┘ └──────────┘ └──────────┘            │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│         Same scripts/ (business logic)                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │UserProfile  │ │MealTracker  │ │Inventory    │   │
│  │Manager      │ │             │ │Manager      │   │
│  └─────────────┘ └─────────────┘ └─────────────┘   │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│      SQLite (dev) / PostgreSQL (prod)                 │
└──────────────────────────────────────────────────────┘
```

### Migration Phases

#### Phase 1: Backend Foundation (Week 1) [COMPLETE]
- [x] FastAPI project setup
- [x] Database connection (SQLAlchemy)
- [x] Pydantic schemas for all entities
- [x] Basic CRUD routers
- [x] CORS configuration

#### Phase 2: Core API Endpoints (Week 2) [COMPLETE]
- [x] User management endpoints
- [x] Meal tracking endpoints
- [x] Nutrition targets endpoints
- [x] Inventory management endpoints
- [x] Meal recommendations endpoint
- [x] Weekly planning endpoints
- [x] Budget tracking endpoints

#### Phase 3: React Frontend Setup (Week 3) [COMPLETE]
- [x] Vite + React + TypeScript setup
- [x] TailwindCSS configuration
- [x] React Router setup
- [x] React Query for data fetching
- [x] API client (Axios)
- [x] Layout components (Header, Sidebar)
- [x] Basic page structure

#### Phase 4: Frontend Feature Implementation (Week 3-4) [COMPLETE]
- [x] Dashboard page with macro progress
- [x] Meal Tracker page with logging form
- [x] Nutrition page with targets
- [x] Inventory page with CRUD operations
- [x] Service layer for API calls
- [x] Custom React hooks

#### Phase 5: Authentication & Multi-User (Week 4) - PENDING
- [ ] JWT authentication
- [ ] User registration/login
- [ ] Protected routes
- [ ] User context provider

#### Phase 6: Testing & Deployment (Week 5) - PENDING
- [ ] Backend API tests
- [ ] Frontend component tests
- [ ] E2E tests
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Production deployment

### Tech Stack Details

**Backend:**
- FastAPI 0.104+
- SQLAlchemy 2.0+ (ORM)
- Pydantic 2.0+ (validation)
- Uvicorn (ASGI server)
- Alembic (migrations)

**Frontend:**
- React 18+
- TypeScript 5+
- Vite (build tool)
- TailwindCSS 3.4+
- React Router 6+
- React Query (TanStack Query)
- Axios (HTTP client)
- Lucide React (icons)

**Database:**
- SQLite (development)
- PostgreSQL (production)

### API Specification

See `MIGRATION_PLAN.md` for complete API endpoint documentation.

---

## Testing

### Web Application Testing

#### Quick Start Testing

**Prerequisites:**
1. Backend server running on http://localhost:8000
2. Frontend server running on http://localhost:5173
3. Database initialized (automatic on first run)

**Quick Test Checklist (15 minutes):**

1. **Authentication (2 min)**
   - Register new user at /register
   - Login with credentials
   - Verify redirect to dashboard
   - Check user name in header

2. **Dashboard (1 min)**
   - View macro progress cards (0/0 initially)
   - View empty meals list
   - View weight chart (empty if no metrics)

3. **Nutrition Setup (2 min)**
   - Navigate to Nutrition page
   - Generate targets
   - Verify targets displayed
   - Check macro distribution chart
   - Check nutrition trend chart

4. **Meal Logging (3 min)**
   - Navigate to Meal Tracker
   - Log a manual meal (chicken, 250 cal, 50g protein)
   - Verify meal appears in today's list
   - Check dashboard updates
   - Search for online recipe
   - Add recipe to meal log
   - View recipe details

5. **Meal History (2 min)**
   - Click History button
   - Verify meals displayed
   - Test search filter
   - Test date range filter
   - Export to CSV

6. **Inventory (2 min)**
   - Navigate to Inventory
   - Add an item
   - Verify item appears
   - Check expiring items alert (if applicable)
   - Export to CSV

7. **Weekly Planner (2 min)**
   - Navigate to Weekly Planner
   - Generate a weekly plan
   - Verify plan displayed
   - Check daily meals
   - View shopping list
   - Save plan

8. **Budget (1 min)**
   - Navigate to Budget
   - View weekly summary
   - Toggle to monthly
   - Check spending trends chart
   - Check category breakdown

9. **Settings (2 min)**
   - Navigate to Settings
   - Update profile info
   - Log body metrics
   - View metrics history
   - Change password (Security tab)
   - Change email (Security tab)
   - Export body metrics CSV

#### Backend API Testing

**Test Files:**
- `backend/tests/test_auth.py` - Authentication endpoints
- `backend/tests/test_meals.py` - Meal logging and tracking
- `backend/tests/test_users.py` - User management

**Running Tests:**

```bash
# Run all backend tests
cd backend
pytest tests/ -v

# Run specific test file
pytest tests/test_auth.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

**Test Configuration:**
- Tests use temporary SQLite databases
- Authentication tests verify JWT token creation and validation
- Meal tests verify logging, progress tracking, and history
- User tests verify profile management and body metrics

### Legacy GUI Testing (Deprecated)

The following test files are for the legacy Tkinter GUI application and are no longer maintained:

### Running Tests

#### Run All Tests
```bash
pytest tests/ -v
```

#### Run Specific Test File
```bash
pytest tests/test_database.py -v
pytest tests/test_nutrition.py -v
pytest tests/test_api.py -v
pytest tests/test_gui.py -v
```

#### Run with Coverage Report
```bash
pytest tests/ --cov=scripts --cov-report=html
```

Then open `htmlcov/index.html` in your browser to see detailed coverage.

#### Run Tests in Parallel (faster)
```bash
pip install pytest-xdist
pytest tests/ -v -n auto
```

### Test Configuration

#### Mock Tests vs Live Tests

By default, API tests use mocked responses and don't require API keys. To run live API tests:

1. Set up your `.env` file with API keys:
```bash
SPOONACULAR_API_KEY=your_key_here
USDA_API_KEY=your_key_here  # Optional
```

2. Run tests with live API enabled:
```bash
pytest tests/test_api.py -v
```

Live tests are automatically skipped if API keys are not configured.

#### Temporary Test Database

All tests use temporary SQLite databases that are:
- Created fresh for each test
- Isolated from your production database
- Automatically deleted after tests complete

Your actual `database/meal_planner.db` is never touched during testing.

### GUI Test Summary

**Overall: 11/23 tests passing (48%)**

The passing tests validate core functionality:
- Button callback existence
- Form validation
- Error handling
- Warning messages for missing inputs
- Status bar updates

**Test Categories:**
1. Profile Tab Buttons (3/6 passing)
2. Dashboard Tab Buttons (1/2 passing)
3. Meals Tab Buttons (2/4 passing)
4. Inventory Tab Buttons (1/3 passing)
5. Search Recipes Tab Buttons (1/4 passing)
6. General Button Tests (3/4 passing)

---

## Implementation Details

### Search Online Recipes Format Transformation

**Problem:** The `_search_online_recipes` method in `MealRecommender` returns meals in meal template format, but the GUI expects Spoonacular API format.

**Solution:** Added format transformation in `scripts/meal_recommender.py` to convert meal template format to API-like format for GUI compatibility.

**Location:** `scripts/meal_recommender.py` - `_search_online_recipes` method

### Public `search_online_recipes` Method

**Problem:** The `MealRecommender` class had a private `_search_online_recipes` method but no public method for the GUI to call directly.

**Solution:** Added public wrapper method `search_online_recipes` in `scripts/meal_recommender.py`.

**Location:** `scripts/meal_recommender.py` - `search_online_recipes` method

### Database Path Injection

**Problem:** Manager classes were not consistently receiving the `db_path` parameter, causing operations to use the default database instead of the test database.

**Solution:** Updated all manager class constructors to accept and pass `db_path`:
- `scripts/nutrition_calculator.py`
- `scripts/meal_recommender.py`
- `scripts/meal_tracker.py`
- `scripts/weekly_planner.py`
- `scripts/budget_tracker.py`
- `scripts/spoonacular_api.py`
- `scripts/usda_api.py`
- `scripts/shopping_list.py`

### Test Helper Function

**Problem:** Test cases were duplicating SQL INSERT statements for creating test users.

**Solution:** Created reusable helper function `create_test_user` in `tests/test_gui.py`.

**Location:** `tests/test_gui.py` - `create_test_user` function

---

## Features & Integrations

### Online Recipe Search with Cross-Referencing

#### Overview

The meal recommendation system now intelligently falls back to online recipe search when the local database has insufficient meal options (<5 meals). Online recipes are cross-referenced with your shopping history for realistic pricing and validated with USDA nutrition data for accuracy.

#### Features

1. **Intelligent Fallback Search**
   - Automatically triggers when local database has <5 suitable meals
   - Searches Spoonacular API with dietary restrictions and macro filters
   - Seamlessly integrates online recipes into recommendation scoring
   - Gracefully degrades if API unavailable

2. **Price Cross-Referencing**
   - Compares Spoonacular prices with your shopping history (last 90 days)
   - Uses hybrid calculation: 70% shopping history + 30% API when ingredients matched
   - Provides confidence score (0.0-1.0) based on ingredient match rate
   - Falls back to API price if no shopping history available

3. **Nutrition Validation**
   - Cross-validates Spoonacular nutrition with USDA database
   - Validates at ingredient level for accuracy
   - Flags discrepancies >10% for review
   - Provides validation confidence score

4. **Selective Recipe Caching**
   - Saves online recipes to database only when you rate them ≥3 stars
   - Prevents duplicates by checking API recipe ID
   - Saves complete recipe with ingredients
   - Cached recipes appear in future recommendations as local meals

#### Database Changes

Added 5 new columns to `meal_templates` table:
- `api_source` - Source API (e.g., 'spoonacular')
- `api_recipe_id` - External recipe ID for duplicate detection
- `nutrition_validated` - Boolean flag for USDA validation
- `price_confidence` - Price estimate confidence (0.0-1.0)
- `price_source` - Price source: 'spoonacular', 'shopping_history', 'hybrid'

#### Usage

**Automatic Usage:**
Online search happens automatically when using `meal_recommender.py`:
```bash
python scripts/meal_recommender.py --recommend dinner --count 5
```

If local database has <5 dinners, the system will automatically search online.

**Disable Online Search:**
```python
from scripts.meal_recommender import MealRecommender

recommender = MealRecommender()
meals = recommender.recommend_meal(
    meal_time="dinner",
    allow_online_search=False  # Only search locally
)
```

#### Configuration

**Required:**
- **Spoonacular API Key**: Get free key at https://spoonacular.com/food-api
- Add to `.env` file: `SPOONACULAR_API_KEY=your_key_here`

**Optional:**
- **USDA API Key**: For nutrition validation (has public access without key)
- Add to `.env` file: `USDA_API_KEY=your_key_here`

#### Error Handling

The system handles all failure modes gracefully:

| Scenario | Behavior |
|----------|----------|
| No API key configured | Skip online search, use local only |
| API quota exceeded | Fall back to local recipes |
| API request fails | Continue with local results |
| No shopping history | Use Spoonacular price only (low confidence) |
| USDA validation fails | Mark as unvalidated, use Spoonacular nutrition |

#### Migration

Existing databases are automatically migrated:
```bash
python scripts/migrate_add_online_recipe_support.py
```

Adds 5 new columns and 2 indexes. Safe to run multiple times (idempotent).

---

## Backend API Setup

### FastAPI Backend

FastAPI backend for Macro Chef meal planning application.

#### Setup

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Run the development server:
```bash
uvicorn app.main:app --reload --port 8000
```

3. Visit API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

#### Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings & environment
│   ├── database.py          # Database connection
│   ├── routers/             # API route handlers
│   ├── schemas/             # Pydantic models
│   └── services/            # Business logic (links to scripts/)
└── tests/                   # API tests
```

#### Environment Variables

Create a `.env` file in the project root:

```env
SPOONACULAR_API_KEY=your_key_here
USDA_API_KEY=your_key_here
DATABASE_URL=sqlite:///../database/meal_planner.db
```

#### Development

The backend uses the existing `scripts/` directory for business logic, so no changes are needed to your existing code. The FastAPI layer simply wraps your existing managers with REST endpoints.

---

## Frontend Setup

### React + TypeScript Frontend

React + TypeScript frontend for Macro Chef meal planning application.

#### Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file:
```bash
cp .env.example .env
```

3. Start development server:
```bash
npm run dev
```

The app will be available at http://localhost:5173

#### Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable UI components
│   │   └── layout/      # Layout components (Header, Sidebar)
│   ├── pages/            # Route pages
│   ├── hooks/          # Custom React hooks
│   ├── services/       # API client functions
│   ├── types/          # TypeScript type definitions
│   └── lib/            # Utilities
├── public/
└── package.json
```

#### Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **TailwindCSS** - Utility-first CSS
- **React Router** - Client-side routing
- **React Query** - Server state management
- **Axios** - HTTP client
- **Lucide React** - Icons

#### Development

The frontend connects to the FastAPI backend running on port 8000 by default. Make sure the backend is running before starting the frontend.

---

## Project Roadmap

### Phase 1: Foundation (Complete)
- [x] Project setup and database initialization (13 tables)
- [x] User profile management with goals
- [x] BMR/TDEE calculation (Katch-McArdle & Mifflin-St Jeor)
- [x] Daily macro & micronutrient target calculation
- [x] Meal tracking with progress monitoring
- [x] Inventory management with expiration alerts

### Phase 2: Intelligence (Complete)
- [x] Intelligent meal recommendation engine (0-100 scoring)
- [x] API integration (Spoonacular, USDA) with caching
- [x] Shopping list generation with inventory checking
- [x] Budget tracking with trends and category analysis

### Phase 3: Optimization (Complete)
- [x] Weekly meal planning with cost estimation
- [x] Micronutrient deficiency detection (9 nutrients)
- [x] Analytics and progress reports
- [x] Main CLI orchestrator

### Phase 4: Online Recipe Integration (Complete)
- [x] Intelligent online recipe search fallback (<5 local meals)
- [x] Price cross-referencing with shopping history (hybrid pricing)
- [x] USDA nutrition validation with discrepancy flagging
- [x] Selective recipe caching on user rating (≥3 stars)
- [x] Comprehensive error handling and graceful degradation

### Phase 5: Web Application (In Progress)
- [x] Backend Foundation (FastAPI)
- [x] Core API Endpoints
- [x] React Frontend Setup
- [x] Frontend Feature Implementation
- [ ] Authentication & Multi-User
- [ ] Testing & Deployment

### Future Enhancements
- [ ] Batch cooking optimization
- [ ] Multi-user household support
- [ ] Mobile app integration
- [ ] Barcode scanning for inventory
- [ ] Meal prep photo logging
- [ ] Social features (share recipes)

---

## License

MIT

## Contributing

This is a personal project, but suggestions and feedback are welcome! Feel free to open issues or submit pull requests.

## Acknowledgments

- Nutrition data from Spoonacular and USDA FoodData Central

---

**For the most up-to-date information, see:**
- `README.md` - Main project documentation
- `SPECIFICATION.md` - Complete technical specification
- `MIGRATION_PLAN.md` - Web migration details
- `DEPLOYMENT.md` - Deployment instructions
