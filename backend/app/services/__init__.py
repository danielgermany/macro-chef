"""
Service layer - imports existing business logic from scripts/
"""
import sys
from pathlib import Path

# Add project root to path so imports work correctly
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Re-export managers (imports will work from project root)
from scripts.user_profile import UserProfileManager
from scripts.nutrition_calculator import NutritionCalculator
from scripts.meal_tracker import MealTracker
from scripts.meal_recommender import MealRecommender
from scripts.inventory_manager import InventoryManager
from scripts.weekly_planner import WeeklyPlanner
from scripts.budget_tracker import BudgetTracker
from scripts.shopping_list import ShoppingListGenerator
from scripts.spoonacular_api import SpoonacularAPI
from scripts.usda_api import USDAAPI
from scripts.usda_api import USDAAPI

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
