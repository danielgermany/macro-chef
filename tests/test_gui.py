"""
Unit tests for GUI application buttons and functionality.

Tests all button callbacks, user interactions, and GUI state management.
"""

import pytest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
from datetime import date, timedelta
import sqlite3
import tempfile
import os

# Import GUI class
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gui_app import MacroChefGUI


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)

    # Initialize database schema
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    # Create minimal schema for testing
    cursor.execute("""
        CREATE TABLE user_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            sex TEXT,
            height_inches REAL,
            weight_lbs REAL NOT NULL,
            body_fat_pct REAL,
            muscle_mass_lbs REAL,
            bmr_kcal INTEGER,
            goal_type TEXT,
            target_weekly_change_lbs REAL,
            activity_level TEXT,
            training_days_per_week INTEGER DEFAULT 0,
            cooking_skill TEXT,
            cooking_frequency TEXT,
            dietary_restrictions TEXT,
            food_dislikes TEXT,
            weekly_budget_usd REAL,
            available_equipment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE daily_nutrition_targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date DATE NOT NULL,
            calories_target INTEGER,
            protein_target_g INTEGER,
            carbs_target_g INTEGER,
            fat_target_g INTEGER,
            fiber_target_g INTEGER,
            is_training_day BOOLEAN DEFAULT 0,
            goal_type TEXT,
            tdee_kcal INTEGER,
            FOREIGN KEY (user_id) REFERENCES user_profile (id),
            UNIQUE(user_id, date)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE body_metrics_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date DATE NOT NULL,
            weight_lbs REAL NOT NULL,
            body_fat_pct REAL,
            muscle_mass_lbs REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_profile (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE meal_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            meal_type TEXT,
            calories REAL,
            protein_g REAL,
            carbs_g REAL,
            fat_g REAL,
            FOREIGN KEY (user_id) REFERENCES user_profile (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            category TEXT,
            location TEXT,
            expiration_date DATE,
            purchase_date DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY (user_id) REFERENCES user_profile (id)
        )
    """)

    conn.commit()
    conn.close()

    yield path

    # Cleanup - ensure all connections are closed
    import time
    import gc
    
    # Force garbage collection to close any lingering connections
    gc.collect()
    time.sleep(0.2)  # Brief delay to allow connections to close
    
    # Try multiple times with increasing delays
    for attempt in range(3):
        try:
            # Try to close any remaining connections by opening and closing
            try:
                test_conn = sqlite3.connect(path)
                test_conn.close()
            except:
                pass
            
            os.unlink(path)
            break  # Success, exit loop
        except (PermissionError, OSError) as e:
            if attempt < 2:  # Not the last attempt
                time.sleep(0.3 * (attempt + 1))  # Increasing delay
            else:
                # Last attempt failed - log but don't fail the test
                print(f"[WARNING] Could not delete temp database {path}: {e}")
                # On Windows, sometimes files are locked by the OS briefly
                # This is a known issue and doesn't affect test results


@pytest.fixture
def gui_root():
    """Create a Tk root for GUI testing."""
    root = tk.Tk()
    root.withdraw()  # Hide window during tests
    yield root
    root.destroy()


@pytest.fixture
def mock_gui(gui_root, temp_db, monkeypatch):
    """Create a GUI instance with mocked dependencies."""
    # Mock the database path
    monkeypatch.setattr('gui_app.DATABASE_PATH', temp_db)

    # Create GUI instance with test database
    app = MacroChefGUI(gui_root, db_path=temp_db)

    yield app


