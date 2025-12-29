"""
User profile management.
Handles user data, body metrics, goals, and preferences.
"""

from datetime import date, datetime
from typing import Dict, List, Optional
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from scripts.db_manager import DatabaseManager
from config.config import DEFAULT_USER_ID

class UserProfileManager(DatabaseManager):
    """Manage user profile and body metrics."""

    def create_user(
        self,
        name: str,
        age: int,
        sex: str,
        height_inches: float,
        weight_lbs: float,
        body_fat_pct: Optional[float] = None,
        goal_type: str = "maintain",
        activity_level: str = "moderate",
        training_days_per_week: int = 0,
        weekly_budget_usd: float = 75.0,
        dietary_restrictions: List[str] = None,
        food_dislikes: List[str] = None,
        cooking_skill: str = "beginner",
        cooking_frequency: str = "batch_2_3x",
        available_equipment: List[str] = None
    ) -> int:
        """Create a new user profile."""

        # Calculate muscle mass if body fat provided
        muscle_mass_lbs = None
        if body_fat_pct:
            muscle_mass_lbs = weight_lbs * (1 - body_fat_pct / 100)

        # Convert lists to JSON
        dietary_restrictions_json = json.dumps(dietary_restrictions or [])
        food_dislikes_json = json.dumps(food_dislikes or [])
        equipment_json = json.dumps(available_equipment or ["oven", "stovetop", "microwave"])

        query = """
            INSERT INTO user_profile (
                name, age, sex, height_inches,
                weight_lbs, body_fat_pct, muscle_mass_lbs,
                goal_type, activity_level, training_days_per_week,
                cooking_skill, cooking_frequency,
                dietary_restrictions, food_dislikes,
                weekly_budget_usd, available_equipment
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            name, age, sex, height_inches,
            weight_lbs, body_fat_pct, muscle_mass_lbs,
            goal_type, activity_level, training_days_per_week,
            cooking_skill, cooking_frequency,
            dietary_restrictions_json, food_dislikes_json,
            weekly_budget_usd, equipment_json
        )

        user_id = self.execute_write(query, params)
        print(f"[SUCCESS] User profile created with ID: {user_id}")
        return user_id

    def get_user(self, user_id: int = DEFAULT_USER_ID) -> Optional[Dict]:
        """Get user profile."""
        query = "SELECT * FROM user_profile WHERE id = ?"
        user = self.execute_single(query, (user_id,))

        if user:
            # Parse JSON fields
            user['dietary_restrictions'] = json.loads(user.get('dietary_restrictions', '[]'))
            user['food_dislikes'] = json.loads(user.get('food_dislikes', '[]'))
            user['available_equipment'] = json.loads(user.get('available_equipment', '[]'))

        return user

    def update_user(self, user_id: int = DEFAULT_USER_ID, **kwargs) -> bool:
        """Update user profile fields."""

        # Convert lists to JSON if present
        if 'dietary_restrictions' in kwargs:
            kwargs['dietary_restrictions'] = json.dumps(kwargs['dietary_restrictions'])
        if 'food_dislikes' in kwargs:
            kwargs['food_dislikes'] = json.dumps(kwargs['food_dislikes'])
        if 'available_equipment' in kwargs:
            kwargs['available_equipment'] = json.dumps(kwargs['available_equipment'])

        # Build UPDATE query dynamically
        fields = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values())
        values.append(datetime.now())  # updated_at
        values.append(user_id)

        query = f"""
            UPDATE user_profile
            SET {fields}, updated_at = ?
            WHERE id = ?
        """

        self.execute_write(query, tuple(values))
        print(f"[SUCCESS] User profile updated")
        return True

    def log_body_metrics(
        self,
        weight_lbs: float,
        body_fat_pct: Optional[float] = None,
        user_id: int = DEFAULT_USER_ID,
        measurement_date: date = None,
        waist_inches: Optional[float] = None,
        chest_inches: Optional[float] = None,
        arms_inches: Optional[float] = None,
        legs_inches: Optional[float] = None,
        notes: Optional[str] = None
    ) -> int:
        """Log body metrics for tracking progress."""

        if not measurement_date:
            measurement_date = date.today()

        # Calculate muscle mass if body fat provided
        muscle_mass_lbs = None
        if body_fat_pct:
            muscle_mass_lbs = weight_lbs * (1 - body_fat_pct / 100)

        query = """
            INSERT INTO body_metrics_history (
                user_id, date, weight_lbs, body_fat_pct, muscle_mass_lbs,
                waist_inches, chest_inches, arms_inches, legs_inches, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            user_id, measurement_date, weight_lbs, body_fat_pct, muscle_mass_lbs,
            waist_inches, chest_inches, arms_inches, legs_inches, notes
        )
        metric_id = self.execute_write(query, params)

        # Also update user profile with latest metrics
        self.update_user(
            user_id=user_id,
            weight_lbs=weight_lbs,
            body_fat_pct=body_fat_pct,
            muscle_mass_lbs=muscle_mass_lbs
        )

        print(f"[SUCCESS] Body metrics logged for {measurement_date}")
        return metric_id

    def get_metrics_history(
        self,
        days: int = 30,
        user_id: int = DEFAULT_USER_ID
    ) -> List[Dict]:
        """Get body metrics history."""
        query = """
            SELECT * FROM body_metrics_history
            WHERE user_id = ?
            AND date >= date('now', '-' || ? || ' days')
            ORDER BY date DESC
        """

        return self.execute_query(query, (user_id, days))

    def get_latest_metrics(self, user_id: int = DEFAULT_USER_ID) -> Optional[Dict]:
        """Get most recent body metrics."""
        query = """
            SELECT * FROM body_metrics_history
            WHERE user_id = ?
            ORDER BY date DESC
            LIMIT 1
        """

        return self.execute_single(query, (user_id,))

    def get_progress_summary(self, user_id: int = DEFAULT_USER_ID, days: int = 30) -> Dict:
        """Get summary of body composition changes over time period."""
        metrics = self.get_metrics_history(days=days, user_id=user_id)

        if not metrics or len(metrics) < 2:
            return {
                'status': 'insufficient_data',
                'message': 'Need at least 2 measurements to calculate progress'
            }

        # Most recent (first in DESC order) vs oldest
        current = metrics[0]
        starting = metrics[-1]

        weight_change = current['weight_lbs'] - starting['weight_lbs']

        summary = {
            'status': 'success',
            'period_days': days,
            'measurements_count': len(metrics),
            'starting_weight': starting['weight_lbs'],
            'current_weight': current['weight_lbs'],
            'weight_change_lbs': round(weight_change, 1),
            'weight_change_pct': round((weight_change / starting['weight_lbs']) * 100, 1),
        }

        # Add body fat changes if available
        if current.get('body_fat_pct') and starting.get('body_fat_pct'):
            bf_change = current['body_fat_pct'] - starting['body_fat_pct']
            summary['starting_bodyfat'] = starting['body_fat_pct']
            summary['current_bodyfat'] = current['body_fat_pct']
            summary['bodyfat_change_pct'] = round(bf_change, 1)

            if current.get('muscle_mass_lbs') and starting.get('muscle_mass_lbs'):
                muscle_change = current['muscle_mass_lbs'] - starting['muscle_mass_lbs']
                summary['muscle_change_lbs'] = round(muscle_change, 1)

        return summary

