"""
USDA FoodData Central API integration.
Backup nutrition data source for foods not found in Spoonacular.
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from scripts.db_manager import DatabaseManager
from config.config import (
    USDA_API_KEY,
    USDA_BASE_URL,
    MAX_API_RETRIES,
    API_TIMEOUT
)


class USDAAPI(DatabaseManager):
    """Interface to USDA FoodData Central API with caching."""

    def __init__(self, db_path=None):
        super().__init__(db_path=db_path)
        self.api_key = USDA_API_KEY
        self.base_url = USDA_BASE_URL

        # USDA API key is optional (has public access with rate limits)
        if not self.api_key:
            print("[INFO] USDA_API_KEY not set - using public access (limited rate)")

    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with retry logic."""

        url = f"{self.base_url}/{endpoint}"

        # Add API key if available
        if params is None:
            params = {}
        if self.api_key:
            params['api_key'] = self.api_key

        for attempt in range(MAX_API_RETRIES):
            try:
                response = requests.get(url, params=params, timeout=API_TIMEOUT)

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 403:
                    print("[ERROR] API access forbidden - check API key")
                    return None
                elif response.status_code == 429:
                    print("[ERROR] Rate limit exceeded")
                    return None
                else:
                    print(f"[WARNING] API request failed: {response.status_code}")

            except requests.exceptions.Timeout:
                print(f"[WARNING] Request timeout (attempt {attempt + 1}/{MAX_API_RETRIES})")
            except requests.exceptions.RequestException as e:
                print(f"[WARNING] Request error: {e}")

        return None

    def search_foods(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search USDA food database.

        Args:
            query: Search query (e.g., "chicken breast")
            max_results: Number of results (default: 10)
        """

        params = {
            'query': query,
            'pageSize': max_results,
            'dataType': ['Survey (FNDDS)', 'Foundation', 'SR Legacy']  # Focus on verified data
        }

        result = self._make_request('foods/search', params)

        if result and 'foods' in result:
            print(f"[SUCCESS] Found {len(result['foods'])} foods")
            return result['foods']

        return []

    def get_food_details(self, fdc_id: int) -> Optional[Dict]:
        """Get detailed nutrition data for a specific food by FDC ID."""

        result = self._make_request(f'food/{fdc_id}')

        if result:
            print(f"[SUCCESS] Retrieved: {result.get('description', 'Unknown')}")

        return result

    def get_nutrition_from_search(self, query: str) -> Optional[Dict]:
        """
        Search for food and return nutrition data for best match.
        Checks cache first.
        """

        # Check cache
        cached = self._get_from_cache(query)
        if cached:
            print(f"[CACHE] Using cached data for {query}")
            return cached

        # Search USDA
        foods = self.search_foods(query, max_results=1)

        if not foods:
            return None

        # Get first result
        food = foods[0]
        fdc_id = food.get('fdcId')

        # Get detailed nutrition
        details = self.get_food_details(fdc_id)

        if details:
            nutrition = self._parse_nutrition(details)
            # Cache the result
            self._save_to_cache(query, nutrition, details)
            return nutrition

        return None

    def _parse_nutrition(self, food_data: Dict) -> Dict:
        """Parse USDA food data into standardized nutrition format."""

        # Extract nutrients
        nutrients = food_data.get('foodNutrients', [])
        nutrient_map = {}

        for nutrient in nutrients:
            name = nutrient.get('nutrient', {}).get('name', '').lower()
            amount = nutrient.get('amount', 0)
            nutrient_map[name] = amount

        # Map to our standard format (per 100g)
        nutrition = {
            'name': food_data.get('description', 'Unknown'),
            'fdc_id': food_data.get('fdcId'),
            'data_type': food_data.get('dataType'),
            'serving_size': 100,
            'serving_unit': 'g',

            # Macros
            'calories': nutrient_map.get('energy', 0),
            'protein_g': nutrient_map.get('protein', 0),
            'carbs_g': nutrient_map.get('carbohydrate, by difference', 0),
            'fat_g': nutrient_map.get('total lipid (fat)', 0),
            'fiber_g': nutrient_map.get('fiber, total dietary', 0),

            # Other
            'sugar_g': nutrient_map.get('sugars, total including nlea', nutrient_map.get('sugars, total', 0)),
            'saturated_fat_g': nutrient_map.get('fatty acids, total saturated', 0),
            'sodium_mg': nutrient_map.get('sodium, na', 0),
            'cholesterol_mg': nutrient_map.get('cholesterol', 0),

            # Micronutrients
            'vitamin_d_mcg': nutrient_map.get('vitamin d (d2 + d3)', 0),
            'vitamin_c_mg': nutrient_map.get('vitamin c, total ascorbic acid', 0),
            'vitamin_a_mcg': nutrient_map.get('vitamin a, rae', 0),
            'calcium_mg': nutrient_map.get('calcium, ca', 0),
            'iron_mg': nutrient_map.get('iron, fe', 0),
            'magnesium_mg': nutrient_map.get('magnesium, mg', 0),
            'potassium_mg': nutrient_map.get('potassium, k', 0),
            'zinc_mg': nutrient_map.get('zinc, zn', 0),

            # Omega-3 (multiple forms, sum them)
            'omega3_g': sum([
                nutrient_map.get('18:3 n-3 c,c,c (ala)', 0),
                nutrient_map.get('20:5 n-3 (epa)', 0),
                nutrient_map.get('22:6 n-3 (dha)', 0)
            ])
        }

        return nutrition

    def _get_from_cache(self, food_name: str) -> Optional[Dict]:
        """Get nutrition data from cache."""
        query = """
            SELECT * FROM food_nutrition_cache
            WHERE food_name = ? AND data_source = 'usda'
            AND datetime(last_updated) > datetime('now', '-30 days')
        """

        result = self.execute_single(query, (food_name.lower(),))

        if result:
            return {
                'name': result['food_name'],
                'serving_size': result['serving_size'],
                'serving_unit': result['serving_unit'],
                'calories': result['calories'],
                'protein_g': result['protein_g'],
                'carbs_g': result['carbs_g'],
                'fat_g': result['fat_g'],
                'fiber_g': result['fiber_g'],
                'sugar_g': result['sugar_g'],
                'saturated_fat_g': result['saturated_fat_g'],
                'sodium_mg': result['sodium_mg'],
                'cholesterol_mg': result['cholesterol_mg']
            }

        return None

    def _save_to_cache(self, food_name: str, nutrition: Dict, food_data: Dict):
        """Save nutrition data to cache."""

        query = """
            INSERT OR REPLACE INTO food_nutrition_cache (
                food_name, serving_size, serving_unit,
                calories, protein_g, carbs_g, fat_g, fiber_g,
                sugar_g, saturated_fat_g, sodium_mg, cholesterol_mg,
                vitamin_d_mcg, vitamin_c_mg, vitamin_a_mcg,
                calcium_mg, iron_mg, magnesium_mg, potassium_mg, zinc_mg,
                omega3_g,
                data_source, source_id, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            food_name.lower(),
            nutrition['serving_size'],
            nutrition['serving_unit'],
            nutrition['calories'],
            nutrition['protein_g'],
            nutrition['carbs_g'],
            nutrition['fat_g'],
            nutrition['fiber_g'],
            nutrition['sugar_g'],
            nutrition['saturated_fat_g'],
            nutrition['sodium_mg'],
            nutrition['cholesterol_mg'],
            nutrition['vitamin_d_mcg'],
            nutrition['vitamin_c_mg'],
            nutrition['vitamin_a_mcg'],
            nutrition['calcium_mg'],
            nutrition['iron_mg'],
            nutrition['magnesium_mg'],
            nutrition['potassium_mg'],
            nutrition['zinc_mg'],
            nutrition['omega3_g'],
            'usda',
            str(food_data.get('fdcId')),
            datetime.now()
        )

        self.execute_write(query, params)
        print(f"[SUCCESS] Cached nutrition data for {food_name}")


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="USDA FoodData Central API Interface")
    parser.add_argument('--search', type=str, help='Search for food')
    parser.add_argument('--fdc-id', type=int, help='Get food by FDC ID')
    parser.add_argument('--nutrition', type=str, help='Get nutrition for food')
    parser.add_argument('--results', type=int, default=10, help='Number of results (default: 10)')

    args = parser.parse_args()

    api = USDAAPI()

    if args.search:
        print(f"\nSearching USDA database for: {args.search}")
        print("=" * 80)

        foods = api.search_foods(args.search, max_results=args.results)

        if foods:
            for i, food in enumerate(foods, 1):
                print(f"\n{i}. {food.get('description', 'Unknown')}")
                print(f"   FDC ID: {food.get('fdcId')} | Type: {food.get('dataType', 'N/A')}")

                # Show basic nutrients if available
                nutrients = food.get('foodNutrients', [])
                if nutrients:
                    for nutrient in nutrients[:4]:  # Show first 4
                        name = nutrient.get('nutrientName', 'Unknown')
                        value = nutrient.get('value', 'N/A')
                        unit = nutrient.get('unitName', '')
                        print(f"   {name}: {value} {unit}")
        else:
            print("No foods found")

    elif args.fdc_id:
        print(f"\nFetching FDC ID: {args.fdc_id}")
        print("=" * 80)

        food = api.get_food_details(args.fdc_id)

        if food:
            nutrition = api._parse_nutrition(food)

            print(f"\nFood: {nutrition['name']}")
            print(f"Type: {nutrition['data_type']}")
            print(f"\nNutrition (per 100g):")
            print(f"  Calories: {nutrition['calories']:.0f} kcal")
            print(f"  Protein: {nutrition['protein_g']:.1f}g")
            print(f"  Carbs: {nutrition['carbs_g']:.1f}g")
            print(f"  Fat: {nutrition['fat_g']:.1f}g")
            print(f"  Fiber: {nutrition['fiber_g']:.1f}g")

            if nutrition['vitamin_c_mg'] > 0:
                print(f"\nKey Micronutrients:")
                print(f"  Vitamin C: {nutrition['vitamin_c_mg']:.1f}mg")
                print(f"  Calcium: {nutrition['calcium_mg']:.0f}mg")
                print(f"  Iron: {nutrition['iron_mg']:.1f}mg")

    elif args.nutrition:
        print(f"\nLooking up nutrition for: {args.nutrition}")
        print("=" * 80)

        nutrition = api.get_nutrition_from_search(args.nutrition)

        if nutrition:
            print(f"\nFood: {nutrition['name']}")
            print(f"Serving: {nutrition['serving_size']}{nutrition['serving_unit']}")
            print(f"\nMacronutrients:")
            print(f"  Calories: {nutrition['calories']:.0f} kcal")
            print(f"  Protein: {nutrition['protein_g']:.1f}g")
            print(f"  Carbs: {nutrition['carbs_g']:.1f}g")
            print(f"  Fat: {nutrition['fat_g']:.1f}g")
            print(f"  Fiber: {nutrition['fiber_g']:.1f}g")
        else:
            print("Nutrition data not found")

    else:
        parser.print_help()