class TestProfileButtons:
    """Test Profile tab buttons."""

    def test_save_profile_button_creates_new_user(self, mock_gui, temp_db):
        """Test Save Profile button creates a new user."""
        # Set form values
        mock_gui.name_var.set("Test User")
        mock_gui.age_var.set(30)
        mock_gui.sex_var.set("male")
        mock_gui.height_var.set(70)
        mock_gui.weight_var.set(180)
        mock_gui.bodyfat_var.set(15.0)
        mock_gui.goal_var.set("maintain")
        mock_gui.activity_var.set("moderate")
        mock_gui.training_days_var.set(3)
        mock_gui.budget_var.set(100.0)

        # Mock messagebox
        with patch('gui_app.messagebox.showinfo') as mock_info:
            mock_gui.save_profile()

            # Verify success message
            mock_info.assert_called_once()
            assert "success" in mock_info.call_args[0][0].lower()

        # Verify user was created
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_profile WHERE name = ?", ("Test User",))
        user = cursor.fetchone()
        conn.close()

        assert user is not None
        assert user[1] == "Test User"  # name
        assert user[2] == 30  # age
        assert user[3] == "male"  # sex

    def test_save_profile_button_requires_name(self, mock_gui):
        """Test Save Profile button requires a name."""
        mock_gui.name_var.set("")

        with patch('gui_app.messagebox.showwarning') as mock_warning:
            mock_gui.save_profile()

            # Verify warning message
            mock_warning.assert_called_once()
            assert "name" in mock_warning.call_args[0][1].lower()

    def test_save_profile_button_updates_existing_user(self, mock_gui, temp_db):
        """Test Save Profile button updates existing user."""
        # Create initial user
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_profile
            (name, age, sex, height_inches, weight_lbs, body_fat_pct, goal_type, activity_level,
             dietary_restrictions, food_dislikes, available_equipment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("Original User", 25, "female", 65, 150, 20.0, "cut", "light", '[]', '[]', '[]'))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()

        # Set current user
        mock_gui.current_user_id = user_id

        # Update form values
        mock_gui.name_var.set("Updated User")
        mock_gui.age_var.set(26)
        mock_gui.weight_var.set(145)

        with patch('gui_app.messagebox.showinfo') as mock_info:
            mock_gui.save_profile()
            mock_info.assert_called_once()

        # Verify user was updated
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_profile WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()

        assert user[1] == "Updated User"
        assert user[2] == 26

    def test_load_profile_button_loads_user_data(self, mock_gui, temp_db):
        """Test Load Profile button loads user data."""
        # Create user
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_profile
            (id, name, age, sex, height_inches, weight_lbs, body_fat_pct,
             goal_type, activity_level, training_days_per_week, weekly_budget_usd,
             dietary_restrictions, food_dislikes, available_equipment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (1, "Test User", 30, "male", 70, 180, 15.0, "bulk", "moderate", 4, 120.0, '[]', '[]', '[]'))
        conn.commit()
        conn.close()

        # Load profile
        mock_gui.load_user()

        # Verify form values
        assert mock_gui.name_var.get() == "Test User"
        assert mock_gui.age_var.get() == 30
        assert mock_gui.sex_var.get() == "male"
        assert mock_gui.height_var.get() == 70
        assert mock_gui.weight_var.get() == 180
        assert mock_gui.bodyfat_var.get() == 15.0
        assert mock_gui.goal_var.get() == "bulk"
        assert mock_gui.activity_var.get() == "moderate"
        assert mock_gui.training_days_var.get() == 4
        assert mock_gui.budget_var.get() == 120.0

    def test_generate_targets_button(self, mock_gui, temp_db):
        """Test Generate Targets button creates daily targets."""
        # Create user first
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_profile
            (id, name, age, sex, height_inches, weight_lbs, body_fat_pct,
             goal_type, activity_level, dietary_restrictions, food_dislikes, available_equipment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (1, "Test User", 30, "male", 70, 180, 15.0, "maintain", "moderate", '[]', '[]', '[]'))
        conn.commit()
        conn.close()

        mock_gui.current_user_id = 1

        # Mock the nutrition calculator - return a proper targets dict
        mock_targets = {
            'user_id': 1,
            'date': date.today(),
            'calories_target': 2500,
            'protein_target_g': 180,
            'carbs_target_g': 300,
            'fat_target_g': 70,
            'fiber_target_g': 35,
            'is_training_day': False,
            'goal_type': 'maintain',
            'tdee_kcal': 2500
        }
        with patch.object(mock_gui.nutrition_calc, 'generate_daily_targets', return_value=mock_targets) as mock_gen:
            with patch.object(mock_gui.nutrition_calc, 'save_daily_targets', return_value=1) as mock_save:
                with patch('gui_app.messagebox.showinfo') as mock_info:
                    mock_gui.generate_targets()

                    # Verify calculator was called
                    mock_gen.assert_called_once()
                    assert mock_gen.call_args[1]['user_id'] == 1
                    assert mock_gen.call_args[1]['target_date'] == date.today()

                    # Verify save was called
                    mock_save.assert_called_once()

                    # Verify success message
                    mock_info.assert_called_once()

    def test_generate_targets_button_requires_user(self, mock_gui):
        """Test Generate Targets button requires a user profile."""
        mock_gui.current_user_id = None

        with patch('gui_app.messagebox.showwarning') as mock_warning:
            mock_gui.generate_targets()
            mock_warning.assert_called_once()


