"""
Meal tracking and daily nutrition progress monitoring.
Log meals, track macros, and compare against daily targets.
"""

from datetime import date, datetime
from typing import Dict, List, Optional
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from scripts.db_manager import DatabaseManager
from scripts.nutrition_calculator import NutritionCalculator
from config.config import DEFAULT_USER_ID


class MealTracker(DatabaseManager):
    """Track meals and monitor daily nutrition progress."""

    def __init__(self):
        super().__init__()
        self.nutrition_calc = NutritionCalculator()

    def log_meal(
        self,
        meal_name: str,
        calories: int,
        protein_g: float,
        carbs_g: float,
        fat_g: float,
        meal_time: str = "snack",
        fiber_g: Optional[float] = None,
        sugar_g: Optional[float] = None,
        saturated_fat_g: Optional[float] = None,
        sodium_mg: Optional[float] = None,
        cholesterol_mg: Optional[float] = None,
        serving_size: Optional[str] = None,
        notes: Optional[str] = None,
        rating: Optional[int] = None,
        user_id: int = DEFAULT_USER_ID,
        meal_date: date = None
    ) -> int:
        """Log a meal with nutrition data."""

        if not meal_date:
            meal_date = date.today()

        # Validate meal_time
        valid_meal_times = ['breakfast', 'lunch', 'dinner', 'snack']
        if meal_time not in valid_meal_times:
            raise ValueError(f"meal_time must be one of: {valid_meal_times}")

        # Validate rating if provided
        if rating is not None and (rating < 1 or rating > 5):
            raise ValueError("rating must be between 1 and 5")

        query = """
            INSERT INTO daily_nutrition_progress (
                user_id, date, meal_time, meal_name,
                calories, protein_g, carbs_g, fat_g, fiber_g,
                sugar_g, saturated_fat_g, sodium_mg, cholesterol_mg,
                serving_size, notes, rating
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            user_id, meal_date, meal_time, meal_name,
            calories, protein_g, carbs_g, fat_g, fiber_g,
            sugar_g, saturated_fat_g, sodium_mg, cholesterol_mg,
            serving_size, notes, rating
        )

        meal_id = self.execute_write(query, params)
        print(f"[SUCCESS] Meal logged: {meal_name} ({calories} kcal, {protein_g}g protein)")
        return meal_id

    def get_daily_progress(
        self,
        user_id: int = DEFAULT_USER_ID,
        target_date: date = None
    ) -> Dict:
        """Get nutrition progress for a specific day with targets comparison."""

        if not target_date:
            target_date = date.today()

        # Get all meals for the day
        meals_query = """
            SELECT * FROM daily_nutrition_progress
            WHERE user_id = ? AND date = ?
            ORDER BY logged_at ASC
        """
        meals = self.execute_query(meals_query, (user_id, target_date))

        # Get targets for the day
        targets = self.nutrition_calc.get_or_create_daily_targets(user_id, target_date)

        # Calculate totals from meals
        totals = {
            'calories': 0,
            'protein_g': 0,
            'carbs_g': 0,
            'fat_g': 0,
            'fiber_g': 0,
            'sugar_g': 0,
            'saturated_fat_g': 0,
            'sodium_mg': 0,
            'cholesterol_mg': 0
        }

        for meal in meals:
            totals['calories'] += meal.get('calories', 0) or 0
            totals['protein_g'] += meal.get('protein_g', 0) or 0
            totals['carbs_g'] += meal.get('carbs_g', 0) or 0
            totals['fat_g'] += meal.get('fat_g', 0) or 0
            totals['fiber_g'] += meal.get('fiber_g', 0) or 0
            totals['sugar_g'] += meal.get('sugar_g', 0) or 0
            totals['saturated_fat_g'] += meal.get('saturated_fat_g', 0) or 0
            totals['sodium_mg'] += meal.get('sodium_mg', 0) or 0
            totals['cholesterol_mg'] += meal.get('cholesterol_mg', 0) or 0

        # Calculate remaining macros
        remaining = {
            'calories': targets['calories_target'] - totals['calories'],
            'protein_g': targets['protein_target_g'] - totals['protein_g'],
            'carbs_g': targets['carbs_target_g'] - totals['carbs_g'],
            'fat_g': targets['fat_target_g'] - totals['fat_g'],
            'fiber_g': (targets.get('fiber_target_g', 0) or 0) - totals['fiber_g']
        }

        # Calculate percentages
        percentages = {
            'calories': round((totals['calories'] / targets['calories_target']) * 100, 1) if targets['calories_target'] else 0,
            'protein_g': round((totals['protein_g'] / targets['protein_target_g']) * 100, 1) if targets['protein_target_g'] else 0,
            'carbs_g': round((totals['carbs_g'] / targets['carbs_target_g']) * 100, 1) if targets['carbs_target_g'] else 0,
            'fat_g': round((totals['fat_g'] / targets['fat_target_g']) * 100, 1) if targets['fat_target_g'] else 0
        }

        return {
            'date': target_date,
            'meals': meals,
            'meal_count': len(meals),
            'totals': totals,
            'targets': targets,
            'remaining': remaining,
            'percentages': percentages
        }

    def get_meal_history(
        self,
        days: int = 7,
        meal_name: Optional[str] = None,
        user_id: int = DEFAULT_USER_ID
    ) -> List[Dict]:
        """Get meal history, optionally filtered by meal name."""

        if meal_name:
            query = """
                SELECT * FROM daily_nutrition_progress
                WHERE user_id = ?
                AND date >= date('now', '-' || ? || ' days')
                AND meal_name LIKE ?
                ORDER BY date DESC, logged_at DESC
            """
            params = (user_id, days, f"%{meal_name}%")
        else:
            query = """
                SELECT * FROM daily_nutrition_progress
                WHERE user_id = ?
                AND date >= date('now', '-' || ? || ' days')
                ORDER BY date DESC, logged_at DESC
            """
            params = (user_id, days)

        return self.execute_query(query, params)

    def get_weekly_summary(
        self,
        user_id: int = DEFAULT_USER_ID,
        days: int = 7
    ) -> Dict:
        """Get weekly nutrition summary with averages and adherence."""

        query = """
            SELECT
                date,
                SUM(calories) as total_calories,
                SUM(protein_g) as total_protein,
                SUM(carbs_g) as total_carbs,
                SUM(fat_g) as total_fat,
                COUNT(*) as meal_count
            FROM daily_nutrition_progress
            WHERE user_id = ?
            AND date >= date('now', '-' || ? || ' days')
            GROUP BY date
            ORDER BY date DESC
        """

        daily_totals = self.execute_query(query, (user_id, days))

        if not daily_totals:
            return {
                'status': 'no_data',
                'message': 'No meal data found for this period'
            }

        # Calculate averages
        total_days = len(daily_totals)
        avg_calories = sum(d['total_calories'] for d in daily_totals) / total_days
        avg_protein = sum(d['total_protein'] for d in daily_totals) / total_days
        avg_carbs = sum(d['total_carbs'] for d in daily_totals) / total_days
        avg_fat = sum(d['total_fat'] for d in daily_totals) / total_days
        avg_meals_per_day = sum(d['meal_count'] for d in daily_totals) / total_days

        # Get target for comparison (use most recent)
        latest_target = self.nutrition_calc.get_daily_targets(user_id)

        adherence = {}
        if latest_target:
            adherence = {
                'calories': round((avg_calories / latest_target['calories_target']) * 100, 1),
                'protein': round((avg_protein / latest_target['protein_target_g']) * 100, 1),
                'carbs': round((avg_carbs / latest_target['carbs_target_g']) * 100, 1),
                'fat': round((avg_fat / latest_target['fat_target_g']) * 100, 1)
            }

        return {
            'status': 'success',
            'period_days': days,
            'days_with_data': total_days,
            'averages': {
                'calories': round(avg_calories, 1),
                'protein_g': round(avg_protein, 1),
                'carbs_g': round(avg_carbs, 1),
                'fat_g': round(avg_fat, 1),
                'meals_per_day': round(avg_meals_per_day, 1)
            },
            'adherence': adherence,
            'daily_data': daily_totals
        }

    def delete_meal(self, meal_id: int) -> bool:
        """Delete a logged meal by ID."""
        query = "DELETE FROM daily_nutrition_progress WHERE id = ?"
        self.execute_write(query, (meal_id,))
        print(f"[SUCCESS] Meal deleted (ID: {meal_id})")
        return True

    def update_meal_rating(self, meal_id: int, rating: int) -> bool:
        """Update the rating for a meal."""
        if rating < 1 or rating > 5:
            raise ValueError("rating must be between 1 and 5")

        query = "UPDATE daily_nutrition_progress SET rating = ? WHERE id = ?"
        self.execute_write(query, (rating, meal_id))
        print(f"[SUCCESS] Meal rating updated to {rating}")
        return True


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Meal Tracker")
    parser.add_argument('--log', action='store_true', help='Log a new meal')
    parser.add_argument('--progress', action='store_true', help='View today\'s progress')
    parser.add_argument('--weekly', action='store_true', help='View weekly summary')
    parser.add_argument('--history', action='store_true', help='View meal history')

    # Meal logging arguments
    parser.add_argument('--name', type=str, help='Meal name')
    parser.add_argument('--calories', type=int, help='Calories')
    parser.add_argument('--protein', type=float, help='Protein (g)')
    parser.add_argument('--carbs', type=float, help='Carbs (g)')
    parser.add_argument('--fat', type=float, help='Fat (g)')
    parser.add_argument('--fiber', type=float, help='Fiber (g)')
    parser.add_argument('--meal-time', type=str, choices=['breakfast', 'lunch', 'dinner', 'snack'],
                       default='snack', help='Meal time (default: snack)')
    parser.add_argument('--rating', type=int, choices=[1, 2, 3, 4, 5], help='Rating 1-5')

    # Query arguments
    parser.add_argument('--days', type=int, default=7, help='Days for history/weekly (default: 7)')

    args = parser.parse_args()

    tracker = MealTracker()

    if args.log:
        if not all([args.name, args.calories, args.protein, args.carbs, args.fat]):
            print("[ERROR] --name, --calories, --protein, --carbs, --fat are required for logging")
            parser.print_help()
        else:
            tracker.log_meal(
                meal_name=args.name,
                calories=args.calories,
                protein_g=args.protein,
                carbs_g=args.carbs,
                fat_g=args.fat,
                fiber_g=args.fiber,
                meal_time=args.meal_time,
                rating=args.rating
            )

    elif args.progress:
        progress = tracker.get_daily_progress()
        print(f"\nDaily Progress - {progress['date']}")
        print("=" * 60)

        if progress['meal_count'] == 0:
            print("No meals logged yet today.")
        else:
            print(f"\nMeals logged: {progress['meal_count']}")
            print("-" * 60)
            for i, meal in enumerate(progress['meals'], 1):
                print(f"{i}. {meal['meal_name']} ({meal['meal_time']})")
                print(f"   {meal['calories']} kcal | P: {meal['protein_g']}g | C: {meal['carbs_g']}g | F: {meal['fat_g']}g")
                if meal.get('rating'):
                    print(f"   Rating: {'*' * meal['rating']}")

        print("\n" + "=" * 60)
        print("TOTALS vs TARGETS")
        print("=" * 60)

        totals = progress['totals']
        targets = progress['targets']
        remaining = progress['remaining']
        pct = progress['percentages']

        print(f"Calories:  {totals['calories']:>4} / {targets['calories_target']:>4} kcal ({pct['calories']:>5}%) | Remaining: {remaining['calories']:>4}")
        print(f"Protein:   {totals['protein_g']:>4.0f} / {targets['protein_target_g']:>4}g     ({pct['protein_g']:>5}%) | Remaining: {remaining['protein_g']:>4.0f}g")
        print(f"Carbs:     {totals['carbs_g']:>4.0f} / {targets['carbs_target_g']:>4}g     ({pct['carbs_g']:>5}%) | Remaining: {remaining['carbs_g']:>4.0f}g")
        print(f"Fat:       {totals['fat_g']:>4.0f} / {targets['fat_target_g']:>4}g     ({pct['fat_g']:>5}%) | Remaining: {remaining['fat_g']:>4.0f}g")
        if targets.get('fiber_target_g'):
            print(f"Fiber:     {totals['fiber_g']:>4.0f} / {targets['fiber_target_g']:>4}g")

    elif args.weekly:
        summary = tracker.get_weekly_summary(days=args.days)

        if summary['status'] == 'success':
            print(f"\nWeekly Summary (Last {summary['period_days']} days)")
            print("=" * 60)
            print(f"Days with data: {summary['days_with_data']}")

            print("\nDaily Averages:")
            print("-" * 60)
            avg = summary['averages']
            print(f"Calories:       {avg['calories']:.0f} kcal")
            print(f"Protein:        {avg['protein_g']:.1f}g")
            print(f"Carbs:          {avg['carbs_g']:.1f}g")
            print(f"Fat:            {avg['fat_g']:.1f}g")
            print(f"Meals per day:  {avg['meals_per_day']:.1f}")

            if summary['adherence']:
                print("\nTarget Adherence:")
                print("-" * 60)
                adh = summary['adherence']
                print(f"Calories:  {adh['calories']:.1f}%")
                print(f"Protein:   {adh['protein']:.1f}%")
                print(f"Carbs:     {adh['carbs']:.1f}%")
                print(f"Fat:       {adh['fat']:.1f}%")
        else:
            print(f"[ERROR] {summary['message']}")

    elif args.history:
        meals = tracker.get_meal_history(days=args.days)

        if not meals:
            print(f"No meals found in the last {args.days} days.")
        else:
            print(f"\nMeal History (Last {args.days} days)")
            print("=" * 60)

            current_date = None
            for meal in meals:
                if meal['date'] != current_date:
                    current_date = meal['date']
                    print(f"\n{current_date}")
                    print("-" * 60)

                rating_str = f" | Rating: {'*' * meal['rating']}" if meal.get('rating') else ""
                print(f"{meal['meal_name']} ({meal['meal_time']})")
                print(f"  {meal['calories']} kcal | P: {meal['protein_g']}g | C: {meal['carbs_g']}g | F: {meal['fat_g']}g{rating_str}")

    else:
        parser.print_help()
