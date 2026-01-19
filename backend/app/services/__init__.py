"""
Service layer - imports existing business logic from scripts/
"""
import sys
from pathlib import Path

# Add scripts directory to path
scripts_path = Path(__file__).parent.parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_path))

# Add config directory to path
config_path = Path(__file__).parent.parent.parent.parent / "config"
sys.path.insert(0, str(config_path))

# Re-export managers
from user_profile import UserProfileManager
from nutrition_calculator import NutritionCalculator
from meal_tracker import MealTracker
from meal_recommender import MealRecommender
from inventory_manager import InventoryManager
from weekly_planner import WeeklyPlanner
from budget_tracker import BudgetTracker
from shopping_list import ShoppingListGenerator
from spoonacular_api import SpoonacularAPI
from usda_api import USDAAPI

__all__ = [
    "UserProfileManager",
    "NutritionCalculator",
    "MealTracker",
    "MealRecommender",
    "InventoryManager",
    "WeeklyPlanner",
    "BudgetTracker",
    "ShoppingListGenerator",
    "SpoonacularAPI",
    "USDAAPI",
]
