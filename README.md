# Macro Chef - AI-Powered Meal Planning System

An intelligent meal planning system that helps you maintain nutrition goals, minimize food waste, support athletic performance, and manage grocery budgets through smart recommendations and comprehensive tracking.

## Features

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

## Tech Stack

- **Database**: SQLite (13 tables)
- **Backend**: Python 3.8+
- **APIs**: Spoonacular (recipes/nutrition), USDA FoodData Central (nutrition)
- **Interface**: Unified CLI with natural language support

## Quick Start

### 1. Installation

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

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys (optional but recommended)
# Get Spoonacular API key: https://spoonacular.com/food-api
```

### 3. Initialize Database & Create Profile

```bash
# Initialize database
python scripts/db_setup.py

# Create your user profile (interactive)
python scripts/user_profile.py --create

# If upgrading from a previous version, run migration:
python scripts/migrate_add_online_recipe_support.py
```

**Note**: See [ONLINE_RECIPE_FEATURE.md](ONLINE_RECIPE_FEATURE.md) for details on the online recipe search feature with price cross-referencing and nutrition validation.

## Usage

### Main Interface (Recommended)

The `claude_interface.py` provides a unified CLI for all features:

```bash
# Daily check-in (targets, progress, inventory alerts, budget, next meal suggestion)
python scripts/claude_interface.py daily

# Dashboard overview
python scripts/claude_interface.py dashboard

# Log a meal (interactive with template search)
python scripts/claude_interface.py log-meal

# Get meal recommendations
python scripts/claude_interface.py recommend

# Create weekly meal plan with shopping list
python scripts/claude_interface.py plan-week

# View progress report
python scripts/claude_interface.py progress --days 30

# Quick checks
python scripts/claude_interface.py inventory
python scripts/claude_interface.py budget
```

### Individual Modules

Each module can also be used independently:

#### User Profile & Metrics

```bash
# View profile
python scripts/user_profile.py --view

# Log body metrics
python scripts/user_profile.py --log-metrics --weight 180 --body-fat 15

# View progress (30 days)
python scripts/user_profile.py --progress --days 30
```

#### Nutrition & Meal Tracking

```bash
# Generate today's targets
python scripts/nutrition_calculator.py --generate --training-day

# View targets
python scripts/nutrition_calculator.py --view

# Log a meal
python scripts/meal_tracker.py --log \
  --name "Grilled Chicken" \
  --calories 500 \
  --protein 50 \
  --carbs 40 \
  --fat 15 \
  --meal-time dinner

# View today's progress
python scripts/meal_tracker.py --progress

# Weekly summary
python scripts/meal_tracker.py --weekly --days 7

# Meal history
python scripts/meal_tracker.py --history --days 30
```

#### Meal Recommendations

```bash
# Get dinner recommendations
python scripts/meal_recommender.py --recommend dinner --count 5

# Quick suggestions for all remaining meals
python scripts/meal_recommender.py --quick

# With constraints
python scripts/meal_recommender.py --recommend lunch \
  --max-time 30 \
  --budget 5
```

#### Inventory Management

```bash
# Add items
python scripts/inventory_manager.py --add \
  --name "Chicken breast" \
  --quantity 2.5 \
  --unit lbs \
  --category protein \
  --location freezer \
  --days-until-expire 30

# List inventory
python scripts/inventory_manager.py --list

# Filter by location
python scripts/inventory_manager.py --list --filter-location fridge

# Check expiring items
python scripts/inventory_manager.py --expiring --days 7

# Search
python scripts/inventory_manager.py --search chicken

# Use item (reduces quantity)
python scripts/inventory_manager.py --use 1 --amount 0.5

# Summary
python scripts/inventory_manager.py --summary
```

#### Shopping & Budget

```bash
# Generate shopping list from meals (IDs from meal_templates)
python scripts/shopping_list.py --generate 1 2 3 --servings 1 2 1

# View shopping history
python scripts/shopping_list.py --history --days 30

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

#### Weekly Planning

```bash
# Generate week plan
python scripts/weekly_planner.py --generate --save --name "Cutting Week"

# View saved plans
python scripts/weekly_planner.py --list

# View specific plan
python scripts/weekly_planner.py --view 1

# Generate shopping list from plan
python scripts/weekly_planner.py --shopping-list 1
```

#### Analytics & Insights

```bash
# Comprehensive progress report
python scripts/analytics.py --progress-report --days 30

# Check for micronutrient deficiencies
python scripts/analytics.py --deficiencies --days 7 --save-alerts

# View active alerts
python scripts/analytics.py --alerts
```