class TestDashboardButtons:
    """Test Dashboard tab buttons."""

    def test_refresh_dashboard_button(self, mock_gui, temp_db):
        """Test Refresh Dashboard button updates display."""
        # Create user and targets
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_profile (id, name, weight_lbs, dietary_restrictions, food_dislikes, available_equipment) VALUES (?, ?, 150, '[]', '[]', '[]')
        """, (1, "Test User"))
        cursor.execute("""
            INSERT INTO daily_nutrition_targets
            (user_id, date, calories_target, protein_target_g,
             carbs_target_g, fat_target_g, fiber_target_g)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (1, date.today(), 2500, 180, 300, 70, 35))
        conn.commit()
        conn.close()

        mock_gui.current_user_id = 1

        # Refresh dashboard
        mock_gui.refresh_dashboard()

        # Verify targets are displayed
        targets_content = mock_gui.targets_text.get('1.0', tk.END)
        # Check for calories (may be formatted as 2500 or 2,500)
        assert "2500" in targets_content or "2,500" in targets_content  # calories
        assert "180" in targets_content  # protein

    def test_refresh_dashboard_without_user(self, mock_gui):
        """Test Refresh Dashboard without a user does nothing."""
        mock_gui.current_user_id = None

        # Should not raise an error
        mock_gui.refresh_dashboard()


