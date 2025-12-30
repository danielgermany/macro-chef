"""
Initialize the SQLite database with all required tables.
Run this script once to set up the database.

Usage: python scripts/db_setup.py
"""

import sqlite3
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config.config import DATABASE_PATH, BACKUP_DIR

def create_tables(conn):
    """Create all database tables."""
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. user_profile
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            sex TEXT CHECK(sex IN ('male', 'female')),
            height_inches REAL,

            weight_lbs REAL NOT NULL,
            body_fat_pct REAL,
            muscle_mass_lbs REAL,
            bmr_kcal INTEGER,

            goal_type TEXT CHECK(goal_type IN ('bulk', 'cut', 'maintain', 'recomp')),
            target_weekly_change_lbs REAL,
            activity_level TEXT CHECK(activity_level IN ('sedentary', 'light', 'moderate', 'very_active', 'athlete')),
            training_days_per_week INTEGER DEFAULT 0,

            cooking_skill TEXT CHECK(cooking_skill IN ('beginner', 'intermediate', 'advanced')),
            cooking_frequency TEXT CHECK(cooking_frequency IN ('daily', 'batch_2_3x', 'batch_weekly')),
            dietary_restrictions TEXT,
            food_dislikes TEXT,

            weekly_budget_usd REAL,

            available_equipment TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 2. body_metrics_history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS body_metrics_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date DATE NOT NULL,

            weight_lbs REAL NOT NULL,
            body_fat_pct REAL,
            muscle_mass_lbs REAL,

            waist_inches REAL,
            chest_inches REAL,
            arms_inches REAL,
            legs_inches REAL,

            notes TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_profile(id)
        );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_date ON body_metrics_history(date);")

    # 3. daily_nutrition_targets
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_nutrition_targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date DATE NOT NULL,

            calories_target INTEGER NOT NULL,
            protein_target_g INTEGER NOT NULL,
            carbs_target_g INTEGER NOT NULL,
            fat_target_g INTEGER NOT NULL,
            fiber_target_g INTEGER,

            sugar_limit_g INTEGER,
            saturated_fat_limit_g INTEGER,
            sodium_limit_mg INTEGER,
            cholesterol_limit_mg INTEGER,

            vitamin_d_target_mcg REAL,
            vitamin_c_target_mg REAL,
            vitamin_a_target_mcg REAL,
            calcium_target_mg REAL,
            iron_target_mg REAL,
            magnesium_target_mg REAL,
            potassium_target_mg REAL,
            zinc_target_mg REAL,
            omega3_target_g REAL,

            is_training_day BOOLEAN DEFAULT 0,
            goal_type TEXT,
            tdee_kcal INTEGER,
            notes TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_profile(id),
            UNIQUE(user_id, date)
        );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_targets_date ON daily_nutrition_targets(date);")

    # 4. daily_nutrition_progress
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_nutrition_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date DATE NOT NULL,
            meal_time TEXT CHECK(meal_time IN ('breakfast', 'lunch', 'dinner', 'snack')),
            meal_name TEXT NOT NULL,

            calories INTEGER NOT NULL,
            protein_g REAL NOT NULL,
            carbs_g REAL NOT NULL,
            fat_g REAL NOT NULL,
            fiber_g REAL,

            sugar_g REAL,
            saturated_fat_g REAL,
            sodium_mg REAL,
            cholesterol_mg REAL,

            vitamin_d_mcg REAL,
            vitamin_c_mg REAL,
            vitamin_a_mcg REAL,
            calcium_mg REAL,
            iron_mg REAL,
            magnesium_mg REAL,
            potassium_mg REAL,
            zinc_mg REAL,
            omega3_g REAL,

            serving_size TEXT,
            notes TEXT,
            rating INTEGER CHECK(rating BETWEEN 1 AND 5),

            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_profile(id)
        );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_progress_date ON daily_nutrition_progress(date);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_progress_meal ON daily_nutrition_progress(meal_name);")

    # 5. inventory
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,

            item_name TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,

            category TEXT,

            purchase_date DATE,
            expiration_date DATE,

            location TEXT,

            notes TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_profile(id)
        );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_expiration ON inventory(expiration_date);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_item ON inventory(item_name);")

    # 6. meal_templates
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meal_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,

            name TEXT NOT NULL,
            description TEXT,
            meal_type TEXT CHECK(meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),

            prep_time_minutes INTEGER,
            cook_time_minutes INTEGER,
            total_time_minutes INTEGER,
            difficulty TEXT CHECK(difficulty IN ('easy', 'medium', 'hard')),
            servings INTEGER DEFAULT 1,

            recipe_instructions TEXT NOT NULL,
            recipe_source TEXT,

            calories INTEGER NOT NULL,
            protein_g REAL NOT NULL,
            carbs_g REAL NOT NULL,
            fat_g REAL NOT NULL,
            fiber_g REAL,

            sugar_g REAL,
            saturated_fat_g REAL,
            sodium_mg REAL,
            cholesterol_mg REAL,

            vitamin_d_mcg REAL,
            vitamin_c_mg REAL,
            vitamin_a_mcg REAL,
            calcium_mg REAL,
            iron_mg REAL,
            magnesium_mg REAL,
            potassium_mg REAL,
            zinc_mg REAL,
            omega3_g REAL,

            cost_estimate_usd REAL,
            rating INTEGER CHECK(rating BETWEEN 1 AND 5),
            times_made INTEGER DEFAULT 0,
            last_made DATE,

            tags TEXT,

            is_batch_friendly BOOLEAN DEFAULT 0,
            can_freeze BOOLEAN DEFAULT 0,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_profile(id)
        );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_meal_type ON meal_templates(meal_type);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_meal_rating ON meal_templates(rating);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_meal_last_made ON meal_templates(last_made);")

    # 7. meal_ingredients
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meal_ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meal_template_id INTEGER NOT NULL,

            ingredient_name TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,

            optional BOOLEAN DEFAULT 0,
            substitutions TEXT,

            notes TEXT,

            FOREIGN KEY (meal_template_id) REFERENCES meal_templates(id) ON DELETE CASCADE
        );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ingredient_meal ON meal_ingredients(meal_template_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ingredient_name ON meal_ingredients(ingredient_name);")

    # 8. shopping_history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shopping_history (
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
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_shopping_date ON shopping_history(purchase_date);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_shopping_item ON shopping_history(item_name);")

    # 9. budget_tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budget_tracking (
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
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_budget_period ON budget_tracking(period_start, period_end);")

    # 10. food_nutrition_cache
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS food_nutrition_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            food_name TEXT NOT NULL UNIQUE,
            serving_size REAL NOT NULL,
            serving_unit TEXT NOT NULL,

            calories INTEGER,
            protein_g REAL,
            carbs_g REAL,
            fat_g REAL,
            fiber_g REAL,

            sugar_g REAL,
            saturated_fat_g REAL,
            sodium_mg REAL,
            cholesterol_mg REAL,

            vitamin_d_mcg REAL,
            vitamin_c_mg REAL,
            vitamin_a_mcg REAL,
            calcium_mg REAL,
            iron_mg REAL,
            magnesium_mg REAL,
            potassium_mg REAL,
            zinc_mg REAL,
            omega3_g REAL,

            data_source TEXT CHECK(data_source IN ('spoonacular', 'usda', 'manual')),
            source_id TEXT,

            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_food_name ON food_nutrition_cache(food_name);")

    # Phase 2 Enhancement Tables

    # 11. weekly_meal_plans
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weekly_meal_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,

            week_start_date DATE NOT NULL,
            week_end_date DATE NOT NULL,

            plan_name TEXT,

            total_cost_estimate_usd REAL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_profile(id)
        );
    """)

    # 12. weekly_meal_plan_items
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weekly_meal_plan_items (
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
    """)

    # 13. micronutrient_deficiency_alerts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS micronutrient_deficiency_alerts (
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
            food_suggestions TEXT,

            acknowledged BOOLEAN DEFAULT 0,
            resolved_date DATE,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_profile(id)
        );
    """)

    conn.commit()
    print("[SUCCESS] All tables created successfully!")

def main():
    """Main setup function."""
    # Ensure database directory exists
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    # Connect and create tables
    conn = sqlite3.connect(DATABASE_PATH)
    try:
        create_tables(conn)
        print(f"\n[SUCCESS] Database initialized at: {DATABASE_PATH}")
    except Exception as e:
        print(f"[ERROR] Error creating database: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()