#### API Integration (Optional)

```bash
# Search recipes
python scripts/spoonacular_api.py --search "chicken" \
  --max-time 30 \
  --min-protein 40

# Get recipe by ID
python scripts/spoonacular_api.py --recipe-id 12345

# Look up ingredient nutrition
python scripts/spoonacular_api.py --ingredient "chicken breast"

# USDA nutrition search
python scripts/usda_api.py --nutrition "salmon"
```

## Example Workflow

### Daily Routine

```bash
# Morning check-in
python scripts/claude_interface.py daily

# Log breakfast
python scripts/claude_interface.py log-meal
> Protein oatmeal
> 1 serving
> 5/5 rating

# Get lunch recommendation
python scripts/claude_interface.py recommend

# Check remaining macros
python scripts/claude_interface.py dashboard
```

### Weekly Planning

```bash
# Review last week
python scripts/analytics.py --progress-report --days 7

# Create new week plan
python scripts/claude_interface.py plan-week
> Save plan
> Generate shopping list

# Go shopping (record purchases for budget tracking)
```

## Project Structure

```
macro-chef/
├── README.md                   # This file
├── SPECIFICATION.md            # Complete technical specification
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
├── .gitignore
│
├── database/
│   ├── meal_planner.db        # SQLite database (13 tables)
│   └── backups/               # Automatic backups
│
├── config/
│   └── config.py              # Configuration & constants
│
├── scripts/
│   ├── claude_interface.py    # Main CLI orchestrator
│   ├── db_setup.py            # Database initialization
│   ├── db_manager.py          # Base database operations
│   │
│   ├── user_profile.py        # User & body metrics management
│   ├── nutrition_calculator.py # Daily target calculation
│   ├── meal_tracker.py        # Meal logging & progress
│   ├── inventory_manager.py   # Food inventory management
│   │
│   ├── meal_recommender.py    # Intelligent meal suggestions
│   ├── spoonacular_api.py     # Spoonacular API integration
│   ├── usda_api.py            # USDA nutrition database
│   │
│   ├── shopping_list.py       # Shopping list generation
│   ├── budget_tracker.py      # Expense tracking & analysis
│   ├── weekly_planner.py      # Weekly meal planning
│   └── analytics.py           # Insights & deficiency detection
│
└── data/                       # JSON caches and templates
```

## Key Principles

- **Cheap**: Budget-conscious recommendations
- **Fast**: Quick meal suggestions and prep
- **Easy**: Simple recipes, minimal complexity
- **Nutritious**: Macro and micronutrient optimization

## Features Roadmap

### ✅ Phase 1: Foundation (Complete)
- [x] Project setup and database initialization (13 tables)
- [x] User profile management with goals
- [x] BMR/TDEE calculation (Katch-McArdle & Mifflin-St Jeor)
- [x] Daily macro & micronutrient target calculation
- [x] Meal tracking with progress monitoring
- [x] Inventory management with expiration alerts

### ✅ Phase 2: Intelligence (Complete)
- [x] Intelligent meal recommendation engine (0-100 scoring)
- [x] API integration (Spoonacular, USDA) with caching
- [x] Shopping list generation with inventory checking
- [x] Budget tracking with trends and category analysis

### ✅ Phase 3: Optimization (Complete)
- [x] Weekly meal planning with cost estimation
- [x] Micronutrient deficiency detection (9 nutrients)
- [x] Analytics and progress reports
- [x] Main CLI orchestrator

### ✅ Phase 4: Online Recipe Integration (Complete)
- [x] Intelligent online recipe search fallback (<5 local meals)
- [x] Price cross-referencing with shopping history (hybrid pricing)
- [x] USDA nutrition validation with discrepancy flagging
- [x] Selective recipe caching on user rating (≥3 stars)
- [x] Comprehensive error handling and graceful degradation

### 🎯 Future Enhancements
- [ ] Batch cooking optimization
- [ ] Multi-user household support
- [ ] Mobile app integration
- [ ] Barcode scanning for inventory
- [ ] Meal prep photo logging
- [ ] Social features (share recipes)

## Database Schema

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

See [SPECIFICATION.md](SPECIFICATION.md) for complete schema details.

## License

MIT

## Contributing

This is a personal project, but suggestions and feedback are welcome! Feel free to open issues or submit pull requests.

## Acknowledgments

- Nutrition data from Spoonacular and USDA FoodData Central

