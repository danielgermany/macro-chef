"""
Configuration management for the meal planner system.
Loads environment variables, API keys, and paths.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_PATH = PROJECT_ROOT / "database" / "meal_planner.db"
BACKUP_DIR = PROJECT_ROOT / "database" / "backups"
DATA_DIR = PROJECT_ROOT / "data"

# API Keys
SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY", "")
USDA_API_KEY = os.getenv("USDA_API_KEY", "")  # Optional

# API Settings
SPOONACULAR_BASE_URL = "https://api.spoonacular.com"
USDA_BASE_URL = "https://api.nal.usda.gov/fdc/v1"

# App Settings
DEFAULT_USER_ID = 1
MAX_API_RETRIES = 3
API_TIMEOUT = 10  # seconds

# Nutrition Constants
RDA_MALE = {
    'vitamin_d_mcg': 20,
    'vitamin_c_mg': 90,
    'vitamin_a_mcg': 900,
    'calcium_mg': 1000,
    'iron_mg': 8,
    'magnesium_mg': 420,
    'potassium_mg': 3400,
    'zinc_mg': 11,
    'omega3_g': 1.6,
}

RDA_FEMALE = {
    'vitamin_d_mcg': 20,
    'vitamin_c_mg': 75,
    'vitamin_a_mcg': 700,
    'calcium_mg': 1000,
    'iron_mg': 18,
    'magnesium_mg': 320,
    'potassium_mg': 2600,
    'zinc_mg': 8,
    'omega3_g': 1.1,
}

# Athlete multipliers (for very_active and athlete activity levels)
ATHLETE_MICRONUTRIENT_MULTIPLIERS = {
    'vitamin_c_mg': 1.5,
    'magnesium_mg': 1.2,
    'zinc_mg': 1.2,
    'iron_mg': 1.2,
    'potassium_mg': 1.2,
}
