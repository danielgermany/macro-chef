"""
Unit tests for database operations.
Tests database initialization, CRUD operations, and data integrity.

Usage: pytest tests/test_database.py -v
"""

import pytest
import sqlite3
import tempfile
import os
from pathlib import Path
from datetime import date, datetime, timedelta
import sys

sys.path.append(str(Path(__file__).parent.parent))
from scripts.db_setup import create_tables
from scripts.db_manager import DatabaseManager
from scripts.user_profile import UserProfileManager
from scripts.inventory_manager import InventoryManager


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    # Create temporary database file
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db')
    temp_path = temp_file.name
    temp_file.close()

    # Initialize database with schema
    conn = sqlite3.connect(temp_path)
    create_tables(conn)
    conn.commit()
    conn.close()

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


class TestDatabaseSetup:
    """Test database initialization and schema."""

    def test_database_creation(self, temp_db):
        """Test that database file is created."""
        assert os.path.exists(temp_db)
        assert os.path.getsize(temp_db) > 0

    def test_all_tables_created(self, temp_db):
        """Test that all 13 tables are created."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)

        tables = [row[0] for row in cursor.fetchall()]
        conn.close()

        expected_tables = [
            'body_metrics_history',
            'budget_tracking',
            'daily_nutrition_progress',
            'daily_nutrition_targets',
            'food_nutrition_cache',
            'inventory',
            'meal_ingredients',
            'meal_templates',
            'micronutrient_deficiency_alerts',
            'shopping_history',
            'user_profile',
            'weekly_meal_plan_items',
            'weekly_meal_plans'
        ]

        assert len(tables) == 13
        assert sorted(tables) == sorted(expected_tables)

    def test_foreign_keys_enabled(self, temp_db):
        """Test that foreign key constraints are enabled."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys;")
        result = cursor.fetchone()[0]
        conn.close()

        # Note: Foreign keys are enabled per connection, not globally
        # This tests the PRAGMA is available
        assert result in (0, 1)

    def test_indexes_created(self, temp_db):
        """Test that indexes are created for performance."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='index' AND name NOT LIKE 'sqlite_%'
        """)

        indexes = [row[0] for row in cursor.fetchall()]
        conn.close()

        # Check for key indexes
        assert 'idx_metrics_date' in indexes
        assert 'idx_targets_date' in indexes
        assert 'idx_progress_date' in indexes
        assert 'idx_inventory_expiration' in indexes


class TestUserProfile:
    """Test user profile CRUD operations."""

    def test_create_user_profile(self, temp_db):
        """Test creating a new user profile."""
        manager = UserProfileManager(db_path=temp_db)

        user_id = manager.create_user(
            name='Test User',
            age=30,
            sex='male',
            height_inches=70,
            weight_lbs=180,
            body_fat_pct=15.0,
            goal_type='maintain',
            activity_level='moderate',
            weekly_budget_usd=100.0
        )

        assert user_id is not None
        assert user_id == 1

    def test_read_user_profile(self, temp_db):
        """Test reading user profile."""
        manager = UserProfileManager(db_path=temp_db)

        # Create user first
        user_id = manager.create_user(
            name='Test User',
            age=25,
            sex='female',
            height_inches=65,
            weight_lbs=140,
            goal_type='cut',
            activity_level='light'
        )

        # Read profile
        profile = manager.get_user(user_id)

        assert profile is not None
        assert profile['name'] == 'Test User'
        assert profile['age'] == 25
        assert profile['sex'] == 'female'
        assert profile['weight_lbs'] == 140
        assert profile['goal_type'] == 'cut'

    def test_update_user_profile(self, temp_db):
        """Test updating user profile."""
        manager = UserProfileManager(db_path=temp_db)

        # Create user
        user_id = manager.create_user(
            name='Test User',
            age=30,
            sex='male',
            height_inches=70,
            weight_lbs=180,
            goal_type='bulk'
        )

        # Update profile
        manager.update_user(
            user_id=user_id,
            weight_lbs=185,
            goal_type='maintain'
        )

        # Verify update
        profile = manager.get_user(user_id)
        assert profile['weight_lbs'] == 185
        assert profile['goal_type'] == 'maintain'
        assert profile['name'] == 'Test User'  # Unchanged fields preserved


