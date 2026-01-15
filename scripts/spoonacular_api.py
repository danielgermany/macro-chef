"""
Spoonacular API integration for recipe and nutrition data.
Handles recipe search, nutrition lookup, and data caching.
"""

import requests
import json
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from scripts.db_manager import DatabaseManager
from config.config import (
    SPOONACULAR_API_KEY,
    SPOONACULAR_BASE_URL,
    MAX_API_RETRIES,
    API_TIMEOUT
)


class SpoonacularAPI(DatabaseManager):
    """Interface to Spoonacular API with caching."""

    def __init__(self):
        super().__init__()
        self.api_key = SPOONACULAR_API_KEY
        self.base_url = SPOONACULAR_BASE_URL

        if not self.api_key:
            print("[WARNING] SPOONACULAR_API_KEY not set in .env file")

    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with retry logic."""

        if not self.api_key:
            print("[ERROR] API key not configured")
            return None

        url = f"{self.base_url}/{endpoint}"

        # Add API key to params
        if params is None:
            params = {}
        params['apiKey'] = self.api_key

        for attempt in range(MAX_API_RETRIES):
            try:
                response = requests.get(url, params=params, timeout=API_TIMEOUT)

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 400:
                    print(f"[ERROR] Bad request (400): Invalid parameters")
                    return None  # Don't retry client errors
                elif response.status_code == 401:
                    print("[ERROR] Invalid API key")
                    return None  # Don't retry authentication errors
                elif response.status_code == 402:
                    print("[ERROR] API quota exceeded")
                    return None  # Don't retry quota errors
                else:
                    print(f"[WARNING] API request failed: {response.status_code}")
                    # Only retry on server errors (5xx), not client errors (4xx)
                    if response.status_code >= 500:
                        # Continue to retry logic below
                        pass
                    else:
                        return None  # Don't retry other client errors

            except requests.exceptions.Timeout:
                print(f"[WARNING] Request timeout (attempt {attempt + 1}/{MAX_API_RETRIES})")
            except requests.exceptions.RequestException as e:
                print(f"[WARNING] Request error: {e}")

            if attempt < MAX_API_RETRIES - 1:
                time.sleep(1)  # Wait before retry

        return None

    def search_recipes(
        self,
        query: str,
        max_results: int = 10,
        diet: Optional[str] = None,
        intolerances: Optional[List[str]] = None,
        max_ready_time: Optional[int] = None,
        min_protein: Optional[int] = None,
        max_calories: Optional[int] = None
    ) -> List[Dict]:
        """
        Search for recipes.

        Args:
            query: Search query (e.g., "chicken breast")
            max_results: Number of results (default: 10)
            diet: Diet type (vegetarian, vegan, etc.)
            intolerances: List of intolerances (dairy, gluten, etc.)
            max_ready_time: Max cooking time in minutes
            min_protein: Minimum protein in grams
            max_calories: Maximum calories
        """

        params = {
            'query': query,
            'number': max_results,
            'addRecipeNutrition': True,
            'fillIngredients': True
        }

        if diet:
            params['diet'] = diet
        if intolerances:
            params['intolerances'] = ','.join(intolerances)
        if max_ready_time:
            params['maxReadyTime'] = max_ready_time
        if min_protein:
            params['minProtein'] = min_protein
        if max_calories:
            params['maxCalories'] = max_calories

        result = self._make_request('recipes/complexSearch', params)

        if result and 'results' in result:
            print(f"[SUCCESS] Found {len(result['results'])} recipes")
            return result['results']

        return []

    def get_recipe_information(self, recipe_id: int) -> Optional[Dict]:
        """Get detailed recipe information including nutrition."""

        params = {
            'includeNutrition': True
        }

        result = self._make_request(f'recipes/{recipe_id}/information', params)

        if result:
            print(f"[SUCCESS] Retrieved recipe: {result.get('title', 'Unknown')}")

        return result

    def get_ingredient_nutrition(self, ingredient_name: str, amount: float = 100, unit: str = "grams") -> Optional[Dict]:
        """
        Get nutrition info for a specific ingredient.
        Checks cache first, then fetches from API.
        """

        # Check cache first
        cached = self._get_from_cache(ingredient_name)
        if cached:
            print(f"[CACHE] Using cached data for {ingredient_name}")
            return cached

        # Fetch from API
        params = {
            'ingredientName': ingredient_name,
            'amount': amount,
            'unit': unit
        }

        result = self._make_request('recipes/ingredientWidget.json', params)

        if result:
            # Cache the result
            self._save_to_cache(ingredient_name, result, amount, unit)
            print(f"[SUCCESS] Retrieved nutrition for {ingredient_name}")
            return result

        return None

    def parse_recipe_to_template(self, recipe_data: Dict, user_id: int = 1) -> Dict:
        """Convert Spoonacular recipe to meal template format."""

        nutrition = recipe_data.get('nutrition', {})
        nutrients = {n['name'].lower(): n['amount'] for n in nutrition.get('nutrients', [])}

        # Extract macro and micronutrients
        template = {
            'user_id': user_id,
            'name': recipe_data.get('title', 'Unknown Recipe'),
            'description': recipe_data.get('summary', '').replace('<b>', '').replace('</b>', ''),
            'meal_type': self._guess_meal_type(recipe_data),
            'prep_time_minutes': recipe_data.get('preparationMinutes'),
            'cook_time_minutes': recipe_data.get('cookingMinutes'),
            'total_time_minutes': recipe_data.get('readyInMinutes'),
            'difficulty': 'medium',  # API doesn't provide this
            'servings': recipe_data.get('servings', 1),
            'recipe_instructions': self._format_instructions(recipe_data.get('analyzedInstructions', [])),
            'recipe_source': recipe_data.get('sourceUrl', f"spoonacular:{recipe_data.get('id')}"),

            # Macros
            'calories': int(nutrients.get('calories', 0)),
            'protein_g': round(nutrients.get('protein', 0), 1),
            'carbs_g': round(nutrients.get('carbohydrates', 0), 1),
            'fat_g': round(nutrients.get('fat', 0), 1),
            'fiber_g': round(nutrients.get('fiber', 0), 1),

            # Other
            'sugar_g': round(nutrients.get('sugar', 0), 1),
            'saturated_fat_g': round(nutrients.get('saturated fat', 0), 1),
            'sodium_mg': round(nutrients.get('sodium', 0), 1),
            'cholesterol_mg': round(nutrients.get('cholesterol', 0), 1),

            # Micronutrients
            'vitamin_d_mcg': round(nutrients.get('vitamin d', 0), 1),
            'vitamin_c_mg': round(nutrients.get('vitamin c', 0), 1),
            'vitamin_a_mcg': round(nutrients.get('vitamin a', 0) / 3.33, 1) if nutrients.get('vitamin a') else None,  # Convert IU to mcg
            'calcium_mg': round(nutrients.get('calcium', 0), 1),
            'iron_mg': round(nutrients.get('iron', 0), 1),
            'magnesium_mg': round(nutrients.get('magnesium', 0), 1),
            'potassium_mg': round(nutrients.get('potassium', 0), 1),
            'zinc_mg': round(nutrients.get('zinc', 0), 1),
            'omega3_g': None,  # Not typically provided

            # Cost (if available)
            'cost_estimate_usd': recipe_data.get('pricePerServing', 0) / 100 if recipe_data.get('pricePerServing') else None,

            # Tags
            'tags': json.dumps(self._extract_tags(recipe_data)),

            # Flags
            'is_batch_friendly': recipe_data.get('servings', 1) >= 4,
            'can_freeze': False  # Would need custom logic
        }

        return template

    def _guess_meal_type(self, recipe_data: Dict) -> str:
        """Guess meal type from recipe data."""
        title = recipe_data.get('title', '').lower()
        dish_types = recipe_data.get('dishTypes', [])

        if 'breakfast' in dish_types or any(word in title for word in ['breakfast', 'pancake', 'waffle', 'omelette']):
            return 'breakfast'
        elif 'lunch' in dish_types or 'main course' in dish_types:
            return 'lunch'
        elif 'dinner' in dish_types or 'main dish' in dish_types:
            return 'dinner'
        else:
            return 'snack'

    def _format_instructions(self, analyzed_instructions: List) -> str:
        """Format recipe instructions from Spoonacular format."""
        if not analyzed_instructions:
            return "No instructions available"

        instructions = []
        for section in analyzed_instructions:
            steps = section.get('steps', [])
            for step in steps:
                instructions.append(f"{step['number']}. {step['step']}")

        return '\n'.join(instructions)

    def _extract_tags(self, recipe_data: Dict) -> List[str]:
        """Extract tags from recipe data."""
        tags = []

        # Add diet tags
        diets = recipe_data.get('diets', [])
        tags.extend(diets)

        # Add dish types
        dish_types = recipe_data.get('dishTypes', [])
        tags.extend(dish_types)

        # Add time-based tags
        ready_time = recipe_data.get('readyInMinutes', 0)
        if ready_time <= 30:
            tags.append('quick')

        # Add cost tags
        price_per_serving = recipe_data.get('pricePerServing', 0) / 100
        if price_per_serving and price_per_serving < 3:
            tags.append('budget')

        # Add health tags
        if recipe_data.get('veryHealthy'):
            tags.append('healthy')

        return list(set(tags))  # Remove duplicates

    def _get_from_cache(self, food_name: str) -> Optional[Dict]:
        """Get nutrition data from cache."""
        query = """
            SELECT * FROM food_nutrition_cache
            WHERE food_name = ?
            AND datetime(last_updated) > datetime('now', '-30 days')
        """

        result = self.execute_single(query, (food_name.lower(),))

        if result:
            return {
                'name': result['food_name'],
                'amount': result['serving_size'],
                'unit': result['serving_unit'],
                'calories': result['calories'],
                'protein': result['protein_g'],
                'carbs': result['carbs_g'],
                'fat': result['fat_g'],
                'fiber': result['fiber_g']
            }

        return None

    def _save_to_cache(self, food_name: str, nutrition_data: Dict, amount: float, unit: str):
        """Save nutrition data to cache."""

        # Extract nutrients from Spoonacular format
        nutrients = nutrition_data.get('nutrition', {}).get('nutrients', [])
        nutrient_map = {n['name'].lower(): n['amount'] for n in nutrients}

        query = """
            INSERT OR REPLACE INTO food_nutrition_cache (
                food_name, serving_size, serving_unit,
                calories, protein_g, carbs_g, fat_g, fiber_g,
                sugar_g, saturated_fat_g, sodium_mg, cholesterol_mg,
                data_source, source_id, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            food_name.lower(),
            amount,
            unit,
            nutrient_map.get('calories', 0),
            nutrient_map.get('protein', 0),
            nutrient_map.get('carbohydrates', 0),
            nutrient_map.get('fat', 0),
            nutrient_map.get('fiber', 0),
            nutrient_map.get('sugar', 0),
            nutrient_map.get('saturated fat', 0),
            nutrient_map.get('sodium', 0),
            nutrient_map.get('cholesterol', 0),
            'spoonacular',
            nutrition_data.get('id'),
            datetime.now()
        )

        self.execute_write(query, params)


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Spoonacular API Interface")
    parser.add_argument('--search', type=str, help='Search for recipes')
    parser.add_argument('--recipe-id', type=int, help='Get recipe by ID')
    parser.add_argument('--ingredient', type=str, help='Get ingredient nutrition')

    # Search filters
    parser.add_argument('--max-time', type=int, help='Max cooking time (minutes)')
    parser.add_argument('--min-protein', type=int, help='Min protein (grams)')
    parser.add_argument('--max-calories', type=int, help='Max calories')
    parser.add_argument('--diet', type=str, help='Diet type (vegetarian, vegan, etc.)')
    parser.add_argument('--results', type=int, default=5, help='Number of results (default: 5)')

    args = parser.parse_args()

    api = SpoonacularAPI()

    if args.search:
        print(f"\nSearching for: {args.search}")
        print("=" * 60)

        recipes = api.search_recipes(
            query=args.search,
            max_results=args.results,
            max_ready_time=args.max_time,
            min_protein=args.min_protein,
            max_calories=args.max_calories,
            diet=args.diet
        )

        if recipes:
            for i, recipe in enumerate(recipes, 1):
                nutrition = recipe.get('nutrition', {})
                nutrients = {n['name']: n['amount'] for n in nutrition.get('nutrients', [])}

                print(f"\n{i}. {recipe['title']}")
                print(f"   ID: {recipe['id']} | Ready in: {recipe.get('readyInMinutes', 'N/A')} min")
                print(f"   Calories: {nutrients.get('Calories', 'N/A')} | Protein: {nutrients.get('Protein', 'N/A')}g")
                if recipe.get('pricePerServing'):
                    print(f"   Cost per serving: ${recipe['pricePerServing'] / 100:.2f}")
        else:
            print("No recipes found")

    elif args.recipe_id:
        print(f"\nFetching recipe ID: {args.recipe_id}")
        print("=" * 60)

        recipe = api.get_recipe_information(args.recipe_id)

        if recipe:
            print(f"\nTitle: {recipe['title']}")
            print(f"Servings: {recipe.get('servings', 'N/A')}")
            print(f"Ready in: {recipe.get('readyInMinutes', 'N/A')} minutes")
            print(f"Source: {recipe.get('sourceUrl', 'N/A')}")

            nutrition = recipe.get('nutrition', {})
            nutrients = {n['name']: n['amount'] for n in nutrition.get('nutrients', [])}

            print("\nNutrition (per serving):")
            print(f"  Calories: {nutrients.get('Calories', 'N/A')}")
            print(f"  Protein: {nutrients.get('Protein', 'N/A')}g")
            print(f"  Carbs: {nutrients.get('Carbohydrates', 'N/A')}g")
            print(f"  Fat: {nutrients.get('Fat', 'N/A')}g")

            # Show if it can be converted to template
            template = api.parse_recipe_to_template(recipe)
            print(f"\nCan be imported as: {template['meal_type']}")
            print(f"Tags: {', '.join(json.loads(template['tags']))}")

    elif args.ingredient:
        print(f"\nLooking up nutrition for: {args.ingredient}")
        print("=" * 60)

        nutrition = api.get_ingredient_nutrition(args.ingredient)

        if nutrition:
            print(f"\nIngredient: {nutrition.get('name', args.ingredient)}")
            print(f"Amount: {nutrition.get('amount', 'N/A')} {nutrition.get('unit', '')}")

            nutrients = nutrition.get('nutrition', {}).get('nutrients', [])
            print("\nNutrition:")
            for nutrient in nutrients[:10]:  # Show top 10
                print(f"  {nutrient['name']}: {nutrient['amount']}{nutrient['unit']}")
        else:
            print("Nutrition data not found")

    else:
        parser.print_help()
