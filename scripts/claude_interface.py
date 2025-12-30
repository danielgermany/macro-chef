"""
Main CLI orchestrator for Macro Chef meal planning system.
Unified interface that ties all modules together with common workflows.
"""

from datetime import date, datetime
from typing import Dict, List, Optional
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

# Import all modules
from scripts.user_profile import UserProfileManager
from scripts.nutrition_calculator import NutritionCalculator
from scripts.meal_tracker import MealTracker
from scripts.inventory_manager import InventoryManager
from scripts.meal_recommender import MealRecommender
from scripts.shopping_list import ShoppingListGenerator
from scripts.budget_tracker import BudgetTracker
from scripts.weekly_planner import WeeklyPlanner
from scripts.analytics import AnalyticsEngine
from config.config import DEFAULT_USER_ID


class MacroChef:
    """Main orchestrator for the Macro Chef system."""

    def __init__(self, user_id: int = DEFAULT_USER_ID):
        """Initialize all managers."""
        self.user_id = user_id

        # Initialize managers
        self.user_manager = UserProfileManager()
        self.nutrition_calc = NutritionCalculator()
        self.meal_tracker = MealTracker()
        self.inventory = InventoryManager()
        self.recommender = MealRecommender()
        self.shopping_gen = ShoppingListGenerator()
        self.budget_tracker = BudgetTracker()
        self.weekly_planner = WeeklyPlanner()
        self.analytics = AnalyticsEngine()

        # Load user context
        self.user = self.user_manager.get_user(user_id)
        self.today = date.today()

    def daily_routine(self):
        """Morning check-in and daily overview."""

        print("\n" + "=" * 80)
        print(f"MACRO CHEF - Daily Check-in ({self.today})")
        print("=" * 80)

        # Get today's targets
        targets = self.nutrition_calc.get_or_create_daily_targets(
            user_id=self.user_id,
            target_date=self.today
        )

        # Get progress
        progress = self.meal_tracker.get_daily_progress(
            user_id=self.user_id,
            target_date=self.today
        )

        # Display targets
        print(f"\nYOUR TARGETS TODAY:")
        print(f"  Goal: {targets['goal_type'].upper()} | TDEE: {targets['tdee_kcal']} kcal")
        if targets.get('is_training_day'):
            print(f"  [TRAINING DAY] Extra carbs included")
        print(f"  Calories: {targets['calories_target']} kcal | Protein: {targets['protein_target_g']}g | Carbs: {targets['carbs_target_g']}g | Fat: {targets['fat_target_g']}g")

        # Display progress
        print(f"\nPROGRESS SO FAR ({progress['meal_count']} meals logged):")
        totals = progress['totals']
        remaining = progress['remaining']
        pct = progress['percentages']

        print(f"  Eaten:     {totals['calories']:4} kcal ({pct['calories']:5.1f}%) | P: {totals['protein_g']:4.0f}g | C: {totals['carbs_g']:4.0f}g | F: {totals['fat_g']:4.0f}g")
        print(f"  Remaining: {remaining['calories']:4} kcal          | P: {remaining['protein_g']:4.0f}g | C: {remaining['carbs_g']:4.0f}g | F: {remaining['fat_g']:4.0f}g")

        # Check inventory alerts
        expiring = self.inventory.get_expiring_soon(days=3, user_id=self.user_id)
        expired = self.inventory.get_expired_items(user_id=self.user_id)

        if expired or expiring:
            print(f"\nINVENTORY ALERTS:")
            for item in expired:
                print(f"  [EXPIRED] {item['item_name']} - expired {item['expiration_date']}")
            for item in expiring:
                days_left = (date.fromisoformat(item['expiration_date']) - self.today).days
                print(f"  [!] {item['item_name']} - {days_left} days left")

        # Budget status
        budget = self.budget_tracker.get_weekly_summary(user_id=self.user_id)
        print(f"\nBUDGET STATUS (This Week):")
        print(f"  ${budget['total_spent']:.2f} / ${budget['budget_limit']:.2f} ({budget['percent_used']:.0f}% used)")

        # Next meal suggestion
        if remaining['calories'] > 200:  # Still need more food
            print(f"\nNEXT MEAL SUGGESTION:")

            # Determine next meal type based on time and what's been logged
            meals_logged = {meal['meal_time'] for meal in progress['meals']}
            hour = datetime.now().hour

            if hour < 10 and 'breakfast' not in meals_logged:
                next_meal = 'breakfast'
            elif hour < 14 and 'lunch' not in meals_logged:
                next_meal = 'lunch'
            elif hour < 20 and 'dinner' not in meals_logged:
                next_meal = 'dinner'
            else:
                next_meal = 'snack'

            recommendations = self.recommender.recommend_meal(
                meal_time=next_meal,
                user_id=self.user_id,
                target_date=self.today
            )

            if recommendations:
                top = recommendations[0]
                print(f"  {next_meal.upper()}: {top['name']}")
                print(f"  {top['calories']} kcal | P: {top['protein_g']:.0f}g | C: {top['carbs_g']:.0f}g | F: {top['fat_g']:.0f}g")
                if top.get('match_reasons'):
                    print(f"  Why: {', '.join(top['match_reasons'][:3])}")

        print(f"\n" + "=" * 80)
        self._show_quick_actions()

    def _show_quick_actions(self):
        """Show available quick actions."""
        print("\nQUICK ACTIONS:")
        print("  1. Log a meal")
        print("  2. Get meal recommendations")
        print("  3. View full progress")
        print("  4. Check inventory")
        print("  5. View budget")
        print("  6. Exit")

    def interactive_meal_log(self):
        """Interactive meal logging workflow."""

        print("\n" + "=" * 80)
        print("LOG A MEAL")
        print("=" * 80)

        # Ask for meal name
        meal_name = input("\nWhat did you eat? ").strip()

        if not meal_name:
            print("[ERROR] Meal name required")
            return

        # Search for templates
        templates = self.recommender.execute_query(
            "SELECT * FROM meal_templates WHERE name LIKE ? ORDER BY rating DESC NULLS LAST LIMIT 5",
            (f"%{meal_name}%",)
        )

        # Search recent meals
        recent = self.meal_tracker.get_meal_history(days=30, meal_name=meal_name, user_id=self.user_id)

        options = []

        # Add templates
        for template in templates:
            options.append({
                'type': 'template',
                'data': template,
                'display': f"{template['name']} ({template['calories']} kcal, {template['protein_g']}g protein) [Template]"
            })

        # Add recent meals
        for meal in recent[:3]:
            options.append({
                'type': 'recent',
                'data': meal,
                'display': f"{meal['meal_name']} ({meal['calories']} kcal, logged {meal['date']}) [Recent]"
            })

        if options:
            print("\nFound these options:")
            for i, option in enumerate(options, 1):
                print(f"  {i}. {option['display']}")
            print(f"  {len(options) + 1}. Enter custom nutrition")

            choice = input(f"\nSelect (1-{len(options) + 1}): ").strip()

            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(options):
                    selected = options[choice_idx]

                    # Get servings
                    servings_str = input("How many servings? [1]: ").strip() or "1"
                    servings = float(servings_str)

                    # Determine meal time
                    meal_time = self._determine_meal_time()

                    # Log the meal
                    data = selected['data']
                    self.meal_tracker.log_meal(
                        meal_name=meal_name,
                        calories=int(data['calories'] * servings),
                        protein_g=data['protein_g'] * servings,
                        carbs_g=data['carbs_g'] * servings,
                        fat_g=data['fat_g'] * servings,
                        fiber_g=data.get('fiber_g', 0) * servings if data.get('fiber_g') else None,
                        meal_time=meal_time,
                        user_id=self.user_id,
                        meal_date=self.today
                    )

                    # Ask for rating
                    rating_str = input("Rate this meal (1-5, or press enter to skip): ").strip()
                    if rating_str and rating_str.isdigit():
                        rating = int(rating_str)
                        if 1 <= rating <= 5:
                            # Get the meal ID we just logged
                            last_meal = self.meal_tracker.execute_single(
                                "SELECT id FROM daily_nutrition_progress WHERE user_id = ? ORDER BY logged_at DESC LIMIT 1",
                                (self.user_id,)
                            )
                            if last_meal:
                                self.meal_tracker.update_meal_rating(last_meal['id'], rating)

                    # Show updated progress
                    self._show_updated_progress()
                    return

            except ValueError:
                pass

        # Custom entry
        print("\nEnter custom nutrition:")
        self._custom_meal_entry(meal_name)

    def _custom_meal_entry(self, meal_name: str):
        """Custom meal entry with manual nutrition data."""

        try:
            calories = int(input("Calories: ").strip())
            protein = float(input("Protein (g): ").strip())
            carbs = float(input("Carbs (g): ").strip())
            fat = float(input("Fat (g): ").strip())

            meal_time = self._determine_meal_time()

            self.meal_tracker.log_meal(
                meal_name=meal_name,
                calories=calories,
                protein_g=protein,
                carbs_g=carbs,
                fat_g=fat,
                meal_time=meal_time,
                user_id=self.user_id,
                meal_date=self.today
            )

            self._show_updated_progress()

        except ValueError:
            print("[ERROR] Invalid input")

    def _determine_meal_time(self) -> str:
        """Determine meal time based on current time."""
        hour = datetime.now().hour

        if hour < 11:
            return 'breakfast'
        elif hour < 15:
            return 'lunch'
        elif hour < 20:
            return 'dinner'
        else:
            return 'snack'

    def _show_updated_progress(self):
        """Show updated daily progress after logging a meal."""

        progress = self.meal_tracker.get_daily_progress(
            user_id=self.user_id,
            target_date=self.today
        )

        print("\n" + "-" * 80)
        print("UPDATED PROGRESS:")
        totals = progress['totals']
        remaining = progress['remaining']

        print(f"  Total:     {totals['calories']:4} kcal | P: {totals['protein_g']:4.0f}g | C: {totals['carbs_g']:4.0f}g | F: {totals['fat_g']:4.0f}g")
        print(f"  Remaining: {remaining['calories']:4} kcal | P: {remaining['protein_g']:4.0f}g | C: {remaining['carbs_g']:4.0f}g | F: {remaining['fat_g']:4.0f}g")
        print("-" * 80)

    def recommend_meal_interactive(self):
        """Interactive meal recommendation."""

        print("\n" + "=" * 80)
        print("MEAL RECOMMENDATIONS")
        print("=" * 80)

        print("\nWhich meal?")
        print("  1. Breakfast")
        print("  2. Lunch")
        print("  3. Dinner")
        print("  4. Snack")
        print("  5. Auto-detect")

        choice = input("\nSelect (1-5): ").strip()

        meal_types = {
            '1': 'breakfast',
            '2': 'lunch',
            '3': 'dinner',
            '4': 'snack',
            '5': 'auto'
        }

        meal_time = meal_types.get(choice, 'auto')

        if meal_time == 'auto':
            meal_time = self._determine_meal_time()

        print(f"\nFinding {meal_time} recommendations...")

        recommendations = self.recommender.recommend_meal(
            meal_time=meal_time,
            user_id=self.user_id,
            target_date=self.today
        )

        if not recommendations:
            print("[ERROR] No recommendations found")
            return

        print(f"\nTOP RECOMMENDATIONS FOR {meal_time.upper()}:")
        print("=" * 80)

        for i, rec in enumerate(recommendations[:5], 1):
            print(f"\n{i}. {rec['name']} (Score: {rec['recommendation_score']}/100)")
            print(f"   {rec['calories']} kcal | P: {rec['protein_g']:.0f}g | C: {rec['carbs_g']:.0f}g | F: {rec['fat_g']:.0f}g")

            if rec.get('total_time_minutes'):
                print(f"   Time: {rec['total_time_minutes']} min", end='')
                if rec.get('difficulty'):
                    print(f" | Difficulty: {rec['difficulty']}", end='')
                print()

            if rec.get('cost_estimate_usd'):
                print(f"   Cost: ${rec['cost_estimate_usd']:.2f}/serving")

            if rec.get('match_reasons'):
                print(f"   Why: {', '.join(rec['match_reasons'])}")

    def weekly_planning_workflow(self):
        """Complete weekly planning workflow."""

        print("\n" + "=" * 80)
        print("WEEKLY MEAL PLANNING")
        print("=" * 80)

        # Show last week's performance
        print("\nAnalyzing last week's performance...")
        body_progress = self.user_manager.get_progress_summary(days=7, user_id=self.user_id)

        if body_progress['status'] == 'success':
            print(f"\nLast 7 Days:")
            print(f"  Weight: {body_progress['starting_weight']} lbs -> {body_progress['current_weight']} lbs ({body_progress['weight_change_lbs']:+.1f} lbs)")

        # Generate plan
        print("\nGenerating weekly meal plan...")

        plan_name = input("Plan name (or press enter for default): ").strip()

        plan = self.weekly_planner.generate_weekly_plan(
            user_id=self.user_id,
            plan_name=plan_name if plan_name else None
        )

        # Show summary
        nutrition = self.weekly_planner.calculate_plan_nutrition(plan)

        print(f"\n{plan['plan_name']}")
        print(f"{plan['week_start']} to {plan['week_end']}")
        print("=" * 80)

        print(f"\nDaily Averages:")
        print(f"  Calories: {nutrition['daily_averages']['calories']:.0f} kcal")
        print(f"  Protein:  {nutrition['daily_averages']['protein_g']:.1f}g")
        print(f"  Carbs:    {nutrition['daily_averages']['carbs_g']:.1f}g")
        print(f"  Fat:      {nutrition['daily_averages']['fat_g']:.1f}g")

        print(f"\nEstimated weekly cost: ${plan['total_cost_estimate']:.2f}")

        # Ask to save
        save = input("\nSave this plan? (y/n): ").strip().lower()

        if save == 'y':
            plan_id = self.weekly_planner.save_plan(plan, user_id=self.user_id)

            # Ask about shopping list
            shopping = input("Generate shopping list? (y/n): ").strip().lower()

            if shopping == 'y':
                shopping_list = self.weekly_planner.generate_shopping_list_from_plan(
                    plan_id, user_id=self.user_id
                )

                formatted = self.shopping_gen.format_shopping_list(shopping_list, group_by='category')
                print("\n" + formatted)

    def dashboard(self):
        """Comprehensive dashboard view."""

        print("\n" + "=" * 80)
        print("MACRO CHEF - DASHBOARD")
        print("=" * 80)

        # Quick stats
        progress = self.meal_tracker.get_daily_progress(user_id=self.user_id, target_date=self.today)
        budget = self.budget_tracker.get_weekly_summary(user_id=self.user_id)

        print(f"\nTODAY'S PROGRESS:")
        print(f"  Meals logged: {progress['meal_count']}")
        print(f"  Calories: {progress['totals']['calories']} / {progress['targets']['calories_target']} ({progress['percentages']['calories']:.0f}%)")

        print(f"\nWEEKLY BUDGET:")
        print(f"  Spent: ${budget['total_spent']:.2f} / ${budget['budget_limit']:.2f}")
        print(f"  Status: {'OVER' if budget['is_over_budget'] else 'OK'}")

        # Body stats
        latest_metrics = self.user_manager.get_latest_metrics(user_id=self.user_id)
        if latest_metrics:
            print(f"\nBODY METRICS (Last recorded: {latest_metrics['date']}):")
            print(f"  Weight: {latest_metrics['weight_lbs']} lbs")
            if latest_metrics.get('body_fat_pct'):
                print(f"  Body Fat: {latest_metrics['body_fat_pct']}%")

        # Inventory alerts
        expiring = len(self.inventory.get_expiring_soon(days=7, user_id=self.user_id))
        if expiring > 0:
            print(f"\nINVENTORY: {expiring} items expiring within 7 days")

        # Micronutrient status
        deficiencies = self.analytics.detect_micronutrient_deficiencies(days=7, user_id=self.user_id)
        if deficiencies['status'] == 'success' and deficiencies['deficiencies']:
            print(f"\n[WARNING] {len(deficiencies['deficiencies'])} micronutrient deficiencies detected")


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Macro Chef - AI-Powered Meal Planning System",
        epilog="For detailed help on any command, use: python claude_interface.py <command> --help"
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Daily routine
    subparsers.add_parser('daily', help='Daily check-in and overview')

    # Dashboard
    subparsers.add_parser('dashboard', help='Comprehensive dashboard view')

    # Log meal
    subparsers.add_parser('log-meal', help='Log a meal (interactive)')

    # Recommend meals
    recommend_parser = subparsers.add_parser('recommend', help='Get meal recommendations')
    recommend_parser.add_argument('meal_type', nargs='?', choices=['breakfast', 'lunch', 'dinner', 'snack'],
                                   help='Meal type (optional, auto-detects if not provided)')

    # Weekly planning
    subparsers.add_parser('plan-week', help='Create weekly meal plan')

    # Progress report
    progress_parser = subparsers.add_parser('progress', help='View progress report')
    progress_parser.add_argument('--days', type=int, default=30, help='Days to analyze (default: 30)')

    # Quick actions
    subparsers.add_parser('inventory', help='Check inventory and expiring items')
    subparsers.add_parser('budget', help='View budget status')

    args = parser.parse_args()

    # Initialize Macro Chef
    chef = MacroChef()

    # Route commands
    if args.command == 'daily':
        chef.daily_routine()

    elif args.command == 'dashboard':
        chef.dashboard()

    elif args.command == 'log-meal':
        chef.interactive_meal_log()

    elif args.command == 'recommend':
        chef.recommend_meal_interactive()

    elif args.command == 'plan-week':
        chef.weekly_planning_workflow()

    elif args.command == 'progress':
        report = chef.analytics.generate_progress_report(days=args.days, user_id=chef.user_id)
        # Display formatted report (reuse analytics display logic)
        import subprocess
        subprocess.run([sys.executable, 'scripts/analytics.py', '--progress-report', '--days', str(args.days)])

    elif args.command == 'inventory':
        summary = chef.inventory.get_inventory_summary(user_id=chef.user_id)
        expiring = chef.inventory.get_expiring_soon(days=7, user_id=chef.user_id)

        print("\nInventory Summary")
        print("=" * 60)
        print(f"Total items: {summary['total_items']}")

        if summary['expired'] > 0:
            print(f"[WARNING] Expired: {summary['expired']}")
        if summary['expiring_soon_7days'] > 0:
            print(f"Expiring within 7 days: {summary['expiring_soon_7days']}")

        if expiring:
            print("\nExpiring Soon:")
            for item in expiring:
                days_left = (date.fromisoformat(item['expiration_date']) - date.today()).days
                print(f"  {item['item_name']}: {days_left} days left")

    elif args.command == 'budget':
        budget = chef.budget_tracker.get_weekly_summary(user_id=chef.user_id)

        print("\nWeekly Budget")
        print("=" * 60)
        print(f"Week: {budget['start_date']} to {budget['end_date']}")
        print(f"Spent: ${budget['total_spent']:.2f} / ${budget['budget_limit']:.2f}")
        print(f"Remaining: ${budget['remaining']:.2f}")

        if budget['is_over_budget']:
            print(f"\n[WARNING] Over budget by ${abs(budget['remaining']):.2f}!")

    else:
        parser.print_help()