class TestMealsButtons:
    """Test Meals tab buttons."""

    def test_refresh_meals_button(self, mock_gui, temp_db):
        """Test Refresh Meals button loads meal list."""
        # Create test meals
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO meal_templates
            (name, meal_type, calories, protein_g, carbs_g, fat_g)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("Chicken Salad", "lunch", 450, 40, 30, 15))
        cursor.execute("""
            INSERT INTO meal_templates
            (name, meal_type, calories, protein_g, carbs_g, fat_g)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("Oatmeal", "breakfast", 350, 12, 55, 8))
        conn.commit()
        conn.close()

        # Refresh meals
        mock_gui.refresh_meals()

        # Verify meals are displayed
        items = mock_gui.meals_tree.get_children()
        assert len(items) == 2

    def test_get_recommendation_button_requires_user(self, mock_gui):
        """Test Get Recommendation button requires a user."""
        mock_gui.current_user_id = None

        with patch('gui_app.messagebox.showwarning') as mock_warning:
            mock_gui.get_meal_recommendation()
            mock_warning.assert_called_once()

    def test_get_recommendation_button_requires_targets(self, mock_gui, temp_db):
        """Test Get Recommendation button requires targets."""
        # Create user without targets
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_profile (id, name, weight_lbs, dietary_restrictions, food_dislikes, available_equipment) VALUES (?, ?, 150, '[]', '[]', '[]')
        """, (1, "Test User"))
        conn.commit()
        conn.close()

        mock_gui.current_user_id = 1

        # Mock get_targets to return None
        with patch.object(mock_gui.nutrition_calc, 'get_daily_targets', return_value=None):
            with patch('gui_app.messagebox.showwarning') as mock_warning:
                mock_gui.get_meal_recommendation()
                mock_warning.assert_called_once()

    def test_get_recommendation_button_shows_meal(self, mock_gui, temp_db):
        """Test Get Recommendation button displays a meal."""
        # Create user and targets
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_profile (id, name, weight_lbs, dietary_restrictions, food_dislikes, available_equipment) VALUES (?, ?, 150, '[]', '[]', '[]')
        """, (1, "Test User"))
        cursor.execute("""
            INSERT INTO daily_nutrition_targets
            (user_id, date, calories_target, protein_target_g)
            VALUES (?, ?, ?, ?)
        """, (1, date.today(), 2400, 180))
        conn.commit()
        conn.close()

        mock_gui.current_user_id = 1

        # Mock get_targets and recommend_meal
        mock_targets = {
            'calories_target': 2400,
            'protein_target_g': 180
        }
        mock_meal = {
            'name': 'Chicken Dinner',
            'meal_type': 'dinner',
            'calories': 800,
            'protein_g': 60,
            'carbs_g': 80,
            'fat_g': 20
        }

        with patch.object(mock_gui.nutrition_calc, 'get_daily_targets', return_value=mock_targets):
            with patch.object(mock_gui.meal_recommender, 'recommend_meal', return_value=[mock_meal]):  # Return list, not dict
                with patch('gui_app.messagebox.showinfo') as mock_info:
                    mock_gui.get_meal_recommendation()

                    # Verify meal info is shown
                    mock_info.assert_called_once()
                    message = mock_info.call_args[0][1]
                    assert "Chicken Dinner" in message
                    assert "800" in message


class TestInventoryButtons:
    """Test Inventory tab buttons."""

    def test_refresh_inventory_button(self, mock_gui, temp_db):
        """Test Refresh Inventory button loads items."""
        # Create a user first (required for foreign key)
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_profile (id, name, weight_lbs, dietary_restrictions, food_dislikes, available_equipment) 
            VALUES (?, ?, 150, '[]', '[]', '[]')
        """, (1, "Test User"))
        
        # Create test inventory
        cursor.execute("""
            INSERT INTO inventory
            (user_id, item_name, quantity, unit, category, location, expiration_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (1, "Chicken Breast", 2.5, "lbs", "protein", "fridge", date.today() + timedelta(days=7)))
        cursor.execute("""
            INSERT INTO inventory
            (user_id, item_name, quantity, unit, category, location, expiration_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (1, "Rice", 5.0, "lbs", "grain", "pantry", date.today() + timedelta(days=365)))
        conn.commit()
        conn.close()

        mock_gui.current_user_id = 1
        
        # Refresh inventory
        mock_gui.refresh_inventory()

        # Verify items are displayed
        items = mock_gui.inventory_tree.get_children()
        assert len(items) == 2

    def test_add_inventory_button_requires_name(self, mock_gui):
        """Test Add Item button requires a name."""
        mock_gui.inv_name_var.set("")

        with patch('gui_app.messagebox.showwarning') as mock_warning:
            mock_gui.add_inventory_item()
            mock_warning.assert_called_once()

    def test_add_inventory_button_adds_item(self, mock_gui, temp_db):
        """Test Add Item button creates inventory item."""
        # Create a user first (required for foreign key)
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_profile (id, name, weight_lbs, dietary_restrictions, food_dislikes, available_equipment) 
            VALUES (?, ?, 150, '[]', '[]', '[]')
        """, (1, "Test User"))
        conn.commit()
        conn.close()
        
        mock_gui.current_user_id = 1
        
        # Set form values
        mock_gui.inv_name_var.set("Salmon")
        mock_gui.inv_qty_var.set(1.5)
        mock_gui.inv_unit_var.set("lbs")
        mock_gui.inv_cat_var.set("protein")
        mock_gui.inv_loc_var.set("freezer")
        mock_gui.inv_days_var.set(30)

        with patch('gui_app.messagebox.showinfo') as mock_info:
            mock_gui.add_inventory_item()
            mock_info.assert_called_once()

        # Verify item was added
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory WHERE item_name = ?", ("Salmon",))
        item = cursor.fetchone()
        conn.close()

        assert item is not None
        # Check item_name (column index may vary, so check by name)
        # item[0] = id, item[1] = user_id, item[2] = item_name, item[3] = quantity, item[4] = unit
        assert item[2] == "Salmon"  # item_name
        assert item[3] == 1.5  # quantity
        assert item[4] == "lbs"  # unit


class TestSearchButtons:
    """Test Search Recipes tab buttons."""

    def test_search_button_requires_query(self, mock_gui):
        """Test Search button requires a query."""
        mock_gui.search_var.set("")

        with patch('gui_app.messagebox.showwarning') as mock_warning:
            mock_gui.search_recipes()
            mock_warning.assert_called_once()

    def test_search_button_calls_api(self, mock_gui):
        """Test Search button calls recipe search API."""
        mock_gui.search_var.set("chicken")
        mock_gui.search_cal_var.set(600)
        mock_gui.search_protein_var.set(30)
        mock_gui.search_time_var.set(45)

        # Mock search results
        mock_results = [
            {
                'id': 12345,
                'title': 'Grilled Chicken',
                'readyInMinutes': 30,
                'nutrition': {
                    'calories': 450,
                    'protein': 40,
                    'carbs': 20,
                    'fat': 15
                },
                'is_validated': True
            }
        ]

        with patch.object(mock_gui.meal_recommender, 'search_online_recipes', return_value=mock_results) as mock_search:
            mock_gui.search_recipes()

            # Verify search was called with filters
            mock_search.assert_called_once()
            assert mock_search.call_args[1]['query'] == "chicken"
            assert mock_search.call_args[1]['max_calories'] == 600
            assert mock_search.call_args[1]['min_protein'] == 30
            assert mock_search.call_args[1]['max_ready_time'] == 45

            # Verify results are displayed
            results_content = mock_gui.search_results_text.get('1.0', tk.END)
            assert "Grilled Chicken" in results_content

    def test_search_button_handles_no_results(self, mock_gui):
        """Test Search button handles no results."""
        mock_gui.search_var.set("impossible recipe query xyz")

        with patch.object(mock_gui.meal_recommender, 'search_online_recipes', return_value=[]):
            mock_gui.search_recipes()

            # Verify no results message
            results_content = mock_gui.search_results_text.get('1.0', tk.END)
            assert "No recipes found" in results_content

    def test_search_button_handles_api_error(self, mock_gui):
        """Test Search button handles API errors."""
        mock_gui.search_var.set("chicken")

        with patch.object(mock_gui.meal_recommender, 'search_online_recipes', side_effect=Exception("API Error")):
            with patch('gui_app.messagebox.showerror') as mock_error:
                mock_gui.search_recipes()
                mock_error.assert_called_once()


class TestButtonCallbacks:
    """Test button callback behavior."""

    def test_all_buttons_have_callbacks(self, mock_gui):
        """Test that all buttons have valid callback functions."""
        # Check that button commands are callable
        assert callable(mock_gui.save_profile)
        assert callable(mock_gui.load_user)
        assert callable(mock_gui.generate_targets)
        assert callable(mock_gui.refresh_dashboard)
        assert callable(mock_gui.refresh_meals)
        assert callable(mock_gui.get_meal_recommendation)
        assert callable(mock_gui.refresh_inventory)
        assert callable(mock_gui.add_inventory_item)
        assert callable(mock_gui.search_recipes)

    def test_button_callbacks_update_status_bar(self, mock_gui, temp_db):
        """Test that button callbacks update the status bar."""
        # Create user
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_profile (id, name, weight_lbs, dietary_restrictions, food_dislikes, available_equipment) VALUES (?, ?, 150, '[]', '[]', '[]')
        """, (1, "Test User"))
        conn.commit()
        conn.close()

        mock_gui.current_user_id = 1

        # Test refresh_meals updates status
        mock_gui.refresh_meals()
        assert "Loaded" in mock_gui.status_bar.cget('text')

        # Test refresh_inventory updates status
        mock_gui.refresh_inventory()
        assert "Loaded" in mock_gui.status_bar.cget('text')


class TestFormValidation:
    """Test form validation for buttons."""

    def test_save_profile_validates_required_fields(self, mock_gui):
        """Test Save Profile validates required fields."""
        # Empty name should fail
        mock_gui.name_var.set("")

        with patch('gui_app.messagebox.showwarning'):
            mock_gui.save_profile()
            # Should not create user

    def test_numeric_fields_accept_valid_input(self, mock_gui, temp_db):
        """Test numeric fields accept valid input."""
        mock_gui.name_var.set("Test")
        mock_gui.age_var.set(30)
        mock_gui.weight_var.set(180)
        mock_gui.bodyfat_var.set(15.5)
        mock_gui.budget_var.set(100.50)

        with patch('gui_app.messagebox.showinfo'):
            mock_gui.save_profile()

        # Verify values were saved correctly
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT age, weight_lbs, body_fat_pct, weekly_budget_usd FROM user_profile WHERE name = ?", ("Test",))
        result = cursor.fetchone()
        conn.close()

        assert result[0] == 30
        assert result[1] == 180
        assert result[2] == 15.5
        assert result[3] == 100.50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
