# AI-Powered Meal Planning System - Complete Technical Specification

## Project Overview

**Purpose:** Build a comprehensive meal planning system that helps users maintain nutrition goals, minimize food waste, support athletic performance, and manage grocery budgets through intelligent recommendations.

**Tech Stack:**
- Database: SQLite
- Backend: Python 3.8+
- APIs: Spoonacular (primary), USDA FoodData Central (backup)
- Interface: Claude AI (natural language)
- User: Single person (future: multi-person household support)

**Key Principles:**
- Cheap: Budget-conscious recommendations
- Fast: Quick meal suggestions and prep
- Easy: Simple recipes, minimal complexity
- Nutritious: Macro and micronutrient optimization

---

## System Architecture

### High-Level Flow
```
User → Claude Interface → Python Scripts → SQLite Database
                       ↓
                  External APIs (Spoonacular, USDA)
```

### Directory Structure
```
meal-planner/
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
└── tests/
    ├── test_database.py
    ├── test_nutrition.py
    └── test_api.py
```

---

## Database Schema

### Phase 1: MVP Tables

#### 1. user_profile
Stores user's body metrics, goals, and preferences.
```sql
CREATE TABLE user_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    sex TEXT CHECK(sex IN ('male', 'female')),
    height_inches REAL,

    -- Current metrics
    weight_lbs REAL NOT NULL,
    body_fat_pct REAL,
    muscle_mass_lbs REAL,
    bmr_kcal INTEGER,

    -- Goals
    goal_type TEXT CHECK(goal_type IN ('bulk', 'cut', 'maintain', 'recomp')),
    target_weekly_change_lbs REAL,
    activity_level TEXT CHECK(activity_level IN ('sedentary', 'light', 'moderate', 'very_active', 'athlete')),
    training_days_per_week INTEGER DEFAULT 0,

    -- Preferences
    cooking_skill TEXT CHECK(cooking_skill IN ('beginner', 'intermediate', 'advanced')),
    cooking_frequency TEXT CHECK(cooking_frequency IN ('daily', 'batch_2_3x', 'batch_weekly')),
    dietary_restrictions TEXT, -- JSON array: ["vegetarian", "no_dairy", "gluten_free"]
    food_dislikes TEXT,        -- JSON array: ["mushrooms", "olives"]

    -- Budget
    weekly_budget_usd REAL,

    -- Equipment
    available_equipment TEXT,  -- JSON array: ["oven", "stovetop", "microwave", "slow_cooker"]

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. body_metrics_history
Track body composition changes over time.
```sql
CREATE TABLE body_metrics_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL,

    weight_lbs REAL NOT NULL,
    body_fat_pct REAL,
    muscle_mass_lbs REAL,

    -- Optional measurements
    waist_inches REAL,
    chest_inches REAL,
    arms_inches REAL,
    legs_inches REAL,

    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profile(id)
);

CREATE INDEX idx_metrics_date ON body_metrics_history(date);
```

#### 3. daily_nutrition_targets
Calculated daily nutrition targets.
```sql
CREATE TABLE daily_nutrition_targets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL,

    -- Macros
    calories_target INTEGER NOT NULL,
    protein_target_g INTEGER NOT NULL,
    carbs_target_g INTEGER NOT NULL,
    fat_target_g INTEGER NOT NULL,
    fiber_target_g INTEGER,

    -- Limits
    sugar_limit_g INTEGER,
    saturated_fat_limit_g INTEGER,
    sodium_limit_mg INTEGER,
    cholesterol_limit_mg INTEGER,

    -- Top 10 Micronutrients (Phase 2)
    vitamin_d_target_mcg REAL,
    vitamin_c_target_mg REAL,
    vitamin_a_target_mcg REAL,
    calcium_target_mg REAL,
    iron_target_mg REAL,
    magnesium_target_mg REAL,
    potassium_target_mg REAL,
    zinc_target_mg REAL,
    omega3_target_g REAL,

    -- Metadata
    is_training_day BOOLEAN DEFAULT 0,
    goal_type TEXT,
    tdee_kcal INTEGER,
    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profile(id),
    UNIQUE(user_id, date)
);