# CLI interface for testing
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="User Profile Manager")
    parser.add_argument('--create', action='store_true', help='Create new user')
    parser.add_argument('--view', action='store_true', help='View user profile')
    parser.add_argument('--log-metrics', action='store_true', help='Log body metrics')
    parser.add_argument('--weight', type=float, help='Weight in lbs')
    parser.add_argument('--body-fat', type=float, help='Body fat percentage')
    parser.add_argument('--progress', action='store_true', help='View progress summary')
    parser.add_argument('--days', type=int, default=30, help='Days for history/progress (default: 30)')

    args = parser.parse_args()

    manager = UserProfileManager()

    if args.create:
        # Interactive user creation
        print("Create New User Profile")
        print("-" * 40)
        name = input("Name: ")
        age = int(input("Age: "))
        sex = input("Sex (male/female): ").lower()
        height = float(input("Height (inches): "))
        weight = float(input("Weight (lbs): "))
        body_fat = input("Body fat % (optional, press enter to skip): ")
        body_fat = float(body_fat) if body_fat else None

        goal = input("Goal (bulk/cut/maintain/recomp) [maintain]: ").lower() or "maintain"
        activity = input("Activity level (sedentary/light/moderate/very_active/athlete) [moderate]: ").lower() or "moderate"
        training_days = input("Training days per week [0]: ")
        training_days = int(training_days) if training_days else 0

        user_id = manager.create_user(
            name=name,
            age=age,
            sex=sex,
            height_inches=height,
            weight_lbs=weight,
            body_fat_pct=body_fat,
            goal_type=goal,
            activity_level=activity,
            training_days_per_week=training_days
        )

    elif args.view:
        user = manager.get_user()
        if user:
            print("\nUser Profile:")
            print("-" * 40)
            print(f"Name: {user['name']}")
            print(f"Age: {user['age']} | Sex: {user['sex']}")
            print(f"Height: {user['height_inches']}\"")
            print(f"Weight: {user['weight_lbs']} lbs")
            if user.get('body_fat_pct'):
                print(f"Body Fat: {user['body_fat_pct']}%")
                print(f"Muscle Mass: {user.get('muscle_mass_lbs', 'N/A')} lbs")
            print(f"\nGoal: {user['goal_type']}")
            print(f"Activity Level: {user['activity_level']}")
            print(f"Training Days/Week: {user['training_days_per_week']}")
            print(f"\nCooking Skill: {user['cooking_skill']}")
            print(f"Cooking Frequency: {user['cooking_frequency']}")
            print(f"Weekly Budget: ${user['weekly_budget_usd']}")

            if user['dietary_restrictions']:
                print(f"Dietary Restrictions: {', '.join(user['dietary_restrictions'])}")
            if user['food_dislikes']:
                print(f"Food Dislikes: {', '.join(user['food_dislikes'])}")
        else:
            print("[ERROR] No user profile found. Create one with --create")

    elif args.log_metrics:
        if not args.weight:
            print("[ERROR] --weight required")
        else:
            manager.log_body_metrics(
                weight_lbs=args.weight,
                body_fat_pct=args.body_fat
            )

    elif args.progress:
        summary = manager.get_progress_summary(days=args.days)
        if summary['status'] == 'success':
            print(f"\nProgress Summary (Last {summary['period_days']} days)")
            print("-" * 40)
            print(f"Measurements: {summary['measurements_count']}")
            print(f"Weight: {summary['starting_weight']} lbs -> {summary['current_weight']} lbs")
            print(f"Change: {summary['weight_change_lbs']:+.1f} lbs ({summary['weight_change_pct']:+.1f}%)")

            if 'bodyfat_change_pct' in summary:
                print(f"\nBody Fat: {summary['starting_bodyfat']}% -> {summary['current_bodyfat']}%")
                print(f"Change: {summary['bodyfat_change_pct']:+.1f}%")

            if 'muscle_change_lbs' in summary:
                print(f"Muscle Mass Change: {summary['muscle_change_lbs']:+.1f} lbs")
        else:
            print(f"[ERROR] {summary['message']}")

    else:
        parser.print_help()
