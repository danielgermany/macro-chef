"""
Intelligent meal recommendation engine.
Suggests meals based on remaining macros, inventory, budget, and preferences.
"""

from datetime import date
from typing import Dict, List, Optional, Tuple
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from scripts.db_manager import DatabaseManager
from scripts.meal_tracker import MealTracker
from scripts.inventory_manager import InventoryManager
from scripts.user_profile import UserProfileManager
from scripts.spoonacular_api import SpoonacularAPI
from scripts.usda_api import USDAAPI
from config.config import DEFAULT_USER_ID


class MealRecommender(DatabaseManager):
    """Recommend meals based on user needs and constraints."""

    def __init__(self):
        super().__init__()
        self.meal_tracker = MealTracker()
        self.inventory_manager = InventoryManager()
        self.user_manager = UserProfileManager()
        self.spoonacular_api = SpoonacularAPI()
        self.usda_api = USDAAPI()

    def recommend_meal(
        self,
        meal_time: str = "dinner",
        user_id: int = DEFAULT_USER_ID,
        target_date: date = None,
        max_time: Optional[int] = None,
        use_inventory: bool = True,
        budget_limit: Optional[float] = None,
        allow_online_search: bool = True
    ) -> List[Dict]:
        """
        Recommend meals based on current progress and constraints.
        Falls back to online search if local database has <5 suitable meals.

        Args:
            meal_time: Meal type (breakfast, lunch, dinner, snack)
            user_id: User ID
            target_date: Date for recommendations (default: today)
            max_time: Maximum cooking time in minutes
            use_inventory: Consider inventory when recommending
            budget_limit: Maximum cost per meal
            allow_online_search: Allow fallback to Spoonacular API (default: True)
        """

        if not target_date:
            target_date = date.today()

        # Get user profile for preferences
        user = self.user_manager.get_user(user_id)
        if not user:
            print("[ERROR] User not found")
            return []

        # Get daily progress to know remaining macros
        progress = self.meal_tracker.get_daily_progress(user_id, target_date)
        remaining = progress['remaining']

        print(f"\n[INFO] Recommending {meal_time} meals")
        print(f"Remaining today: {remaining['calories']} kcal | P: {remaining['protein_g']:.0f}g | C: {remaining['carbs_g']:.0f}g | F: {remaining['fat_g']:.0f}g")

        # Build recommendation criteria
        criteria = {
            'meal_time': meal_time,
            'target_calories': remaining['calories'] // (4 - progress['meal_count']) if progress['meal_count'] < 4 else remaining['calories'],
            'min_protein': max(0, remaining['protein_g'] * 0.8 // (4 - progress['meal_count'])) if progress['meal_count'] < 4 else remaining['protein_g'] * 0.8,
            'max_calories': remaining['calories'],
            'dietary_restrictions': user.get('dietary_restrictions', []),
            'food_dislikes': user.get('food_dislikes', []),
            'max_time': max_time or (60 if user['cooking_frequency'] == 'daily' else 120),
            'difficulty': user['cooking_skill'],
            'budget_limit': budget_limit
        }

        # Get candidate meals from database
        candidates = self._get_candidate_meals(user_id, criteria)
        print(f"[INFO] Found {len(candidates)} local meal candidates")

        # FALLBACK LOGIC - Search online if insufficient local results
        if len(candidates) < 5 and allow_online_search:
            print(f"[INFO] Triggering online search (threshold: 5, found: {len(candidates)})")

            # Add user_id to criteria for online search
            criteria['user_id'] = user_id

            try:
                online_recipes = self._search_online_recipes(criteria, max_results=10)

                if online_recipes:
                    candidates.extend(online_recipes)
                    print(f"[SUCCESS] Added {len(online_recipes)} online recipes")
                else:
                    print("[INFO] No online recipes available, using local results only")

            except Exception as e:
                print(f"[ERROR] Online search failed: {e}")
                print("[INFO] Falling back to local results only")

        # Check if we have any candidates at all
        if not candidates:
            print("[WARNING] No suitable meals found (local or online)")
            return []

        # Score and rank candidates
        scored_candidates = []
        for candidate in candidates:
            score = self._score_meal(candidate, criteria, remaining, use_inventory, user_id)
            scored_candidates.append((candidate, score))

        # Sort by score (descending)
        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        # Return top recommendations with scores
        recommendations = []
        for candidate, score in scored_candidates[:10]:
            recommendation = candidate.copy()
            recommendation['recommendation_score'] = round(score, 2)
            recommendation['match_reasons'] = self._explain_recommendation(candidate, criteria, remaining)
            recommendations.append(recommendation)

        if recommendations:
            print(f"[SUCCESS] Found {len(recommendations)} recommendations")
        else:
            print("[WARNING] No suitable meals found")

        return recommendations

    def save_recommended_meal(self, meal: Dict, user_id: int) -> Optional[int]:
        """
        Save a recommended meal to the database if it's an online recipe.
        Returns the meal_template_id if saved, or None if already exists or is a database meal.
        """
        # If meal already has a database id, it's already saved
        if 'id' in meal and meal['id']:
            return meal['id']

        # Only save online recipes
        api_recipe_id = meal.get('api_recipe_id')
        if not api_recipe_id:
            return None  # Not an online recipe or missing ID

        # Check if recipe already exists
        check_query = "SELECT id FROM meal_templates WHERE api_recipe_id = ?"
        existing = self.execute_single(check_query, (api_recipe_id,))

        if existing:
            return existing['id']  # Already exists

        # Map difficulty levels
        difficulty_map = {
            'easy': 'easy',
            'beginner': 'easy',
            'intermediate': 'medium',
            'medium': 'medium',
            'advanced': 'hard',
            'hard': 'hard'
        }
        difficulty = difficulty_map.get(meal.get('difficulty', 'medium').lower(), 'medium')

        # Insert into meal_templates
        insert_query = """
            INSERT INTO meal_templates (
                user_id, name, meal_type, calories, protein_g, carbs_g, fat_g,
                fiber_g, sugar_g, saturated_fat_g, sodium_mg, cholesterol_mg,
                prep_time_minutes, cook_time_minutes, total_time_minutes, servings,
                difficulty, tags, cost_estimate_usd,
                recipe_instructions, recipe_source, description,
                api_source, api_recipe_id, nutrition_validated,
                price_confidence, price_source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            user_id,
            meal.get('name', 'Unknown Recipe'),
            meal.get('meal_type', 'dinner'),
            int(meal.get('calories', 0)),
            meal.get('protein_g', 0),
            meal.get('carbs_g', 0),
            meal.get('fat_g', 0),
            meal.get('fiber_g'),
            meal.get('sugar_g'),
            meal.get('saturated_fat_g'),
            meal.get('sodium_mg'),
            meal.get('cholesterol_mg'),
            meal.get('prep_time_minutes'),
            meal.get('cook_time_minutes'),
            meal.get('total_time_minutes'),
            meal.get('servings', 1),
            difficulty,
            meal.get('tags'),
            meal.get('cost_estimate_usd'),
            meal.get('recipe_instructions', 'See source URL'),
            meal.get('recipe_source', meal.get('source_url', 'Online')),
            meal.get('description'),
            meal.get('api_source', 'spoonacular'),
            api_recipe_id,
            meal.get('nutrition_validated', False),
            meal.get('price_confidence'),
            meal.get('price_source', 'spoonacular')
        )

        try:
            template_id = self.execute_write(insert_query, params)
            print(f"[SUCCESS] Saved recommended meal to database (template_id: {template_id})")
            
            # Update meal dict with new id
            meal['id'] = template_id
            
            return template_id
        except Exception as e:
            print(f"[ERROR] Failed to save recommended meal: {e}")
            return None

    def _get_candidate_meals(self, user_id: int, criteria: Dict) -> List[Dict]:
        """Get candidate meals from database based on criteria."""

        query = """
            SELECT * FROM meal_templates
            WHERE user_id = ? AND meal_type = ?
        """
        params = [user_id, criteria['meal_time']]

        # Add time constraint
        if criteria['max_time']:
            query += " AND (total_time_minutes IS NULL OR total_time_minutes <= ?)"
            params.append(criteria['max_time'])

        # Add calorie constraint
        if criteria['max_calories']:
            query += " AND calories <= ?"
            params.append(criteria['max_calories'] * 1.2)  # 20% buffer

        # Add difficulty constraint
        if criteria['difficulty'] == 'beginner':
            query += " AND (difficulty IS NULL OR difficulty IN ('easy', 'medium'))"
        elif criteria['difficulty'] == 'intermediate':
            query += " AND (difficulty IS NULL OR difficulty IN ('easy', 'medium', 'hard'))"

        # Order by rating and recency
        query += " ORDER BY rating DESC NULLS LAST, last_made ASC NULLS FIRST"

        return self.execute_query(query, tuple(params))

    def _search_online_recipes(
        self,
        criteria: Dict,
        max_results: int = 10
    ) -> List[Dict]:
        """
        Search Spoonacular API for recipes matching criteria.
        Returns standardized meal dictionaries with metadata.
        """

        # Check API key availability
        if not self.spoonacular_api.api_key:
            print("[WARNING] Spoonacular API key not configured")
            return []

        try:
            # Build search query from criteria
            query = self._build_search_query(criteria)
            if not query or len(query.strip()) == 0:
                print("[WARNING] Empty search query, skipping online search")
                return []

            diet = self._map_dietary_restrictions(criteria.get('dietary_restrictions', []))
            intolerances = self._map_intolerances(criteria.get('dietary_restrictions', []))

            # Validate and sanitize parameters
            min_protein = max(0, int(criteria.get('min_protein', 0)))  # Ensure non-negative
            max_calories = max(100, int(criteria.get('max_calories', 99999)))  # Ensure positive and reasonable
            max_ready_time = criteria.get('max_time')
            if max_ready_time and max_ready_time <= 0:
                max_ready_time = None  # Don't pass invalid time

            # Search API
            print(f"[INFO] Searching Spoonacular for '{query}' recipes...")
            api_results = self.spoonacular_api.search_recipes(
                query=query,
                max_results=max_results,
                diet=diet,
                intolerances=intolerances,
                max_ready_time=max_ready_time,
                min_protein=min_protein,
                max_calories=max_calories
            )

            if not api_results:
                print("[INFO] No online recipes found")
                return []

            # Parse each result into meal template format
            parsed_meals = []
            failed_count = 0

            for api_recipe in api_results:
                try:
                    # Get full recipe details (includes full nutrition)
                    recipe_details = self.spoonacular_api.get_recipe_information(api_recipe['id'])

                    if not recipe_details:
                        failed_count += 1
                        continue

                    # Convert to meal template format
                    meal = self.spoonacular_api.parse_recipe_to_template(
                        recipe_details,
                        user_id=criteria.get('user_id', DEFAULT_USER_ID)
                    )

                    # Cross-reference price with shopping history
                    user_id = criteria.get('user_id', DEFAULT_USER_ID)
                    price_estimate = self._estimate_recipe_cost(meal, user_id)

                    # Update meal cost with hybrid estimate
                    meal['cost_estimate_usd'] = price_estimate['estimated_price']

                    # Validate nutrition with USDA
                    ingredients_list = []
                    if 'extendedIngredients' in recipe_details:
                        for ing in recipe_details['extendedIngredients']:
                            ingredients_list.append({
                                'name': ing.get('name', ''),
                                'amount': ing.get('amount', 0),
                                'unit': ing.get('unit', 'g')
                            })

                    validation_report = self._validate_nutrition(meal, ingredients_list)

                    # Add online recipe metadata
                    meal['api_source'] = 'spoonacular'
                    meal['api_recipe_id'] = str(api_recipe['id'])
                    meal['nutrition_validated'] = validation_report['validation_passed']
                    meal['validation_confidence'] = validation_report['validation_confidence']
                    meal['nutrition_flags'] = validation_report.get('flags', [])
                    meal['price_confidence'] = price_estimate['confidence_score']
                    meal['price_source'] = price_estimate['price_source']
                    meal['is_online_recipe'] = True  # Flag for scoring

                    parsed_meals.append(meal)

                except Exception as e:
                    print(f"[WARNING] Failed to parse recipe {api_recipe.get('id')}: {e}")
                    failed_count += 1
                    continue

            if failed_count > 0:
                print(f"[WARNING] {failed_count}/{len(api_results)} recipes failed to parse")

            print(f"[SUCCESS] Parsed {len(parsed_meals)} online recipes")
            return parsed_meals

        except Exception as e:
            print(f"[ERROR] Online recipe search failed: {e}")
            return []  # Graceful degradation

    def _build_search_query(self, criteria: Dict) -> str:
        """Build search query string from meal criteria."""
        meal_time = criteria.get('meal_time', 'dinner')

        # Map meal_time to search terms
        query_map = {
            'breakfast': 'breakfast',
            'lunch': 'lunch main dish',
            'dinner': 'dinner main course',
            'snack': 'snack'
        }

        return query_map.get(meal_time, meal_time)

    def _map_dietary_restrictions(self, restrictions: List[str]) -> Optional[str]:
        """Map user dietary restrictions to Spoonacular diet parameter."""
        if not restrictions:
            return None

        # Spoonacular supported diets
        diet_map = {
            'vegetarian': 'vegetarian',
            'vegan': 'vegan',
            'pescatarian': 'pescatarian',
            'paleo': 'paleo',
            'ketogenic': 'ketogenic',
            'keto': 'ketogenic',
            'gluten-free': 'gluten free'
        }

        # Return first matching diet
        for restriction in restrictions:
            if restriction.lower() in diet_map:
                return diet_map[restriction.lower()]

        return None

    def _map_intolerances(self, restrictions: List[str]) -> Optional[List[str]]:
        """Map dietary restrictions to Spoonacular intolerances."""
        if not restrictions:
            return None

        intolerance_map = {
            'dairy-free': 'dairy',
            'lactose-free': 'dairy',
            'gluten-free': 'gluten',
            'nut-free': 'tree nut',
            'soy-free': 'soy',
            'egg-free': 'egg'
        }

        intolerances = []
        for restriction in restrictions:
            if restriction.lower() in intolerance_map:
                intolerances.append(intolerance_map[restriction.lower()])

        return intolerances if intolerances else None

    def _estimate_recipe_cost(self, recipe: Dict, user_id: int) -> Dict:
        """
        Cross-reference recipe cost with shopping history.

        Returns price estimate with confidence score based on how many
        ingredients we have shopping history for.
        """
        api_price = recipe.get('cost_estimate_usd', 0)

        # Get ingredients from recipe data
        ingredients = recipe.get('ingredients', [])
        if not ingredients:
            # No ingredients to cross-reference
            return {
                'estimated_price': api_price,
                'api_price': api_price,
                'price_difference': 0,
                'confidence_score': 0.3,  # Low confidence, API only
                'price_source': 'spoonacular',
                'ingredients_matched': 0,
                'ingredients_total': 0
            }

        total_ingredients = len(ingredients)
        matched_ingredients = 0
        shopping_history_total = 0

        try:
            # Query shopping history for last 90 days
            query = """
                SELECT item_name, quantity, unit, total_price_usd, purchase_date
                FROM shopping_history
                WHERE user_id = ?
                AND purchase_date >= DATE('now', '-90 days')
                ORDER BY purchase_date DESC
            """
            shopping_items = self.execute_query(query, (user_id,))

            if not shopping_items:
                # No shopping history available
                return {
                    'estimated_price': api_price,
                    'api_price': api_price,
                    'price_difference': 0,
                    'confidence_score': 0.3,
                    'price_source': 'spoonacular',
                    'ingredients_matched': 0,
                    'ingredients_total': total_ingredients
                }

            # Build lookup dictionary for faster matching
            shopping_dict = {}
            for item in shopping_items:
                item_name = item['item_name']
                qty = item['quantity']
                unit = item['unit']
                price = item['total_price_usd']
                date = item['purchase_date']
                key = item_name.lower()
                if key not in shopping_dict:
                    shopping_dict[key] = {
                        'quantity': qty,
                        'unit': unit,
                        'price': price,
                        'date': date
                    }

            # Match ingredients with shopping history
            for ingredient in ingredients:
                ingredient_name = ingredient.get('name', '').lower()
                ingredient_qty = ingredient.get('amount', 0)

                # Try exact match first
                matched = False
                if ingredient_name in shopping_dict:
                    matched = True
                else:
                    # Try fuzzy matching (contains)
                    for shop_item_name in shopping_dict.keys():
                        if ingredient_name in shop_item_name or shop_item_name in ingredient_name:
                            # Found a match
                            matched = True
                            ingredient_name = shop_item_name
                            break

                if matched:
                    matched_ingredients += 1
                    shop_data = shopping_dict[ingredient_name]

                    # Calculate unit price
                    unit_price = shop_data['price'] / shop_data['quantity'] if shop_data['quantity'] > 0 else 0

                    # Estimate cost for this ingredient
                    # (simplified: assumes same units, more sophisticated conversion possible)
                    ingredient_cost = unit_price * ingredient_qty
                    shopping_history_total += ingredient_cost

            # Calculate confidence score
            confidence_score = matched_ingredients / total_ingredients if total_ingredients > 0 else 0

            # Determine final price and source
            if confidence_score > 0:
                # Hybrid approach: 70% shopping history + 30% API
                # Scale shopping history total to full recipe (proportionally)
                if matched_ingredients > 0:
                    shopping_estimate = shopping_history_total * (total_ingredients / matched_ingredients)
                else:
                    shopping_estimate = 0

                estimated_price = (0.7 * shopping_estimate) + (0.3 * api_price)
                price_source = 'hybrid'
            else:
                estimated_price = api_price
                price_source = 'spoonacular'

            price_difference = abs(estimated_price - api_price)

            return {
                'estimated_price': round(estimated_price, 2),
                'api_price': api_price,
                'price_difference': round(price_difference, 2),
                'confidence_score': round(confidence_score, 2),
                'price_source': price_source,
                'ingredients_matched': matched_ingredients,
                'ingredients_total': total_ingredients
            }

        except Exception as e:
            print(f"[WARNING] Price estimation failed: {e}")
            # Fallback to API price
            return {
                'estimated_price': api_price,
                'api_price': api_price,
                'price_difference': 0,
                'confidence_score': 0.3,
                'price_source': 'spoonacular',
                'ingredients_matched': 0,
                'ingredients_total': total_ingredients
            }

    def _convert_to_grams(self, quantity: float, unit: str) -> float:
        """
        Convert quantity from various units to grams.

        Used for nutrition validation with USDA (which reports per 100g).
        """
        unit = unit.lower().strip()

        # Volume to weight conversions (approximate, varies by ingredient)
        conversion_map = {
            'g': 1.0,
            'gram': 1.0,
            'grams': 1.0,
            'kg': 1000.0,
            'kilogram': 1000.0,
            'kilograms': 1000.0,
            'oz': 28.35,
            'ounce': 28.35,
            'ounces': 28.35,
            'lb': 453.59,
            'lbs': 453.59,
            'pound': 453.59,
            'pounds': 453.59,

            # Volume (approximate - assumes water density)
            'ml': 1.0,
            'milliliter': 1.0,
            'milliliters': 1.0,
            'l': 1000.0,
            'liter': 1000.0,
            'liters': 1000.0,
            'cup': 240.0,
            'cups': 240.0,
            'tbsp': 15.0,
            'tablespoon': 15.0,
            'tablespoons': 15.0,
            'tsp': 5.0,
            'teaspoon': 5.0,
            'teaspoons': 5.0,
            'fl oz': 30.0,
            'fluid ounce': 30.0,
            'fluid ounces': 30.0,

            # Common serving sizes (approximations)
            'serving': 100.0,
            'servings': 100.0,
            'piece': 50.0,
            'pieces': 50.0,
            'slice': 30.0,
            'slices': 30.0,
        }

        multiplier = conversion_map.get(unit, 100.0)  # Default 100g if unknown
        return quantity * multiplier

    def _validate_nutrition(self, recipe: Dict, ingredients_list: List[Dict]) -> Dict:
        """
        Cross-validate Spoonacular nutrition with USDA data.

        Compares ingredient-level USDA nutrition totals with recipe-level
        Spoonacular nutrition. Flags discrepancies >10%.
        """
        if not ingredients_list:
            return {
                'validation_passed': False,
                'validation_confidence': 0.0,
                'discrepancies': {},
                'flags': ['No ingredients to validate'],
                'ingredients_validated': 0,
                'ingredients_total': 0
            }

        # Get recipe nutrition from Spoonacular
        recipe_nutrition = {
            'calories': recipe.get('calories', 0),
            'protein_g': recipe.get('protein_g', 0),
            'carbs_g': recipe.get('carbs_g', 0),
            'fat_g': recipe.get('fat_g', 0)
        }

        # Accumulate USDA nutrition totals
        usda_totals = {
            'calories': 0,
            'protein_g': 0,
            'carbs_g': 0,
            'fat_g': 0
        }

        ingredients_validated = 0
        total_ingredients = len(ingredients_list)

        try:
            for ingredient in ingredients_list:
                ingredient_name = ingredient.get('name', '')
                quantity = ingredient.get('amount', 0)
                unit = ingredient.get('unit', 'g')

                if not ingredient_name or quantity == 0:
                    continue

                try:
                    # Get USDA nutrition (per 100g)
                    usda_data = self.usda_api.get_nutrition_from_search(ingredient_name)

                    if not usda_data:
                        continue

                    # Convert ingredient quantity to grams
                    grams = self._convert_to_grams(quantity, unit)

                    # Scale USDA nutrition (from per 100g to actual quantity)
                    scale_factor = grams / 100.0

                    usda_totals['calories'] += usda_data.get('calories', 0) * scale_factor
                    usda_totals['protein_g'] += usda_data.get('protein_g', 0) * scale_factor
                    usda_totals['carbs_g'] += usda_data.get('carbs_g', 0) * scale_factor
                    usda_totals['fat_g'] += usda_data.get('fat_g', 0) * scale_factor

                    ingredients_validated += 1

                except Exception as e:
                    print(f"[WARNING] Failed to validate ingredient '{ingredient_name}': {e}")
                    continue

            # Calculate confidence based on validated ingredients
            validation_confidence = ingredients_validated / total_ingredients if total_ingredients > 0 else 0

            # Compare USDA totals with Spoonacular recipe nutrition
            discrepancies = {}
            flags = []
            validation_passed = True

            for nutrient in ['calories', 'protein_g', 'carbs_g', 'fat_g']:
                usda_value = usda_totals[nutrient]
                spoon_value = recipe_nutrition[nutrient]

                if spoon_value > 0:
                    percent_diff = abs(usda_value - spoon_value) / spoon_value

                    discrepancies[nutrient] = {
                        'usda_value': round(usda_value, 1),
                        'spoonacular_value': round(spoon_value, 1),
                        'percent_difference': round(percent_diff * 100, 1)
                    }

                    # Flag if >10% difference
                    if percent_diff > 0.10:
                        validation_passed = False
                        flags.append(f"{nutrient.replace('_', ' ')} differs by {round(percent_diff * 100, 1)}%")

            # If we validated <50% of ingredients, lower confidence
            if validation_confidence < 0.5:
                flags.append(f"Only {ingredients_validated}/{total_ingredients} ingredients validated")

            return {
                'validation_passed': validation_passed and validation_confidence >= 0.5,
                'validation_confidence': round(validation_confidence, 2),
                'discrepancies': discrepancies,
                'flags': flags,
                'ingredients_validated': ingredients_validated,
                'ingredients_total': total_ingredients
            }

        except Exception as e:
            print(f"[ERROR] Nutrition validation failed: {e}")
            return {
                'validation_passed': False,
                'validation_confidence': 0.0,
                'discrepancies': {},
                'flags': [f'Validation error: {str(e)}'],
                'ingredients_validated': 0,
                'ingredients_total': total_ingredients
            }

    def _score_meal(
        self,
        meal: Dict,
        criteria: Dict,
        remaining: Dict,
        use_inventory: bool,
        user_id: int
    ) -> float:
        """
        Score a meal candidate (0-100).
        Higher score = better recommendation.
        """

        score = 0.0

        # 1. Macro match (40 points max)
        # How well does this meal fit remaining macros?
        target_cals = criteria['target_calories']
        if target_cals > 0:
            calorie_match = 1 - abs(meal['calories'] - target_cals) / target_cals
            score += max(0, calorie_match * 20)

        if remaining['protein_g'] > 0:
            protein_ratio = meal['protein_g'] / remaining['protein_g']
            protein_score = 1 - abs(protein_ratio - 0.25)  # Aim for ~25% of remaining
            score += max(0, protein_score * 20)

        # 2. User preferences (20 points max)
        # Rating history
        if meal.get('rating'):
            score += meal['rating'] * 4

        # Variety (haven't had recently)
        if meal.get('last_made'):
            days_since = (date.today() - date.fromisoformat(meal['last_made'])).days
            variety_score = min(days_since / 30, 1) * 10  # Max 10 points if >30 days
            score += variety_score
        else:
            score += 5  # Never made before gets 5 points

        # 3. Practical constraints (20 points max)
        # Time efficiency
        if meal.get('total_time_minutes'):
            if meal['total_time_minutes'] <= 30:
                score += 10
            elif meal['total_time_minutes'] <= 60:
                score += 5

        # Difficulty match
        skill_map = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
        user_skill = skill_map.get(criteria['difficulty'], 2)
        meal_difficulty = skill_map.get(meal.get('difficulty', 'medium'), 2)

        if meal_difficulty <= user_skill:
            score += 5
        else:
            score -= 5  # Penalize if too difficult

        # Budget
        if criteria.get('budget_limit') and meal.get('cost_estimate_usd'):
            if meal['cost_estimate_usd'] <= criteria['budget_limit']:
                score += 5

        # 4. Inventory match (20 points max)
        if use_inventory:
            inventory_score = self._calculate_inventory_match(meal, user_id)
            score += inventory_score

        # 5. Online recipe adjustment
        if meal.get('is_online_recipe'):
            # Slight penalty for untried recipes (no user rating history)
            score -= 5

            # But bonus if nutrition is validated
            if meal.get('nutrition_validated'):
                score += 3

            # Bonus if price confidence is high
            if meal.get('price_confidence'):
                score += meal['price_confidence'] * 5  # 0-5 point bonus

        return min(score, 100)  # Cap at 100

    def _calculate_inventory_match(self, meal: Dict, user_id: int) -> float:
        """Calculate how well meal ingredients match inventory (0-20 points)."""

        # Get meal ingredients
        ingredients = []
        
        # Check if this is a database meal (has id) or online recipe
        if 'id' in meal:
            # Database meal - query ingredients
            ingredients_query = """
                SELECT ingredient_name FROM meal_ingredients
                WHERE meal_template_id = ?
            """
            ingredients = self.execute_query(ingredients_query, (meal['id'],))
        elif meal.get('is_online_recipe') or meal.get('api_source'):
            # Online recipe - try to get ingredients from meal data
            # Online recipes might have ingredients in a different format
            # For now, return 0 (no inventory match) since we don't have ingredient data
            return 0
        else:
            # Unknown meal type, return 0
            return 0

        if not ingredients:
            return 0

        # Get inventory items
        inventory = self.inventory_manager.get_all_items(user_id)
        inventory_items = {item['item_name'].lower() for item in inventory}

        # Calculate match
        matches = 0
        for ingredient in ingredients:
            ing_name = ingredient['ingredient_name'].lower()

            # Check for exact match or partial match
            if ing_name in inventory_items:
                matches += 1
            elif any(ing_name in inv_item or inv_item in ing_name for inv_item in inventory_items):
                matches += 0.5

        match_ratio = matches / len(ingredients) if ingredients else 0
        return match_ratio * 20

    def _explain_recommendation(self, meal: Dict, criteria: Dict, remaining: Dict) -> List[str]:
        """Generate human-readable reasons for recommendation."""

        reasons = []

        # Macro fit
        calorie_match = abs(meal['calories'] - criteria['target_calories']) / criteria['target_calories'] if criteria['target_calories'] > 0 else 0
        if calorie_match < 0.2:
            reasons.append(f"Great calorie match ({meal['calories']} kcal)")

        if meal['protein_g'] >= criteria['min_protein']:
            reasons.append(f"Good protein ({meal['protein_g']:.0f}g)")

        # User history
        if meal.get('rating') and meal['rating'] >= 4:
            reasons.append(f"Highly rated ({meal['rating']}/5)")

        # Practical
        if meal.get('total_time_minutes') and meal['total_time_minutes'] <= 30:
            reasons.append("Quick to make")

        if meal.get('difficulty') == 'easy':
            reasons.append("Easy recipe")

        if meal.get('is_batch_friendly'):
            reasons.append("Batch-friendly")

        # Tags
        if meal.get('tags'):
            tags = json.loads(meal['tags'])
            if 'budget' in tags:
                reasons.append("Budget-friendly")
            if 'healthy' in tags:
                reasons.append("Healthy option")

        # Online recipe indicators
        if meal.get('is_online_recipe'):
            reasons.append("New recipe from online search")

            if meal.get('nutrition_validated'):
                reasons.append("Nutrition verified with USDA")

            if meal.get('price_confidence', 0) > 0.7:
                reasons.append("Price estimated from shopping history")

        return reasons

    def get_quick_suggestions(
        self,
        user_id: int = DEFAULT_USER_ID,
        target_date: date = None
    ) -> Dict:
        """Get quick meal suggestions for all remaining meals today."""

        if not target_date:
            target_date = date.today()

        progress = self.meal_tracker.get_daily_progress(user_id, target_date)

        # Determine what meals are left
        meals_logged = {meal['meal_time'] for meal in progress['meals']}
        all_meals = ['breakfast', 'lunch', 'dinner', 'snack']
        remaining_meals = [m for m in all_meals if m not in meals_logged]

        suggestions = {}
        for meal_time in remaining_meals:
            recommendations = self.recommend_meal(
                meal_time=meal_time,
                user_id=user_id,
                target_date=target_date
            )
            if recommendations:
                suggestions[meal_time] = recommendations[0]  # Top recommendation

        return suggestions


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Meal Recommender")
    parser.add_argument('--recommend', type=str, choices=['breakfast', 'lunch', 'dinner', 'snack'],
                       help='Get meal recommendations for specific meal time')
    parser.add_argument('--quick', action='store_true', help='Get quick suggestions for all remaining meals')
    parser.add_argument('--max-time', type=int, help='Maximum cooking time (minutes)')
    parser.add_argument('--budget', type=float, help='Maximum cost per meal')
    parser.add_argument('--count', type=int, default=5, help='Number of recommendations (default: 5)')

    args = parser.parse_args()

    recommender = MealRecommender()

    if args.recommend:
        print(f"\nFinding {args.recommend} recommendations...")
        print("=" * 80)

        recommendations = recommender.recommend_meal(
            meal_time=args.recommend,
            max_time=args.max_time,
            budget_limit=args.budget
        )

        if recommendations:
            for i, rec in enumerate(recommendations[:args.count], 1):
                print(f"\n{i}. {rec['name']} (Score: {rec['recommendation_score']}/100)")
                print(f"   {rec['calories']} kcal | P: {rec['protein_g']}g | C: {rec['carbs_g']}g | F: {rec['fat_g']}g")

                if rec.get('total_time_minutes'):
                    print(f"   Time: {rec['total_time_minutes']} min", end='')
                    if rec.get('difficulty'):
                        print(f" | Difficulty: {rec['difficulty']}", end='')
                    print()

                if rec.get('cost_estimate_usd'):
                    print(f"   Cost: ${rec['cost_estimate_usd']:.2f}/serving")

                if rec['match_reasons']:
                    print(f"   Why: {', '.join(rec['match_reasons'])}")

    elif args.quick:
        print("\nQuick suggestions for remaining meals...")
        print("=" * 80)

        suggestions = recommender.get_quick_suggestions()

        if suggestions:
            for meal_time, suggestion in suggestions.items():
                print(f"\n{meal_time.upper()}: {suggestion['name']}")
                print(f"  {suggestion['calories']} kcal | P: {suggestion['protein_g']}g | C: {suggestion['carbs_g']}g | F: {suggestion['fat_g']}g")
                if suggestion.get('match_reasons'):
                    print(f"  {', '.join(suggestion['match_reasons'])}")
        else:
            print("All meals logged for today!")

    else:
        parser.print_help()