CREATE INDEX idx_targets_date ON daily_nutrition_targets(date);
```

#### 4. daily_nutrition_progress
Track actual food intake throughout the day.
```sql
CREATE TABLE daily_nutrition_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL,
    meal_time TEXT CHECK(meal_time IN ('breakfast', 'lunch', 'dinner', 'snack')),
    meal_name TEXT NOT NULL,

    -- Macros
    calories INTEGER NOT NULL,
    protein_g REAL NOT NULL,
    carbs_g REAL NOT NULL,
    fat_g REAL NOT NULL,
    fiber_g REAL,

    -- Other
    sugar_g REAL,
    saturated_fat_g REAL,
    sodium_mg REAL,
    cholesterol_mg REAL,

    -- Top 10 Micronutrients (Phase 2)
    vitamin_d_mcg REAL,
    vitamin_c_mg REAL,
    vitamin_a_mcg REAL,
    calcium_mg REAL,
    iron_mg REAL,
    magnesium_mg REAL,
    potassium_mg REAL,
    zinc_mg REAL,
    omega3_g REAL,

    -- Metadata
    serving_size TEXT,
    notes TEXT,
    rating INTEGER CHECK(rating BETWEEN 1 AND 5),

    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profile(id),
    FOREIGN KEY (date) REFERENCES daily_nutrition_targets(date)
);

CREATE INDEX idx_progress_date ON daily_nutrition_progress(date);
CREATE INDEX idx_progress_meal ON daily_nutrition_progress(meal_name);
```

#### 5. inventory
Track food items on hand.
```sql
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,

    item_name TEXT NOT NULL,
    quantity REAL NOT NULL,
    unit TEXT NOT NULL, -- 'lbs', 'oz', 'count', 'cups', etc.

    category TEXT, -- 'protein', 'grain', 'vegetable', 'fruit', 'dairy', 'pantry', 'frozen'

    purchase_date DATE,
    expiration_date DATE,

    location TEXT, -- 'fridge', 'freezer', 'pantry'

    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profile(id)
);

CREATE INDEX idx_inventory_expiration ON inventory(expiration_date);
CREATE INDEX idx_inventory_item ON inventory(item_name);
```

#### 6. meal_templates
Store recipes with complete nutrition data.
```sql
CREATE TABLE meal_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,

    name TEXT NOT NULL,
    description TEXT,
    meal_type TEXT CHECK(meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),

    -- Time and difficulty
    prep_time_minutes INTEGER,
    cook_time_minutes INTEGER,
    total_time_minutes INTEGER,
    difficulty TEXT CHECK(difficulty IN ('easy', 'medium', 'hard')),
    servings INTEGER DEFAULT 1,

    -- Recipe
    recipe_instructions TEXT NOT NULL, -- Step-by-step instructions
    recipe_source TEXT,                 -- URL or "custom"

    -- Macros (per serving)
    calories INTEGER NOT NULL,
    protein_g REAL NOT NULL,
    carbs_g REAL NOT NULL,
    fat_g REAL NOT NULL,
    fiber_g REAL,

    -- Other (per serving)
    sugar_g REAL,
    saturated_fat_g REAL,
    sodium_mg REAL,
    cholesterol_mg REAL,

    -- Top 10 Micronutrients (Phase 2, per serving)
    vitamin_d_mcg REAL,
    vitamin_c_mg REAL,
    vitamin_a_mcg REAL,
    calcium_mg REAL,
    iron_mg REAL,
    magnesium_mg REAL,
    potassium_mg REAL,
    zinc_mg REAL,
    omega3_g REAL,

    -- Cost and ratings
    cost_estimate_usd REAL,
    rating INTEGER CHECK(rating BETWEEN 1 AND 5),
    times_made INTEGER DEFAULT 0,
    last_made DATE,

    -- Tags
    tags TEXT, -- JSON array: ["high-protein", "quick", "budget", "batch-friendly"]

    -- Flags
    is_batch_friendly BOOLEAN DEFAULT 0,
    can_freeze BOOLEAN DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profile(id)
);

CREATE INDEX idx_meal_type ON meal_templates(meal_type);
CREATE INDEX idx_meal_rating ON meal_templates(rating);
CREATE INDEX idx_meal_last_made ON meal_templates(last_made);
```

#### 7. meal_ingredients
Link meals to required ingredients.
```sql
CREATE TABLE meal_ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meal_template_id INTEGER NOT NULL,

    ingredient_name TEXT NOT NULL,
    quantity REAL NOT NULL,
    unit TEXT NOT NULL,

    optional BOOLEAN DEFAULT 0,
    substitutions TEXT, -- JSON array: ["Greek yogurt", "sour cream"]

    notes TEXT, -- e.g., "diced", "minced", "to taste"

    FOREIGN KEY (meal_template_id) REFERENCES meal_templates(id) ON DELETE CASCADE
);

