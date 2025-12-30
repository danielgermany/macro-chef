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
from config.config import DEFAULT_USER_ID


class MealRecommender(DatabaseManager):
    """Recommend meals based on user needs and constraints."""

    def __init__(self):
        super().__init__()
        self.meal_tracker = MealTracker()
        self.inventory_manager = InventoryManager()
        self.user_manager = UserProfileManager()

    def recommend_meal(
        self,
        meal_time: str = "dinner",
        user_id: int = DEFAULT_USER_ID,
        target_date: date = None,
        max_time: Optional[int] = None,
        use_inventory: bool = True,
        budget_limit: Optional[float] = None
    ) -> List[Dict]:
        """
        Recommend meals based on current progress and constraints.

        Args:
            meal_time: Meal type (breakfast, lunch, dinner, snack)
            user_id: User ID
            target_date: Date for recommendations (default: today)
            max_time: Maximum cooking time in minutes
            use_inventory: Consider inventory when recommending
            budget_limit: Maximum cost per meal
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

        return min(score, 100)  # Cap at 100

    def _calculate_inventory_match(self, meal: Dict, user_id: int) -> float:
        """Calculate how well meal ingredients match inventory (0-20 points)."""

        # Get meal ingredients
        ingredients_query = """
            SELECT ingredient_name FROM meal_ingredients
            WHERE meal_template_id = ?
        """
        ingredients = self.execute_query(ingredients_query, (meal['id'],))

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
