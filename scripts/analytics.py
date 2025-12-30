"""
Analytics and insights generation.
Analyze progress, adherence, spending patterns, and detect deficiencies.
"""

from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from scripts.db_manager import DatabaseManager
from scripts.user_profile import UserProfileManager
from scripts.meal_tracker import MealTracker
from scripts.budget_tracker import BudgetTracker
from config.config import DEFAULT_USER_ID, RDA_MALE, RDA_FEMALE


class AnalyticsEngine(DatabaseManager):
    """Generate insights and analytics reports."""

    def __init__(self):
        super().__init__()
        self.user_manager = UserProfileManager()
        self.meal_tracker = MealTracker()
        self.budget_tracker = BudgetTracker()

    def generate_progress_report(
        self,
        days: int = 30,
        user_id: int = DEFAULT_USER_ID
    ) -> Dict:
        """Generate comprehensive progress report."""

        print(f"\n[INFO] Generating {days}-day progress report...")

        # 1. Body composition progress
        body_progress = self.user_manager.get_progress_summary(user_id=user_id, days=days)

        # 2. Nutrition adherence
        nutrition_adherence = self._analyze_nutrition_adherence(days, user_id)

        # 3. Budget performance
        budget_performance = self.budget_tracker.get_spending_trends(weeks=days // 7, user_id=user_id)

        # 4. Top meals
        top_meals = self._get_top_meals(days, user_id)

        # 5. Micronutrient status
        micro_status = self.detect_micronutrient_deficiencies(days, user_id)

        return {
            'period_days': days,
            'body_progress': body_progress,
            'nutrition_adherence': nutrition_adherence,
            'budget_performance': budget_performance,
            'top_meals': top_meals,
            'micronutrient_status': micro_status
        }

    def _analyze_nutrition_adherence(
        self,
        days: int,
        user_id: int
    ) -> Dict:
        """Analyze how well user is hitting nutrition targets."""

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # Get all targets and progress for the period
        targets_query = """
            SELECT
                date,
                calories_target, protein_target_g, carbs_target_g, fat_target_g
            FROM daily_nutrition_targets
            WHERE user_id = ?
            AND date >= ? AND date <= ?
            ORDER BY date
        """
        targets = self.execute_query(targets_query, (user_id, start_date, end_date))

        progress_query = """
            SELECT
                date,
                SUM(calories) as calories_actual,
                SUM(protein_g) as protein_actual,
                SUM(carbs_g) as carbs_actual,
                SUM(fat_g) as fat_actual
            FROM daily_nutrition_progress
            WHERE user_id = ?
            AND date >= ? AND date <= ?
            GROUP BY date
            ORDER BY date
        """
        progress = self.execute_query(progress_query, (user_id, start_date, end_date))

        # Match targets with progress
        progress_by_date = {p['date']: p for p in progress}

        daily_adherence = []
        totals = {
            'calories': {'target': 0, 'actual': 0},
            'protein': {'target': 0, 'actual': 0},
            'carbs': {'target': 0, 'actual': 0},
            'fat': {'target': 0, 'actual': 0}
        }

        days_with_data = 0

        for target in targets:
            target_date = target['date']
            actual = progress_by_date.get(target_date)

            if actual:
                days_with_data += 1

                # Calculate adherence percentages
                cal_adherence = (actual['calories_actual'] / target['calories_target'] * 100) if target['calories_target'] else 0
                pro_adherence = (actual['protein_actual'] / target['protein_target_g'] * 100) if target['protein_target_g'] else 0
                carb_adherence = (actual['carbs_actual'] / target['carbs_target_g'] * 100) if target['carbs_target_g'] else 0
                fat_adherence = (actual['fat_actual'] / target['fat_target_g'] * 100) if target['fat_target_g'] else 0

                daily_adherence.append({
                    'date': target_date,
                    'calories_pct': round(cal_adherence, 1),
                    'protein_pct': round(pro_adherence, 1),
                    'carbs_pct': round(carb_adherence, 1),
                    'fat_pct': round(fat_adherence, 1)
                })

                # Add to totals
                totals['calories']['target'] += target['calories_target']
                totals['calories']['actual'] += actual['calories_actual']
                totals['protein']['target'] += target['protein_target_g']
                totals['protein']['actual'] += actual['protein_actual']
                totals['carbs']['target'] += target['carbs_target_g']
                totals['carbs']['actual'] += actual['carbs_actual']
                totals['fat']['target'] += target['fat_target_g']
                totals['fat']['actual'] += actual['fat_actual']

        # Calculate overall adherence
        overall = {}
        if days_with_data > 0:
            for macro, data in totals.items():
                if data['target'] > 0:
                    adherence_pct = (data['actual'] / data['target'] * 100)
                    overall[macro] = {
                        'target_avg': round(data['target'] / days_with_data, 1),
                        'actual_avg': round(data['actual'] / days_with_data, 1),
                        'adherence_pct': round(adherence_pct, 1)
                    }

        return {
            'days_tracked': days_with_data,
            'overall_adherence': overall,
            'daily_adherence': daily_adherence
        }

    def _get_top_meals(self, days: int, user_id: int, limit: int = 10) -> List[Dict]:
        """Get most frequently eaten and highest rated meals."""

        query = """
            SELECT
                meal_name,
                COUNT(*) as times_eaten,
                AVG(rating) as avg_rating,
                AVG(calories) as avg_calories,
                AVG(protein_g) as avg_protein
            FROM daily_nutrition_progress
            WHERE user_id = ?
            AND date >= date('now', '-' || ? || ' days')
            AND rating IS NOT NULL
            GROUP BY meal_name
            ORDER BY times_eaten DESC, avg_rating DESC
            LIMIT ?
        """

        meals = self.execute_query(query, (user_id, days, limit))

        for meal in meals:
            meal['avg_rating'] = round(meal['avg_rating'], 1) if meal['avg_rating'] else None
            meal['avg_calories'] = round(meal['avg_calories'], 0) if meal['avg_calories'] else None
            meal['avg_protein'] = round(meal['avg_protein'], 1) if meal['avg_protein'] else None

        return meals

    def detect_micronutrient_deficiencies(
        self,
        days: int = 7,
        user_id: int = DEFAULT_USER_ID,
        threshold_pct: float = 70.0
    ) -> Dict:
        """
        Detect micronutrient deficiencies.

        Args:
            days: Number of days to analyze
            user_id: User ID
            threshold_pct: Alert if average intake < this % of RDA
        """

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # Get user info for RDA
        user = self.user_manager.get_user(user_id)
        rda = RDA_MALE if user and user.get('sex') == 'male' else RDA_FEMALE

        # Get nutrition progress
        query = """
            SELECT
                AVG(vitamin_d_mcg) as avg_vitamin_d,
                AVG(vitamin_c_mg) as avg_vitamin_c,
                AVG(vitamin_a_mcg) as avg_vitamin_a,
                AVG(calcium_mg) as avg_calcium,
                AVG(iron_mg) as avg_iron,
                AVG(magnesium_mg) as avg_magnesium,
                AVG(potassium_mg) as avg_potassium,
                AVG(zinc_mg) as avg_zinc,
                AVG(omega3_g) as avg_omega3,
                COUNT(DISTINCT date) as days_tracked
            FROM daily_nutrition_progress
            WHERE user_id = ?
            AND date >= ? AND date <= ?
        """

        result = self.execute_single(query, (user_id, start_date, end_date))

        if not result or result['days_tracked'] == 0:
            return {
                'status': 'insufficient_data',
                'message': 'Not enough nutrition data to analyze'
            }

        # Check each micronutrient
        deficiencies = []
        adequate = []
        not_tracked = []

        micronutrients = {
            'vitamin_d': ('vitamin_d_mcg', 'avg_vitamin_d', 'mcg'),
            'vitamin_c': ('vitamin_c_mg', 'avg_vitamin_c', 'mg'),
            'vitamin_a': ('vitamin_a_mcg', 'avg_vitamin_a', 'mcg'),
            'calcium': ('calcium_mg', 'avg_calcium', 'mg'),
            'iron': ('iron_mg', 'avg_iron', 'mg'),
            'magnesium': ('magnesium_mg', 'avg_magnesium', 'mg'),
            'potassium': ('potassium_mg', 'avg_potassium', 'mg'),
            'zinc': ('zinc_mg', 'avg_zinc', 'mg'),
            'omega3': ('omega3_g', 'avg_omega3', 'g')
        }

        for nutrient_name, (rda_key, avg_key, unit) in micronutrients.items():
            target = rda.get(rda_key, 0)
            actual_avg = result.get(avg_key) or 0

            if actual_avg == 0:
                not_tracked.append(nutrient_name)
                continue

            percent_of_rda = (actual_avg / target * 100) if target > 0 else 0

            nutrient_data = {
                'nutrient': nutrient_name,
                'target': target,
                'actual_avg': round(actual_avg, 1),
                'percent_of_rda': round(percent_of_rda, 1),
                'unit': unit
            }

            if percent_of_rda < threshold_pct:
                # Determine severity
                if percent_of_rda < 50:
                    nutrient_data['severity'] = 'severe'
                elif percent_of_rda < 70:
                    nutrient_data['severity'] = 'moderate'
                else:
                    nutrient_data['severity'] = 'mild'

                nutrient_data['recommendations'] = self._get_nutrient_recommendations(nutrient_name)
                deficiencies.append(nutrient_data)
            else:
                adequate.append(nutrient_data)

        return {
            'status': 'success',
            'days_analyzed': result['days_tracked'],
            'deficiencies': deficiencies,
            'adequate': adequate,
            'not_tracked': not_tracked
        }

    def _get_nutrient_recommendations(self, nutrient: str) -> List[str]:
        """Get food recommendations for specific nutrient deficiency."""

        recommendations = {
            'vitamin_d': ['Salmon', 'Fortified milk', 'Eggs', 'Mushrooms', 'Fortified cereals'],
            'vitamin_c': ['Oranges', 'Bell peppers', 'Strawberries', 'Broccoli', 'Kiwi'],
            'vitamin_a': ['Sweet potatoes', 'Carrots', 'Spinach', 'Kale', 'Eggs'],
            'calcium': ['Milk', 'Yogurt', 'Cheese', 'Tofu', 'Leafy greens'],
            'iron': ['Red meat', 'Spinach', 'Lentils', 'Fortified cereals', 'Oysters'],
            'magnesium': ['Almonds', 'Spinach', 'Black beans', 'Avocado', 'Dark chocolate'],
            'potassium': ['Bananas', 'Sweet potatoes', 'Spinach', 'Beans', 'Yogurt'],
            'zinc': ['Beef', 'Pumpkin seeds', 'Lentils', 'Chickpeas', 'Cashews'],
            'omega3': ['Salmon', 'Walnuts', 'Flaxseeds', 'Chia seeds', 'Sardines']
        }

        return recommendations.get(nutrient, ['Consult a nutritionist'])

    def save_deficiency_alert(
        self,
        nutrient_name: str,
        target_amount: float,
        actual_amount: float,
        severity: str,
        days_consecutive: int = 7,
        user_id: int = DEFAULT_USER_ID
    ) -> int:
        """Save micronutrient deficiency alert to database."""

        percent_of_target = (actual_amount / target_amount * 100) if target_amount > 0 else 0

        recommendations = self._get_nutrient_recommendations(nutrient_name)
        food_suggestions = json.dumps(recommendations)

        query = """
            INSERT INTO micronutrient_deficiency_alerts (
                user_id, date_detected, nutrient_name,
                target_amount, avg_actual_amount, percent_of_target,
                severity, days_consecutive, recommendation, food_suggestions
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            user_id,
            date.today(),
            nutrient_name,
            target_amount,
            actual_amount,
            percent_of_target,
            severity,
            days_consecutive,
            f"Increase intake of {nutrient_name}",
            food_suggestions
        )

        alert_id = self.execute_write(query, params)
        print(f"[ALERT] Deficiency detected: {nutrient_name} ({percent_of_target:.0f}% of target)")
        return alert_id

    def get_active_alerts(self, user_id: int = DEFAULT_USER_ID) -> List[Dict]:
        """Get active (unacknowledged) deficiency alerts."""

        query = """
            SELECT * FROM micronutrient_deficiency_alerts
            WHERE user_id = ?
            AND acknowledged = 0
            AND (resolved_date IS NULL OR resolved_date > date('now'))
            ORDER BY severity DESC, date_detected DESC
        """

        alerts = self.execute_query(query, (user_id,))

        for alert in alerts:
            alert['food_suggestions'] = json.loads(alert.get('food_suggestions', '[]'))

        return alerts


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Analytics Engine")
    parser.add_argument('--progress-report', action='store_true', help='Generate progress report')
    parser.add_argument('--deficiencies', action='store_true', help='Check for nutrient deficiencies')
    parser.add_argument('--alerts', action='store_true', help='Show active deficiency alerts')

    parser.add_argument('--days', type=int, default=30, help='Days to analyze (default: 30)')
    parser.add_argument('--save-alerts', action='store_true', help='Save deficiency alerts to database')

    args = parser.parse_args()

    analytics = AnalyticsEngine()

    if args.progress_report:
        report = analytics.generate_progress_report(days=args.days)

        print(f"\n{'=' * 80}")
        print(f"PROGRESS REPORT - Last {args.days} Days")
        print(f"{'=' * 80}")

        # Body progress
        if report['body_progress']['status'] == 'success':
            bp = report['body_progress']
            print(f"\nBODY COMPOSITION:")
            print(f"  Weight: {bp['starting_weight']} lbs -> {bp['current_weight']} lbs ({bp['weight_change_lbs']:+.1f} lbs)")
            if 'bodyfat_change_pct' in bp:
                print(f"  Body Fat: {bp['starting_bodyfat']}% -> {bp['current_bodyfat']}% ({bp['bodyfat_change_pct']:+.1f}%)")
            if 'muscle_change_lbs' in bp:
                print(f"  Muscle Mass: {bp['muscle_change_lbs']:+.1f} lbs")

        # Nutrition adherence
        if report['nutrition_adherence']['days_tracked'] > 0:
            na = report['nutrition_adherence']['overall_adherence']
            print(f"\nNUTRITION ADHERENCE ({report['nutrition_adherence']['days_tracked']} days tracked):")
            for macro, data in na.items():
                status = "Good" if 90 <= data['adherence_pct'] <= 110 else "Needs adjustment"
                print(f"  {macro.capitalize():10} | Target: {data['target_avg']:6.0f} | Actual: {data['actual_avg']:6.0f} | {data['adherence_pct']:5.1f}% ({status})")

        # Top meals
        if report['top_meals']:
            print(f"\nTOP MEALS:")
            for i, meal in enumerate(report['top_meals'][:5], 1):
                rating_stars = '*' * int(meal['avg_rating']) if meal['avg_rating'] else 'N/A'
                print(f"  {i}. {meal['meal_name']} - {meal['times_eaten']} times | Rating: {rating_stars}")

        # Micronutrient status
        if report['micronutrient_status']['status'] == 'success':
            ms = report['micronutrient_status']
            if ms['deficiencies']:
                print(f"\n[WARNING] MICRONUTRIENT DEFICIENCIES DETECTED:")
                for deficiency in ms['deficiencies']:
                    print(f"  {deficiency['nutrient'].upper()} - {deficiency['actual_avg']:.1f}/{deficiency['target']:.0f} {deficiency['unit']} ({deficiency['percent_of_rda']:.0f}%)")
                    print(f"    Severity: {deficiency['severity']} | Try: {', '.join(deficiency['recommendations'][:3])}")
            else:
                print(f"\n[OK] All tracked micronutrients adequate")

        # Budget performance
        if report['budget_performance']['weeks_analyzed'] > 0:
            bp = report['budget_performance']
            status = "OVER" if bp['is_trending_over'] else "UNDER"
            print(f"\nBUDGET PERFORMANCE:")
            print(f"  Avg weekly: ${bp['avg_weekly_spending']:.2f} / ${bp['weekly_budget']:.2f}")
            print(f"  Trending {status} budget by ${abs(bp['avg_over_under']):.2f}/week")

    elif args.deficiencies:
        print(f"\nChecking for micronutrient deficiencies (last {args.days} days)...")
        print("=" * 80)

        deficiencies = analytics.detect_micronutrient_deficiencies(days=args.days)

        if deficiencies['status'] == 'success':
            if deficiencies['deficiencies']:
                print(f"\n[WARNING] {len(deficiencies['deficiencies'])} DEFICIENCIES DETECTED:\n")

                for def_data in deficiencies['deficiencies']:
                    severity_icon = {
                        'severe': '[!!!]',
                        'moderate': '[!!]',
                        'mild': '[!]'
                    }.get(def_data['severity'], '[?]')

                    print(f"{severity_icon} {def_data['nutrient'].upper()}")
                    print(f"  Target: {def_data['target']:.0f} {def_data['unit']}/day")
                    print(f"  Actual: {def_data['actual_avg']:.1f} {def_data['unit']}/day ({def_data['percent_of_rda']:.0f}% of RDA)")
                    print(f"  Severity: {def_data['severity']}")
                    print(f"  Foods to try: {', '.join(def_data['recommendations'][:5])}")
                    print()

                    if args.save_alerts:
                        analytics.save_deficiency_alert(
                            nutrient_name=def_data['nutrient'],
                            target_amount=def_data['target'],
                            actual_amount=def_data['actual_avg'],
                            severity=def_data['severity'],
                            days_consecutive=deficiencies['days_analyzed']
                        )

            else:
                print("[OK] No deficiencies detected - all micronutrients adequate!")

            if deficiencies['not_tracked']:
                print(f"\nNot tracked: {', '.join(deficiencies['not_tracked'])}")

        else:
            print(f"[ERROR] {deficiencies['message']}")

    elif args.alerts:
        alerts = analytics.get_active_alerts()

        if not alerts:
            print("\n[OK] No active deficiency alerts")
        else:
            print(f"\nActive Deficiency Alerts ({len(alerts)})")
            print("=" * 80)

            for alert in alerts:
                print(f"\n{alert['nutrient_name'].upper()} - Detected on {alert['date_detected']}")
                print(f"  Severity: {alert['severity']}")
                print(f"  Target: {alert['target_amount']:.0f} | Actual: {alert['avg_actual_amount']:.1f} ({alert['percent_of_target']:.0f}%)")
                print(f"  Days consecutive: {alert['days_consecutive']}")
                print(f"  Recommended foods: {', '.join(alert['food_suggestions'][:5])}")

    else:
        parser.print_help()
