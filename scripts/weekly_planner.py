"""
Weekly meal planning and management.
Generate, save, and manage 7-day meal plans with nutrition and cost estimates.
"""

from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from scripts.db_manager import DatabaseManager
from scripts.meal_recommender import MealRecommender
from scripts.shopping_list import ShoppingListGenerator
from scripts.user_profile import UserProfileManager
from scripts.nutrition_calculator import NutritionCalculator
from config.config import DEFAULT_USER_ID


class WeeklyPlanner(DatabaseManager):
    """Create and manage weekly meal plans."""

    def __init__(self):
        super().__init__()
        self.recommender = MealRecommender()
        self.shopping_gen = ShoppingListGenerator()
        self.user_manager = UserProfileManager()
        self.nutrition_calc = NutritionCalculator()

    def generate_weekly_plan(
        self,
        week_start: Optional[date] = None,
        user_id: int = DEFAULT_USER_ID,
        plan_name: Optional[str] = None,
        auto_recommend: bool = True
    ) -> Dict:
        """
        Generate a 7-day meal plan.

        Args:
            week_start: Start date (default: next Monday)
            user_id: User ID
            plan_name: Optional name for the plan
            auto_recommend: Use recommender to suggest meals
        """

        if not week_start:
            # Default to next Monday
            today = date.today()
            days_ahead = 0 - today.weekday() + 7
            if days_ahead <= 0:
                days_ahead += 7
            week_start = today + timedelta(days=days_ahead)

        week_end = week_start + timedelta(days=6)

        if not plan_name:
            plan_name = f"Week of {week_start.strftime('%b %d')}"

        print(f"\n[INFO] Generating meal plan: {plan_name}")
        print(f"Period: {week_start} to {week_end}")

        # Get user profile for training days
        user = self.user_manager.get_user(user_id)
        training_days_per_week = user.get('training_days_per_week', 0) if user else 0

        # Generate daily meal plans
        daily_plans = []
        total_cost = 0

        days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

        for i in range(7):
            current_date = week_start + timedelta(days=i)
            day_name = days_of_week[i]

            # Determine if training day (distribute evenly)
            is_training_day = i < training_days_per_week

            # Generate targets for this day
            targets = self.nutrition_calc.generate_daily_targets(
                user_id=user_id,
                target_date=current_date,
                is_training_day=is_training_day
            )

            # Get meal recommendations for each meal time
            daily_meals = {}
            daily_cost = 0

            for meal_time in ['breakfast', 'lunch', 'dinner', 'snack']:
                if auto_recommend:
                    # Get top recommendation
                    recommendations = self.recommender.recommend_meal(
                        meal_time=meal_time,
                        user_id=user_id,
                        target_date=current_date,
                        use_inventory=False  # Don't check inventory for future plans
                    )

                    if recommendations:
                        meal = recommendations[0]  # Top recommendation
                        daily_meals[meal_time] = {
                            'meal_template_id': meal['id'],
                            'meal_name': meal['name'],
                            'servings': 1,
                            'calories': meal['calories'],
                            'protein_g': meal['protein_g'],
                            'carbs_g': meal['carbs_g'],
                            'fat_g': meal['fat_g']
                        }

                        if meal.get('cost_estimate_usd'):
                            daily_cost += meal['cost_estimate_usd']

            daily_plans.append({
                'date': current_date,
                'day_of_week': day_name,
                'is_training_day': is_training_day,
                'targets': targets,
                'meals': daily_meals,
                'daily_cost': daily_cost
            })

            total_cost += daily_cost

        return {
            'plan_name': plan_name,
            'week_start': week_start,
            'week_end': week_end,
            'daily_plans': daily_plans,
            'total_cost_estimate': round(total_cost, 2)
        }

    def save_plan(
        self,
        plan: Dict,
        user_id: int = DEFAULT_USER_ID
    ) -> int:
        """Save weekly meal plan to database."""

        # Insert plan
        plan_query = """
            INSERT INTO weekly_meal_plans (
                user_id, week_start_date, week_end_date,
                plan_name, total_cost_estimate_usd
            ) VALUES (?, ?, ?, ?, ?)
        """

        plan_id = self.execute_write(
            plan_query,
            (
                user_id,
                plan['week_start'],
                plan['week_end'],
                plan['plan_name'],
                plan['total_cost_estimate']
            )
        )

        # Insert daily meals
        item_query = """
            INSERT INTO weekly_meal_plan_items (
                plan_id, day_of_week, meal_time,
                meal_template_id, servings, notes
            ) VALUES (?, ?, ?, ?, ?, ?)
        """

        items_to_insert = []
        for daily in plan['daily_plans']:
            for meal_time, meal_data in daily['meals'].items():
                items_to_insert.append((
                    plan_id,
                    daily['day_of_week'],
                    meal_time,
                    meal_data['meal_template_id'],
                    meal_data['servings'],
                    None
                ))

        self.execute_many(item_query, items_to_insert)

        print(f"[SUCCESS] Meal plan saved (ID: {plan_id})")
        return plan_id

    def get_plan(self, plan_id: int) -> Optional[Dict]:
        """Retrieve a saved meal plan."""

        # Get plan metadata
        plan_query = "SELECT * FROM weekly_meal_plans WHERE id = ?"
        plan = self.execute_single(plan_query, (plan_id,))

        if not plan:
            return None

        # Get plan items with meal details
        items_query = """
            SELECT
                wpi.*,
                mt.name as meal_name,
                mt.calories, mt.protein_g, mt.carbs_g, mt.fat_g,
                mt.cost_estimate_usd
            FROM weekly_meal_plan_items wpi
            JOIN meal_templates mt ON wpi.meal_template_id = mt.id
            WHERE wpi.plan_id = ?
            ORDER BY
                CASE wpi.day_of_week
                    WHEN 'monday' THEN 1
                    WHEN 'tuesday' THEN 2
                    WHEN 'wednesday' THEN 3
                    WHEN 'thursday' THEN 4
                    WHEN 'friday' THEN 5
                    WHEN 'saturday' THEN 6
                    WHEN 'sunday' THEN 7
                END,
                CASE wpi.meal_time
                    WHEN 'breakfast' THEN 1
                    WHEN 'lunch' THEN 2
                    WHEN 'dinner' THEN 3
                    WHEN 'snack' THEN 4
                END
        """

        items = self.execute_query(items_query, (plan_id,))

        # Organize by day
        daily_plans = {}
        for item in items:
            day = item['day_of_week']
            if day not in daily_plans:
                daily_plans[day] = []

            daily_plans[day].append({
                'meal_time': item['meal_time'],
                'meal_name': item['meal_name'],
                'meal_template_id': item['meal_template_id'],
                'servings': item['servings'],
                'calories': item['calories'] * item['servings'],
                'protein_g': item['protein_g'] * item['servings'],
                'carbs_g': item['carbs_g'] * item['servings'],
                'fat_g': item['fat_g'] * item['servings'],
                'cost_estimate_usd': (item['cost_estimate_usd'] or 0) * item['servings']
            })

        return {
            'plan_id': plan['id'],
            'plan_name': plan['plan_name'],
            'week_start': plan['week_start_date'],
            'week_end': plan['week_end_date'],
            'total_cost_estimate': plan['total_cost_estimate_usd'],
            'daily_plans': daily_plans
        }

    def get_recent_plans(
        self,
        limit: int = 5,
        user_id: int = DEFAULT_USER_ID
    ) -> List[Dict]:
        """Get recent meal plans."""

        query = """
            SELECT * FROM weekly_meal_plans
            WHERE user_id = ?
            ORDER BY week_start_date DESC
            LIMIT ?
        """

        return self.execute_query(query, (user_id, limit))

    def generate_shopping_list_from_plan(
        self,
        plan_id: int,
        user_id: int = DEFAULT_USER_ID
    ) -> Dict:
        """Generate shopping list from a saved meal plan."""

        plan = self.get_plan(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")

        # Collect all meal IDs and servings
        meal_ids = []
        servings = []

        for day_meals in plan['daily_plans'].values():
            for meal in day_meals:
                meal_ids.append(meal['meal_template_id'])
                servings.append(meal['servings'])

        # Generate shopping list
        shopping_list = self.shopping_gen.generate_from_meals(
            meal_ids=meal_ids,
            servings_per_meal=servings,
            check_inventory=True,
            user_id=user_id
        )

        return shopping_list

    def calculate_plan_nutrition(self, plan: Dict) -> Dict:
        """Calculate weekly nutrition totals and averages."""

        totals = {
            'calories': 0,
            'protein_g': 0,
            'carbs_g': 0,
            'fat_g': 0
        }

        daily_totals = []

        for day_data in plan['daily_plans']:
            day_totals = {'calories': 0, 'protein_g': 0, 'carbs_g': 0, 'fat_g': 0}

            for meal in day_data['meals'].values():
                day_totals['calories'] += meal['calories']
                day_totals['protein_g'] += meal['protein_g']
                day_totals['carbs_g'] += meal['carbs_g']
                day_totals['fat_g'] += meal['fat_g']

            daily_totals.append(day_totals)

            totals['calories'] += day_totals['calories']
            totals['protein_g'] += day_totals['protein_g']
            totals['carbs_g'] += day_totals['carbs_g']
            totals['fat_g'] += day_totals['fat_g']

        averages = {
            'calories': round(totals['calories'] / 7, 0),
            'protein_g': round(totals['protein_g'] / 7, 1),
            'carbs_g': round(totals['carbs_g'] / 7, 1),
            'fat_g': round(totals['fat_g'] / 7, 1)
        }

        return {
            'weekly_totals': totals,
            'daily_averages': averages,
            'daily_breakdown': daily_totals
        }


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Weekly Meal Planner")
    parser.add_argument('--generate', action='store_true', help='Generate new weekly plan')
    parser.add_argument('--view', type=int, help='View plan by ID')
    parser.add_argument('--list', action='store_true', help='List recent plans')
    parser.add_argument('--shopping-list', type=int, help='Generate shopping list from plan ID')

    parser.add_argument('--name', type=str, help='Plan name')
    parser.add_argument('--start-date', type=str, help='Week start date (YYYY-MM-DD)')
    parser.add_argument('--save', action='store_true', help='Save generated plan to database')

    args = parser.parse_args()

    planner = WeeklyPlanner()

    if args.generate:
        # Parse start date if provided
        week_start = None
        if args.start_date:
            week_start = date.fromisoformat(args.start_date)

        print("\nGenerating weekly meal plan...")
        print("=" * 80)

        plan = planner.generate_weekly_plan(
            week_start=week_start,
            plan_name=args.name
        )

        # Display plan
        print(f"\n{plan['plan_name']}")
        print(f"{plan['week_start']} to {plan['week_end']}")
        print("=" * 80)

        days_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

        for daily in plan['daily_plans']:
            day_name = daily['day_of_week'].upper()
            training_marker = " (TRAINING DAY)" if daily['is_training_day'] else ""
            print(f"\n{day_name}{training_marker} - {daily['date']}")
            print("-" * 80)

            for meal_time in ['breakfast', 'lunch', 'dinner', 'snack']:
                if meal_time in daily['meals']:
                    meal = daily['meals'][meal_time]
                    print(f"  {meal_time.capitalize():10} | {meal['meal_name']}")
                    print(f"             | {meal['calories']} kcal | P: {meal['protein_g']:.0f}g | C: {meal['carbs_g']:.0f}g | F: {meal['fat_g']:.0f}g")

            print(f"\n  Daily cost: ${daily['daily_cost']:.2f}")

        # Calculate nutrition
        nutrition = planner.calculate_plan_nutrition(plan)

        print("\n" + "=" * 80)
        print("WEEKLY SUMMARY")
        print("=" * 80)
        print(f"Estimated total cost: ${plan['total_cost_estimate']:.2f}")
        print(f"\nDaily averages:")
        print(f"  Calories: {nutrition['daily_averages']['calories']:.0f} kcal")
        print(f"  Protein:  {nutrition['daily_averages']['protein_g']:.1f}g")
        print(f"  Carbs:    {nutrition['daily_averages']['carbs_g']:.1f}g")
        print(f"  Fat:      {nutrition['daily_averages']['fat_g']:.1f}g")

        # Save if requested
        if args.save:
            plan_id = planner.save_plan(plan)
            print(f"\n[SUCCESS] Plan saved with ID: {plan_id}")

    elif args.view:
        plan = planner.get_plan(args.view)

        if not plan:
            print(f"[ERROR] Plan {args.view} not found")
        else:
            print(f"\n{plan['plan_name']}")
            print(f"{plan['week_start']} to {plan['week_end']}")
            print("=" * 80)

            days_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

            for day in days_order:
                if day in plan['daily_plans']:
                    print(f"\n{day.upper()}")
                    print("-" * 80)

                    for meal in plan['daily_plans'][day]:
                        print(f"  {meal['meal_time'].capitalize():10} | {meal['meal_name']}")
                        print(f"             | {meal['calories']:.0f} kcal | P: {meal['protein_g']:.0f}g | C: {meal['carbs_g']:.0f}g | F: {meal['fat_g']:.0f}g")

            print(f"\nTotal cost estimate: ${plan['total_cost_estimate']:.2f}")

    elif args.list:
        plans = planner.get_recent_plans()

        if not plans:
            print("No meal plans found")
        else:
            print("\nRecent Meal Plans")
            print("=" * 80)

            for plan in plans:
                print(f"\nID: {plan['id']} | {plan['plan_name']}")
                print(f"  Week: {plan['week_start_date']} to {plan['week_end_date']}")
                print(f"  Cost: ${plan['total_cost_estimate_usd']:.2f}")

    elif args.shopping_list:
        print(f"\nGenerating shopping list for plan {args.shopping_list}...")
        print("=" * 80)

        shopping_list = planner.generate_shopping_list_from_plan(args.shopping_list)
        formatted = planner.shopping_gen.format_shopping_list(shopping_list, group_by='category')

        print(formatted)

    else:
        parser.print_help()