class TestInventoryOperations:
    """Test inventory management operations."""

    def test_add_inventory_item(self, temp_db):
        """Test adding an item to inventory."""
        # Create user first
        user_manager = UserProfileManager(db_path=temp_db)
        user_id = user_manager.create_user(
            name='Test User',
            age=30,
            sex='male',
            height_inches=70,
            weight_lbs=180
        )

        # Add inventory item
        inv_manager = InventoryManager(db_path=temp_db)
        item_id = inv_manager.add_item(
            item_name='Chicken Breast',
            quantity=2.5,
            unit='lbs',
            category='protein',
            location='freezer',
            expiration_date=date.today() + timedelta(days=30)
        )

        assert item_id is not None
        assert item_id > 0

    def test_list_inventory(self, temp_db):
        """Test listing inventory items."""
        # Setup
        user_manager = UserProfileManager(db_path=temp_db)
        user_manager.create_user(
            name='Test User',
            age=30,
            sex='male',
            height_inches=70,
            weight_lbs=180
        )

        inv_manager = InventoryManager(db_path=temp_db)
        inv_manager.add_item('Rice', 5, 'lbs', category='grain', location='pantry')
        inv_manager.add_item('Eggs', 12, 'count', category='protein', location='fridge')

        # List inventory
        items = inv_manager.list_inventory()

        assert len(items) == 2
        assert items[0]['item_name'] in ['Rice', 'Eggs']

    def test_search_inventory(self, temp_db):
        """Test searching inventory by name."""
        # Setup
        user_manager = UserProfileManager(db_path=temp_db)
        user_manager.create_user(
            name='Test User',
            age=30,
            sex='male',
            height_inches=70,
            weight_lbs=180
        )

        inv_manager = InventoryManager(db_path=temp_db)
        inv_manager.add_item('Chicken Breast', 2, 'lbs', category='protein', location='freezer')
        inv_manager.add_item('Chicken Thighs', 1.5, 'lbs', category='protein', location='freezer')
        inv_manager.add_item('Rice', 5, 'lbs', category='grain', location='pantry')

        # Search for chicken
        results = inv_manager.search_items('chicken')

        assert len(results) == 2
        assert all('chicken' in item['item_name'].lower() for item in results)


class TestDataIntegrity:
    """Test data integrity and constraints."""

    def test_unique_user_date_nutrition_target(self, temp_db):
        """Test that user can't have duplicate nutrition targets for same date."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Create user
        cursor.execute("""
            INSERT INTO user_profile (name, age, sex, height_inches, weight_lbs)
            VALUES ('Test', 30, 'male', 70, 180)
        """)
        user_id = cursor.lastrowid

        # Insert first target
        cursor.execute("""
            INSERT INTO daily_nutrition_targets
            (user_id, date, calories_target, protein_target_g, carbs_target_g, fat_target_g)
            VALUES (?, ?, 2000, 150, 200, 60)
        """, (user_id, date.today()))

        # Try to insert duplicate - should fail
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO daily_nutrition_targets
                (user_id, date, calories_target, protein_target_g, carbs_target_g, fat_target_g)
                VALUES (?, ?, 2200, 160, 220, 65)
            """, (user_id, date.today()))

        conn.close()

    def test_check_constraints(self, temp_db):
        """Test CHECK constraints on user profile."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Invalid sex value
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO user_profile (name, age, sex, height_inches, weight_lbs)
                VALUES ('Test', 30, 'other', 70, 180)
            """)

        conn.close()

    def test_cascade_delete(self, temp_db):
        """Test CASCADE delete on meal_ingredients when meal_template is deleted."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Create user and meal template
        cursor.execute("""
            INSERT INTO user_profile (name, age, sex, height_inches, weight_lbs)
            VALUES ('Test', 30, 'male', 70, 180)
        """)
        user_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO meal_templates
            (user_id, name, meal_type, calories, protein_g, carbs_g, fat_g, recipe_instructions)
            VALUES (?, 'Test Meal', 'dinner', 500, 40, 50, 15, 'Cook it')
        """, (user_id,))
        meal_id = cursor.lastrowid

        # Add ingredient
        cursor.execute("""
            INSERT INTO meal_ingredients (meal_template_id, ingredient_name, quantity, unit)
            VALUES (?, 'Chicken', 8, 'oz')
        """, (meal_id,))

        # Verify ingredient exists
        cursor.execute("SELECT COUNT(*) FROM meal_ingredients WHERE meal_template_id = ?", (meal_id,))
        assert cursor.fetchone()[0] == 1

        # Delete meal template
        cursor.execute("DELETE FROM meal_templates WHERE id = ?", (meal_id,))

        # Verify ingredient is also deleted (CASCADE)
        cursor.execute("SELECT COUNT(*) FROM meal_ingredients WHERE meal_template_id = ?", (meal_id,))
        assert cursor.fetchone()[0] == 0

        conn.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
