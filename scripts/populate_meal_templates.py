"""
Populate database with comprehensive meal templates and ingredients.
Creates a diverse library of budget-friendly, nutritious meals.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from scripts.db_manager import DatabaseManager
from config.config import DEFAULT_USER_ID


class MealLibraryPopulator(DatabaseManager):
    """Populate meal template library."""

    def __init__(self):
        super().__init__()

    def add_meal_with_ingredients(self, meal_data: dict, ingredients: list):
        """Add a meal template with its ingredients."""

        # Insert meal template
        meal_query = """
            INSERT INTO meal_templates (
                user_id, name, meal_type, servings, calories,
                protein_g, carbs_g, fat_g, fiber_g,
                total_time_minutes, prep_time_minutes, cook_time_minutes,
                difficulty, cost_estimate_usd, is_batch_friendly,
                recipe_instructions, tags, recipe_source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        meal_id = self.execute_write(meal_query, (
            meal_data['user_id'],
            meal_data['name'],
            meal_data['meal_type'],
            meal_data['servings'],
            meal_data['calories'],
            meal_data['protein_g'],
            meal_data['carbs_g'],
            meal_data['fat_g'],
            meal_data.get('fiber_g'),
            meal_data.get('total_time_minutes'),
            meal_data.get('prep_time_minutes'),
            meal_data.get('cook_time_minutes'),
            meal_data.get('difficulty', 'easy'),
            meal_data.get('cost_estimate_usd'),
            meal_data.get('is_batch_friendly', 0),
            meal_data.get('recipe_instructions'),
            meal_data.get('tags'),
            meal_data.get('recipe_source')
        ))

        # Insert ingredients
        ing_query = """
            INSERT INTO meal_ingredients (
                meal_template_id, ingredient_name, quantity, unit, optional
            ) VALUES (?, ?, ?, ?, ?)
        """

        ing_data = [(meal_id, ing['name'], ing['quantity'], ing['unit'], ing.get('optional', 0))
                    for ing in ingredients]

        self.execute_many(ing_query, ing_data)

        return meal_id

    def populate_breakfast_meals(self, user_id: int = DEFAULT_USER_ID):
        """Add breakfast meal templates."""

        breakfasts = [
            {
                'meal': {
                    'user_id': user_id,
                    'name': 'Protein Oatmeal',
                    'meal_type': 'breakfast',
                    'servings': 1,
                    'calories': 380,
                    'protein_g': 30,
                    'carbs_g': 48,
                    'fat_g': 8,
                    'fiber_g': 8,
                    'total_time_minutes': 10,
                    'prep_time_minutes': 5,
                    'cook_time_minutes': 5,
                    'difficulty': 'easy',
                    'cost_estimate_usd': 1.50,
                    'is_batch_friendly': 0,
                    'recipe_instructions': '1. Cook oats with water/milk. 2. Stir in protein powder. 3. Top with berries.',
                    'tags': '["budget", "quick", "high-protein"]',
                    'recipe_source': 'custom'
                },
                'ingredients': [
                    {'name': 'oats', 'quantity': 0.5, 'unit': 'cup'},
                    {'name': 'protein powder', 'quantity': 1, 'unit': 'scoop'},
                    {'name': 'berries', 'quantity': 0.5, 'unit': 'cup'},
                    {'name': 'milk', 'quantity': 1, 'unit': 'cup'}
                ]
            },
            {
                'meal': {
                    'user_id': user_id,
                    'name': 'Scrambled Eggs & Toast',
                    'meal_type': 'breakfast',
                    'servings': 1,
                    'calories': 420,
                    'protein_g': 28,
                    'carbs_g': 35,
                    'fat_g': 18,
                    'fiber_g': 5,
                    'total_time_minutes': 10,
                    'prep_time_minutes': 3,
                    'cook_time_minutes': 7,
                    'difficulty': 'easy',
                    'cost_estimate_usd': 1.20,
                    'is_batch_friendly': 0,
                    'recipe_instructions': '1. Scramble 3 eggs in pan. 2. Toast whole wheat bread. 3. Serve together.',
                    'tags': '["quick", "high-protein", "budget"]',
                    'recipe_source': 'custom'
                },
                'ingredients': [
                    {'name': 'eggs', 'quantity': 3, 'unit': 'whole'},
                    {'name': 'whole wheat bread', 'quantity': 2, 'unit': 'slices'},
                    {'name': 'butter', 'quantity': 1, 'unit': 'tbsp'}
                ]
            },
            {
                'meal': {
                    'user_id': user_id,
                    'name': 'Greek Yogurt Bowl',
                    'meal_type': 'breakfast',
                    'servings': 1,
                    'calories': 340,
                    'protein_g': 25,
                    'carbs_g': 42,
                    'fat_g': 8,
                    'fiber_g': 6,
                    'total_time_minutes': 5,
                    'prep_time_minutes': 5,
                    'cook_time_minutes': 0,
                    'difficulty': 'easy',
                    'cost_estimate_usd': 2.00,
                    'is_batch_friendly': 0,
                    'recipe_instructions': '1. Add yogurt to bowl. 2. Top with granola, berries, and honey.',
                    'tags': '["quick", "no-cook", "high-protein"]',
                    'recipe_source': 'custom'
                },
                'ingredients': [
                    {'name': 'greek yogurt', 'quantity': 1, 'unit': 'cup'},
                    {'name': 'granola', 'quantity': 0.25, 'unit': 'cup'},
                    {'name': 'berries', 'quantity': 0.5, 'unit': 'cup'},
                    {'name': 'honey', 'quantity': 1, 'unit': 'tbsp'}
                ]
            },
            {
                'meal': {
                    'user_id': user_id,
                    'name': 'Breakfast Burrito',
                    'meal_type': 'breakfast',
                    'servings': 1,
                    'calories': 480,
                    'protein_g': 32,
                    'carbs_g': 45,
                    'fat_g': 18,
                    'fiber_g': 8,
                    'total_time_minutes': 15,
                    'prep_time_minutes': 5,
                    'cook_time_minutes': 10,
                    'difficulty': 'easy',
                    'cost_estimate_usd': 2.50,
                    'is_batch_friendly': 1,
                    'recipe_instructions': '1. Scramble eggs with black beans. 2. Add to tortilla with cheese. 3. Wrap and heat.',
                    'tags': '["high-protein", "batch-friendly"]',
                    'recipe_source': 'custom'
                },
                'ingredients': [
                    {'name': 'eggs', 'quantity': 2, 'unit': 'whole'},
                    {'name': 'black beans', 'quantity': 0.5, 'unit': 'cup'},
                    {'name': 'tortilla', 'quantity': 1, 'unit': 'large'},
                    {'name': 'cheese', 'quantity': 0.25, 'unit': 'cup'},
                    {'name': 'salsa', 'quantity': 2, 'unit': 'tbsp', 'optional': 1}
                ]
            },
            {
                'meal': {
                    'user_id': user_id,
                    'name': 'Protein Pancakes',
                    'meal_type': 'breakfast',
                    'servings': 1,
                    'calories': 400,
                    'protein_g': 35,
                    'carbs_g': 40,
                    'fat_g': 10,
                    'fiber_g': 4,
                    'total_time_minutes': 15,
                    'prep_time_minutes': 5,
                    'cook_time_minutes': 10,
                    'difficulty': 'easy',
                    'cost_estimate_usd': 1.80,
                    'is_batch_friendly': 1,
                    'recipe_instructions': '1. Mix oats, eggs, protein powder. 2. Cook on griddle. 3. Serve with syrup.',
                    'tags': '["high-protein", "batch-friendly"]',
                    'recipe_source': 'custom'
                },
                'ingredients': [
                    {'name': 'oats', 'quantity': 0.5, 'unit': 'cup'},
                    {'name': 'eggs', 'quantity': 2, 'unit': 'whole'},
                    {'name': 'protein powder', 'quantity': 1, 'unit': 'scoop'},
                    {'name': 'banana', 'quantity': 1, 'unit': 'whole'},
                    {'name': 'maple syrup', 'quantity': 1, 'unit': 'tbsp'}
                ]
            },
            {
                'meal': {
                    'user_id': user_id,
                    'name': 'Egg White Omelet',
                    'meal_type': 'breakfast',
                    'servings': 1,
                    'calories': 280,
                    'protein_g': 32,
                    'carbs_g': 18,
                    'fat_g': 8,
                    'fiber_g': 3,
                    'total_time_minutes': 12,
                    'prep_time_minutes': 5,
                    'cook_time_minutes': 7,
                    'difficulty': 'easy',
                    'cost_estimate_usd': 2.20,
                    'is_batch_friendly': 0,
                    'recipe_instructions': '1. Whisk egg whites. 2. Cook with veggies. 3. Fold and serve.',
                    'tags': '["high-protein", "low-fat", "healthy"]',
                    'recipe_source': 'custom'
                },
                'ingredients': [
                    {'name': 'egg whites', 'quantity': 1, 'unit': 'cup'},
                    {'name': 'spinach', 'quantity': 1, 'unit': 'cup'},
                    {'name': 'tomato', 'quantity': 0.5, 'unit': 'cup'},
                    {'name': 'cheese', 'quantity': 2, 'unit': 'tbsp'}
                ]
            },
            {
                'meal': {
                    'user_id': user_id,
                    'name': 'Peanut Butter Banana Smoothie',
                    'meal_type': 'breakfast',
                    'servings': 1,
                    'calories': 420,
                    'protein_g': 28,
                    'carbs_g': 52,
                    'fat_g': 12,
                    'fiber_g': 6,
                    'total_time_minutes': 5,
                    'prep_time_minutes': 5,
                    'cook_time_minutes': 0,
                    'difficulty': 'easy',
                    'cost_estimate_usd': 1.60,
                    'is_batch_friendly': 0,
                    'recipe_instructions': '1. Blend all ingredients until smooth. 2. Serve immediately.',
                    'tags': '["quick", "no-cook", "high-protein"]',
                    'recipe_source': 'custom'
                },
                'ingredients': [
                    {'name': 'banana', 'quantity': 1, 'unit': 'whole'},
                    {'name': 'peanut butter', 'quantity': 2, 'unit': 'tbsp'},
                    {'name': 'protein powder', 'quantity': 1, 'unit': 'scoop'},
                    {'name': 'milk', 'quantity': 1, 'unit': 'cup'}
                ]
            }
        ]

        count = 0
        for item in breakfasts:
            self.add_meal_with_ingredients(item['meal'], item['ingredients'])
            count += 1
            print(f"[INFO] Added: {item['meal']['name']}")

        print(f"[SUCCESS] Added {count} breakfast meals")
        return count

    def populate_lunch_meals(self, user_id: int = DEFAULT_USER_ID):
        """Add lunch meal templates."""

        lunches = [
            {
                'meal': {
                    'user_id': user_id,
                    'name': 'Chicken & Rice Bowl',
                    'meal_type': 'lunch',
                    'servings': 1,
                    'calories': 520,
                    'protein_g': 45,
                    'carbs_g': 55,
                    'fat_g': 12,
                    'fiber_g': 4,
                    'total_time_minutes': 25,
                    'prep_time_minutes': 10,
                    'cook_time_minutes': 15,
                    'difficulty': 'easy',
                    'cost_estimate_usd': 3.50,
                    'is_batch_friendly': 1,
                    'recipe_instructions': '1. Cook rice. 2. Grill chicken breast. 3. Serve with steamed broccoli.',
                    'tags': '["high-protein", "batch-friendly", "meal-prep"]',
                    'recipe_source': 'custom'
                },
                'ingredients': [
                    {'name': 'chicken breast', 'quantity': 6, 'unit': 'oz'},
                    {'name': 'rice', 'quantity': 0.75, 'unit': 'cup'},
                    {'name': 'broccoli', 'quantity': 1, 'unit': 'cup'},
                    {'name': 'olive oil', 'quantity': 1, 'unit': 'tbsp'}
                ]
            },
            {
                'meal': {
                    'user_id': user_id,
                    'name': 'Turkey Sandwich',
                    'meal_type': 'lunch',
                    'servings': 1,
                    'calories': 450,
                    'protein_g': 38,
                    'carbs_g': 48,
                    'fat_g': 12,
                    'fiber_g': 8,
                    'total_time_minutes': 5,
                    'prep_time_minutes': 5,
                    'cook_time_minutes': 0,
                    'difficulty': 'easy',
                    'cost_estimate_usd': 2.80,
                    'is_batch_friendly': 0,
                    'recipe_instructions': '1. Layer turkey, cheese, lettuce, tomato on whole wheat bread. 2. Add mustard.',
                    'tags': '["quick", "no-cook", "high-protein"]',
                    'recipe_source': 'custom'
                },
                'ingredients': [
                    {'name': 'turkey breast', 'quantity': 4, 'unit': 'oz'},
                    {'name': 'whole wheat bread', 'quantity': 2, 'unit': 'slices'},
                    {'name': 'cheese', 'quantity': 1, 'unit': 'slice'},
                    {'name': 'lettuce', 'quantity': 2, 'unit': 'leaves'},
                    {'name': 'tomato', 'quantity': 2, 'unit': 'slices'},
                    {'name': 'mustard', 'quantity': 1, 'unit': 'tbsp'}
                ]
            },
            {
                'meal': {
                    'user_id': user_id,
                    'name': 'Tuna Salad',
                    'meal_type': 'lunch',
                    'servings': 1,
                    'calories': 380,
                    'protein_g': 42,
                    'carbs_g': 28,
                    'fat_g': 10,
                    'fiber_g': 8,
                    'total_time_minutes': 10,
                    'prep_time_minutes': 10,
                    'cook_time_minutes': 0,
                    'difficulty': 'easy',
                    'cost_estimate_usd': 2.50,
                    'is_batch_friendly': 0,
                    'recipe_instructions': '1. Mix tuna with Greek yogurt. 2. Serve over mixed greens with crackers.',
                    'tags': '["quick", "no-cook", "high-protein", "healthy"]',
                    'recipe_source': 'custom'
                },
                'ingredients': [
                    {'name': 'canned tuna', 'quantity': 1, 'unit': 'can'},
                    {'name': 'greek yogurt', 'quantity': 2, 'unit': 'tbsp'},
                    {'name': 'mixed greens', 'quantity': 2, 'unit': 'cups'},
                    {'name': 'whole wheat crackers', 'quantity': 10, 'unit': 'crackers'}
                ]
            },
            {
                'meal': {
                    'user_id': user_id,
                    'name': 'Chicken Quesadilla',
                    'meal_type': 'lunch',
                    'servings': 1,
                    'calories': 550,
                    'protein_g': 40,
                    'carbs_g': 50,
                    'fat_g': 20,
                    'fiber_g': 6,
                    'total_time_minutes': 15,
                    'prep_time_minutes': 5,
                    'cook_time_minutes': 10,
                    'difficulty': 'easy',
                    'cost_estimate_usd': 3.00,
                    'is_batch_friendly': 1,
                    'recipe_instructions': '1. Fill tortilla with chicken and cheese. 2. Cook in pan until crispy. 3. Cut and serve.',
                    'tags': '["high-protein", "quick"]',
                    'recipe_source': 'custom'
                },
                'ingredients': [
                    {'name': 'chicken breast', 'quantity': 4, 'unit': 'oz'},
                    {'name': 'tortilla', 'quantity': 2, 'unit': 'large'},
                    {'name': 'cheese', 'quantity': 0.5, 'unit': 'cup'},
                    {'name': 'salsa', 'quantity': 0.25, 'unit': 'cup', 'optional': 1}
                ]
            },
            {
                'meal': {
                    'user_id': user_id,
                    'name': 'Beef & Veggie Stir Fry',
                    'meal_type': 'lunch',
                    'servings': 1,
                    'calories': 480,
                    'protein_g': 38,
                    'carbs_g': 45,
                    'fat_g': 15,
                    'fiber_g': 6,
                    'total_time_minutes': 20,
                    'prep_time_minutes': 10,
                    'cook_time_minutes': 10,
                    'difficulty': 'medium',
                    'cost_estimate_usd': 4.00,
                    'is_batch_friendly': 1,
                    'recipe_instructions': '1. Stir fry beef and vegetables. 2. Serve over rice. 3. Add soy sauce.',
                    'tags': '["high-protein", "batch-friendly"]',
                    'recipe_source': 'custom'
                },
                'ingredients': [
                    {'name': 'beef sirloin', 'quantity': 5, 'unit': 'oz'},
                    {'name': 'mixed vegetables', 'quantity': 2, 'unit': 'cups'},
                    {'name': 'rice', 'quantity': 0.5, 'unit': 'cup'},
                    {'name': 'soy sauce', 'quantity': 2, 'unit': 'tbsp'},
                    {'name': 'sesame oil', 'quantity': 1, 'unit': 'tsp'}
                ]
            },
            {
                'meal': {
                    'user_id': user_id,
                    'name': 'Pasta Salad with Chicken',
                    'meal_type': 'lunch',
                    'servings': 1,
                    'calories': 500,
                    'protein_g': 35,
                    'carbs_g': 58,
                    'fat_g': 14,
                    'fiber_g': 7,
                    'total_time_minutes': 20,
                    'prep_time_minutes': 10,
                    'cook_time_minutes': 10,
                    'difficulty': 'easy',
                    'cost_estimate_usd': 3.20,
                    'is_batch_friendly': 1,
                    'recipe_instructions': '1. Cook pasta. 2. Mix with grilled chicken, vegetables, Italian dressing.',
                    'tags': '["batch-friendly", "meal-prep"]',
                    'recipe_source': 'custom'
                },
                'ingredients': [
                    {'name': 'pasta', 'quantity': 1.5, 'unit': 'cups'},
                    {'name': 'chicken breast', 'quantity': 4, 'unit': 'oz'},
                    {'name': 'cherry tomatoes', 'quantity': 0.5, 'unit': 'cup'},
                    {'name': 'cucumber', 'quantity': 0.5, 'unit': 'cup'},
                    {'name': 'italian dressing', 'quantity': 2, 'unit': 'tbsp'}
                ]
            },
            {
                'meal': {
                    'user_id': user_id,
                    'name': 'Protein Bowl',
                    'meal_type': 'lunch',
                    'servings': 1,
                    'calories': 560,
                    'protein_g': 48,
                    'carbs_g': 52,
                    'fat_g': 16,
                    'fiber_g': 10,
                    'total_time_minutes': 25,
                    'prep_time_minutes': 10,
                    'cook_time_minutes': 15,
                    'difficulty': 'easy',
                    'cost_estimate_usd': 4.50,
                    'is_batch_friendly': 1,
                    'recipe_instructions': '1. Layer quinoa, grilled chicken, roasted veggies. 2. Top with avocado and tahini.',
                    'tags': '["high-protein", "healthy", "batch-friendly"]',
                    'recipe_source': 'custom'
                },
                'ingredients': [
                    {'name': 'quinoa', 'quantity': 0.75, 'unit': 'cup'},
                    {'name': 'chicken breast', 'quantity': 5, 'unit': 'oz'},
                    {'name': 'sweet potato', 'quantity': 0.5, 'unit': 'cup'},
                    {'name': 'broccoli', 'quantity': 1, 'unit': 'cup'},
                    {'name': 'avocado', 'quantity': 0.25, 'unit': 'whole'}
                ]
            }
        ]

        count = 0
        for item in lunches:
            self.add_meal_with_ingredients(item['meal'], item['ingredients'])
            count += 1
            print(f"[INFO] Added: {item['meal']['name']}")

        print(f"[SUCCESS] Added {count} lunch meals")
        return count

    def populate_dinner_meals(self, user_id: int = DEFAULT_USER_ID):
        """Add dinner meal templates."""

        dinners = [
            {
                'meal': {
                    'user_id': user_id,
                    'name': 'Grilled Salmon & Vegetables',
                    'meal_type': 'dinner',
                    'servings': 1,
                    'calories': 580,
                    'protein_g': 48,
                    'carbs_g': 42,
                    'fat_g': 22,
                    'fiber_g': 8,
                    'total_time_minutes': 30,
                    'prep_time_minutes': 10,
                    'cook_time_minutes': 20,
                    'difficulty': 'medium',
                    'cost_estimate_usd': 6.50,
                    'is_batch_friendly': 1,
                    'recipe_instructions': '1. Season and grill salmon. 2. Roast vegetables. 3. Serve with quinoa.',
                    'tags': '["high-protein", "healthy", "omega3"]',
                    'recipe_source': 'custom'
                },
                'ingredients': [
                    {'name': 'salmon fillet', 'quantity': 6, 'unit': 'oz'},
                    {'name': 'quinoa', 'quantity': 0.5, 'unit': 'cup'},
                    {'name': 'asparagus', 'quantity': 1, 'unit': 'cup'},
                    {'name': 'bell pepper', 'quantity': 0.5, 'unit': 'cup'},
                    {'name': 'olive oil', 'quantity': 1, 'unit': 'tbsp'}
                ]
            },
            {
                'meal': {
                    'user_id': user_id,
                    'name': 'Spaghetti & Meatballs',
                    'meal_type': 'dinner',
                    'servings': 1,
                    'calories': 620,
                    'protein_g': 42,
                    'carbs_g': 68,
                    'fat_g': 18,
                    'fiber_g': 8,
                    'total_time_minutes': 35,
                    'prep_time_minutes': 15,
                    'cook_time_minutes': 20,
                    'difficulty': 'medium',
                    'cost_estimate_usd': 3.80,
                    'is_batch_friendly': 1,
                    'recipe_instructions': '1. Cook pasta. 2. Make meatballs and brown. 3. Simmer in marinara. 4. Combine.',
                    'tags': '["batch-friendly", "comfort-food"]',
                    'recipe_source': 'custom'
                },
                'ingredients': [
                    {'name': 'ground beef', 'quantity': 5, 'unit': 'oz'},
                    {'name': 'spaghetti', 'quantity': 2, 'unit': 'oz'},
                    {'name': 'marinara sauce', 'quantity': 1, 'unit': 'cup'},
                    {'name': 'parmesan cheese', 'quantity': 2, 'unit': 'tbsp'}
                ]
            },
            {
                'meal': {
                    'user_id': user_id,
                    'name': 'Chicken Fajitas',
                    'meal_type': 'dinner',
                    'servings': 1,
                    'calories': 540,
                    'protein_g': 45,
                    'carbs_g': 52,
                    'fat_g': 16,
                    'fiber_g': 10,
                    'total_time_minutes': 25,
                    'prep_time_minutes': 10,
                    'cook_time_minutes': 15,
                    'difficulty': 'easy',
                    'cost_estimate_usd': 4.20,
                    'is_batch_friendly': 1,
                    'recipe_instructions': '1. Slice and cook chicken with peppers and onions. 2. Serve in tortillas.',
                    'tags': '["high-protein", "batch-friendly"]',
                    'recipe_source': 'custom'
                },
                'ingredients': [
                    {'name': 'chicken breast', 'quantity': 6, 'unit': 'oz'},
                    {'name': 'bell peppers', 'quantity': 1, 'unit': 'cup'},
                    {'name': 'onion', 'quantity': 0.5, 'unit': 'cup'},
                    {'name': 'tortilla', 'quantity': 2, 'unit': 'medium'},
                    {'name': 'fajita seasoning', 'quantity': 1, 'unit': 'tbsp'}
                ]
            },
            {
                'meal': {
                    'user_id': user_id,
                    'name': 'Turkey Chili',
                    'meal_type': 'dinner',
                    'servings': 1,
                    'calories': 480,
                    'protein_g': 42,
                    'carbs_g': 48,
                    'fat_g': 12,
                    'fiber_g': 14,
                    'total_time_minutes': 40,
                    'prep_time_minutes': 10,
                    'cook_time_minutes': 30,
                    'difficulty': 'easy',
                    'cost_estimate_usd': 3.50,
                    'is_batch_friendly': 1,
                    'recipe_instructions': '1. Brown ground turkey. 2. Add beans, tomatoes, spices. 3. Simmer 30 min.',
                    'tags': '["high-protein", "batch-friendly", "budget", "healthy"]',
                    'recipe_source': 'custom'
                },
                'ingredients': [
                    {'name': 'ground turkey', 'quantity': 6, 'unit': 'oz'},
                    {'name': 'kidney beans', 'quantity': 1, 'unit': 'cup'},
                    {'name': 'diced tomatoes', 'quantity': 1, 'unit': 'cup'},
                    {'name': 'onion', 'quantity': 0.5, 'unit': 'cup'},
                    {'name': 'chili powder', 'quantity': 1, 'unit': 'tbsp'}
                ]
            },
            {
                'meal': {
                    'user_id': user_id,
                    'name': 'Pork Chop with Sweet Potato',
                    'meal_type': 'dinner',
                    'servings': 1,
                    'calories': 560,
                    'protein_g': 46,
                    'carbs_g': 52,
                    'fat_g': 16,
                    'fiber_g': 8,
                    'total_time_minutes': 35,
                    'prep_time_minutes': 10,
                    'cook_time_minutes': 25,
                    'difficulty': 'medium',
                    'cost_estimate_usd': 5.00,
                    'is_batch_friendly': 1,
                    'recipe_instructions': '1. Season and pan-sear pork chop. 2. Roast sweet potato and green beans.',
                    'tags': '["high-protein", "batch-friendly"]',
                    'recipe_source': 'custom'
                },
                'ingredients': [
                    {'name': 'pork chop', 'quantity': 6, 'unit': 'oz'},
                    {'name': 'sweet potato', 'quantity': 1, 'unit': 'medium'},
                    {'name': 'green beans', 'quantity': 1.5, 'unit': 'cups'},
                    {'name': 'olive oil', 'quantity': 1, 'unit': 'tbsp'}
                ]
            },
            {
                'meal': {
                    'user_id': user_id,
                    'name': 'Shrimp Stir Fry',
                    'meal_type': 'dinner',
                    'servings': 1,
                    'calories': 420,
                    'protein_g': 38,
                    'carbs_g': 48,
                    'fat_g': 10,
                    'fiber_g': 6,
                    'total_time_minutes': 20,
                    'prep_time_minutes': 10,
                    'cook_time_minutes': 10,
                    'difficulty': 'easy',
                    'cost_estimate_usd': 5.50,
                    'is_batch_friendly': 1,
                    'recipe_instructions': '1. Stir fry shrimp and vegetables. 2. Serve over rice with teriyaki sauce.',
                    'tags': '["high-protein", "quick", "healthy"]',
                    'recipe_source': 'custom'
                },
                'ingredients': [
                    {'name': 'shrimp', 'quantity': 6, 'unit': 'oz'},
                    {'name': 'mixed vegetables', 'quantity': 2, 'unit': 'cups'},
                    {'name': 'rice', 'quantity': 0.75, 'unit': 'cup'},
                    {'name': 'teriyaki sauce', 'quantity': 2, 'unit': 'tbsp'}
                ]
            },
            {
                'meal': {
                    'user_id': user_id,
                    'name': 'Beef Tacos',
                    'meal_type': 'dinner',
                    'servings': 1,
                    'calories': 580,
                    'protein_g': 40,
                    'carbs_g': 45,
                    'fat_g': 24,
                    'fiber_g': 8,
                    'total_time_minutes': 20,
                    'prep_time_minutes': 5,
                    'cook_time_minutes': 15,
                    'difficulty': 'easy',
                    'cost_estimate_usd': 4.00,
                    'is_batch_friendly': 1,
                    'recipe_instructions': '1. Cook ground beef with taco seasoning. 2. Serve in shells with toppings.',
                    'tags': '["quick", "batch-friendly"]',
                    'recipe_source': 'custom'
                },
                'ingredients': [
                    {'name': 'ground beef', 'quantity': 5, 'unit': 'oz'},
                    {'name': 'taco shells', 'quantity': 3, 'unit': 'shells'},
                    {'name': 'lettuce', 'quantity': 1, 'unit': 'cup'},
                    {'name': 'cheese', 'quantity': 0.25, 'unit': 'cup'},
                    {'name': 'salsa', 'quantity': 0.25, 'unit': 'cup'}
                ]
            }
        ]

        count = 0
        for item in dinners:
            self.add_meal_with_ingredients(item['meal'], item['ingredients'])
            count += 1
            print(f"[INFO] Added: {item['meal']['name']}")

        print(f"[SUCCESS] Added {count} dinner meals")
        return count

    def populate_snack_meals(self, user_id: int = DEFAULT_USER_ID):
        """Add snack meal templates."""

        snacks = [
            {
                'meal': {
                    'user_id': user_id,
                    'name': 'Protein Shake',
                    'meal_type': 'snack',
                    'servings': 1,
                    'calories': 180,
                    'protein_g': 25,
                    'carbs_g': 12,
                    'fat_g': 4,
                    'fiber_g': 1,
                    'total_time_minutes': 3,
                    'prep_time_minutes': 3,
                    'cook_time_minutes': 0,
                    'difficulty': 'easy',
                    'cost_estimate_usd': 1.20,
                    'is_batch_friendly': 0,
                    'recipe_instructions': '1. Mix protein powder with water or milk. 2. Shake and drink.',
                    'tags': '["quick", "high-protein", "post-workout"]',
                    'recipe_source': 'custom'
                },
                'ingredients': [
                    {'name': 'protein powder', 'quantity': 1, 'unit': 'scoop'},
                    {'name': 'water', 'quantity': 1, 'unit': 'cup'}
                ]
            },
            {
                'meal': {
                    'user_id': user_id,
                    'name': 'Apple with Peanut Butter',
                    'meal_type': 'snack',
                    'servings': 1,
                    'calories': 240,
                    'protein_g': 8,
                    'carbs_g': 32,
                    'fat_g': 10,
                    'fiber_g': 6,
                    'total_time_minutes': 2,
                    'prep_time_minutes': 2,
                    'cook_time_minutes': 0,
                    'difficulty': 'easy',
                    'cost_estimate_usd': 0.80,
                    'is_batch_friendly': 0,
                    'recipe_instructions': '1. Slice apple. 2. Serve with peanut butter for dipping.',
                    'tags': '["quick", "budget", "healthy"]',
                    'recipe_source': 'custom'
                },
                'ingredients': [
                    {'name': 'apple', 'quantity': 1, 'unit': 'medium'},
                    {'name': 'peanut butter', 'quantity': 2, 'unit': 'tbsp'}
                ]
            },
            {
                'meal': {
                    'user_id': user_id,
                    'name': 'Cottage Cheese & Berries',
                    'meal_type': 'snack',
                    'servings': 1,
                    'calories': 200,
                    'protein_g': 18,
                    'carbs_g': 22,
                    'fat_g': 4,
                    'fiber_g': 3,
                    'total_time_minutes': 2,
                    'prep_time_minutes': 2,
                    'cook_time_minutes': 0,
                    'difficulty': 'easy',
                    'cost_estimate_usd': 1.50,
                    'is_batch_friendly': 0,
                    'recipe_instructions': '1. Top cottage cheese with berries.',
                    'tags': '["quick", "high-protein", "healthy"]',
                    'recipe_source': 'custom'
                },
                'ingredients': [
                    {'name': 'cottage cheese', 'quantity': 1, 'unit': 'cup'},
                    {'name': 'berries', 'quantity': 0.5, 'unit': 'cup'}
                ]
            },
            {
                'meal': {
                    'user_id': user_id,
                    'name': 'Trail Mix',
                    'meal_type': 'snack',
                    'servings': 1,
                    'calories': 280,
                    'protein_g': 8,
                    'carbs_g': 28,
                    'fat_g': 16,
                    'fiber_g': 4,
                    'total_time_minutes': 1,
                    'prep_time_minutes': 1,
                    'cook_time_minutes': 0,
                    'difficulty': 'easy',
                    'cost_estimate_usd': 1.00,
                    'is_batch_friendly': 0,
                    'recipe_instructions': '1. Mix almonds, dried fruit, dark chocolate chips.',
                    'tags': '["quick", "portable"]',
                    'recipe_source': 'custom'
                },
                'ingredients': [
                    {'name': 'almonds', 'quantity': 0.25, 'unit': 'cup'},
                    {'name': 'dried cranberries', 'quantity': 2, 'unit': 'tbsp'},
                    {'name': 'dark chocolate chips', 'quantity': 1, 'unit': 'tbsp'}
                ]
            },
            {
                'meal': {
                    'user_id': user_id,
                    'name': 'Protein Bar',
                    'meal_type': 'snack',
                    'servings': 1,
                    'calories': 220,
                    'protein_g': 20,
                    'carbs_g': 24,
                    'fat_g': 8,
                    'fiber_g': 3,
                    'total_time_minutes': 1,
                    'prep_time_minutes': 1,
                    'cook_time_minutes': 0,
                    'difficulty': 'easy',
                    'cost_estimate_usd': 2.00,
                    'is_batch_friendly': 0,
                    'recipe_instructions': '1. Unwrap and eat.',
                    'tags': '["quick", "high-protein", "portable"]',
                    'recipe_source': 'custom'
                },
                'ingredients': [
                    {'name': 'protein bar', 'quantity': 1, 'unit': 'bar'}
                ]
            },
            {
                'meal': {
                    'user_id': user_id,
                    'name': 'Hummus & Veggies',
                    'meal_type': 'snack',
                    'servings': 1,
                    'calories': 180,
                    'protein_g': 8,
                    'carbs_g': 22,
                    'fat_g': 8,
                    'fiber_g': 7,
                    'total_time_minutes': 5,
                    'prep_time_minutes': 5,
                    'cook_time_minutes': 0,
                    'difficulty': 'easy',
                    'cost_estimate_usd': 1.20,
                    'is_batch_friendly': 0,
                    'recipe_instructions': '1. Cut vegetables. 2. Serve with hummus.',
                    'tags': '["quick", "healthy", "vegetarian"]',
                    'recipe_source': 'custom'
                },
                'ingredients': [
                    {'name': 'hummus', 'quantity': 0.25, 'unit': 'cup'},
                    {'name': 'carrots', 'quantity': 1, 'unit': 'cup'},
                    {'name': 'celery', 'quantity': 1, 'unit': 'cup'}
                ]
            },
            {
                'meal': {
                    'user_id': user_id,
                    'name': 'Hard Boiled Eggs',
                    'meal_type': 'snack',
                    'servings': 1,
                    'calories': 140,
                    'protein_g': 12,
                    'carbs_g': 2,
                    'fat_g': 10,
                    'fiber_g': 0,
                    'total_time_minutes': 12,
                    'prep_time_minutes': 2,
                    'cook_time_minutes': 10,
                    'difficulty': 'easy',
                    'cost_estimate_usd': 0.60,
                    'is_batch_friendly': 1,
                    'recipe_instructions': '1. Boil eggs for 10 minutes. 2. Cool and peel.',
                    'tags': '["high-protein", "budget", "batch-friendly"]',
                    'recipe_source': 'custom'
                },
                'ingredients': [
                    {'name': 'eggs', 'quantity': 2, 'unit': 'whole'}
                ]
            }
        ]

        count = 0
        for item in snacks:
            self.add_meal_with_ingredients(item['meal'], item['ingredients'])
            count += 1
            print(f"[INFO] Added: {item['meal']['name']}")

        print(f"[SUCCESS] Added {count} snack meals")
        return count


if __name__ == "__main__":
    populator = MealLibraryPopulator()

    print("\n" + "=" * 60)
    print("POPULATING MEAL TEMPLATE LIBRARY")
    print("=" * 60)

    breakfast_count = populator.populate_breakfast_meals()
    print()

    lunch_count = populator.populate_lunch_meals()
    print()

    dinner_count = populator.populate_dinner_meals()
    print()

    snack_count = populator.populate_snack_meals()
    print()

    total = breakfast_count + lunch_count + dinner_count + snack_count

    print("=" * 60)
    print(f"[SUCCESS] Populated {total} total meal templates:")
    print(f"  - {breakfast_count} breakfasts")
    print(f"  - {lunch_count} lunches")
    print(f"  - {dinner_count} dinners")
    print(f"  - {snack_count} snacks")
    print("=" * 60)