CREATE INDEX idx_ingredient_meal ON meal_ingredients(meal_template_id);
CREATE INDEX idx_ingredient_name ON meal_ingredients(ingredient_name);
```

#### 8. shopping_history
Track purchases and spending.
```sql
CREATE TABLE shopping_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,

    purchase_date DATE NOT NULL,

    item_name TEXT NOT NULL,
    quantity REAL NOT NULL,
    unit TEXT NOT NULL,

    unit_price_usd REAL,
    total_price_usd REAL NOT NULL,

    store TEXT,
    category TEXT,

    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profile(id)
);

CREATE INDEX idx_shopping_date ON shopping_history(purchase_date);
CREATE INDEX idx_shopping_item ON shopping_history(item_name);
```

#### 9. budget_tracking
Weekly/monthly budget summaries.
```sql
CREATE TABLE budget_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,

    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    period_type TEXT CHECK(period_type IN ('weekly', 'monthly')),

    total_spent_usd REAL NOT NULL,
    budget_limit_usd REAL NOT NULL,
    remaining_usd REAL NOT NULL,

    num_shopping_trips INTEGER,

    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profile(id)
);

CREATE INDEX idx_budget_period ON budget_tracking(period_start, period_end);
```

#### 10. food_nutrition_cache
Cache nutrition data from APIs to minimize requests.
```sql
CREATE TABLE food_nutrition_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    food_name TEXT NOT NULL UNIQUE,
    serving_size REAL NOT NULL,
    serving_unit TEXT NOT NULL,

    -- Macros per serving
    calories INTEGER,
    protein_g REAL,
    carbs_g REAL,
    fat_g REAL,
    fiber_g REAL,

    -- Other per serving
    sugar_g REAL,
    saturated_fat_g REAL,
    sodium_mg REAL,
    cholesterol_mg REAL,

    -- Top 10 Micronutrients (Phase 2, per serving)
    vitamin_d_mcg REAL,
    vitamin_c_mg REAL,
    vitamin_a_mcg REAL,
    calcium_mg REAL,
    iron_mg REAL,
    magnesium_mg REAL,
    potassium_mg REAL,
    zinc_mg REAL,
    omega3_g REAL,

    -- Source
    data_source TEXT CHECK(data_source IN ('spoonacular', 'usda', 'manual')),
    source_id TEXT,

    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_food_name ON food_nutrition_cache(food_name);
```

### Phase 2: Enhancement Tables (Add Later)

#### 11. weekly_meal_plans
Store pre-planned weekly meals.
```sql
CREATE TABLE weekly_meal_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,

    week_start_date DATE NOT NULL,
    week_end_date DATE NOT NULL,

    plan_name TEXT,

    total_cost_estimate_usd REAL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profile(id)
);
```

#### 12. weekly_meal_plan_items
Individual meals within a weekly plan.
```sql
CREATE TABLE weekly_meal_plan_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,

    day_of_week TEXT CHECK(day_of_week IN ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')),
    meal_time TEXT CHECK(meal_time IN ('breakfast', 'lunch', 'dinner', 'snack')),

    meal_template_id INTEGER NOT NULL,
    servings INTEGER DEFAULT 1,

    notes TEXT,

    FOREIGN KEY (plan_id) REFERENCES weekly_meal_plans(id) ON DELETE CASCADE,
    FOREIGN KEY (meal_template_id) REFERENCES meal_templates(id)
);
```

#### 13. micronutrient_deficiency_alerts
Track and alert on deficiencies.
```sql
CREATE TABLE micronutrient_deficiency_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,

    date_detected DATE NOT NULL,
    nutrient_name TEXT NOT NULL,

    target_amount REAL NOT NULL,
    avg_actual_amount REAL NOT NULL,
    percent_of_target REAL NOT NULL,

    severity TEXT CHECK(severity IN ('low', 'moderate', 'severe')),
    days_consecutive INTEGER DEFAULT 1,

    recommendation TEXT,
    food_suggestions TEXT, -- JSON array: ["salmon", "fortified milk"]

    acknowledged BOOLEAN DEFAULT 0,
    resolved_date DATE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profile(id)
);
```

---

## Implementation Steps

### Phase 1: Foundation (Start Here)

1. **Project Setup**
   - Create directory structure
   - Set up .gitignore
   - Create .env.example
   - Create requirements.txt
   - Initialize git repository

2. **Database Layer**
   - Create config/config.py
   - Create scripts/db_setup.py
   - Create scripts/db_manager.py
   - Initialize database

3. **User Management**
   - Create scripts/user_profile.py
   - Create scripts/nutrition_calculator.py
   - Test user creation and nutrition calculations

4. **Meal Tracking**
   - Create scripts/meal_tracker.py
   - Implement logging meals
   - Implement daily progress tracking

5. **Testing**
   - Create basic tests
   - Verify database operations
   - Verify nutrition calculations
