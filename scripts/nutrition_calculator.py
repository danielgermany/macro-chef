"""
Nutrition calculator for macro and micronutrient targets.
Calculates daily targets based on user profile and goals.
"""

from datetime import date, datetime
from typing import Dict, Optional
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from scripts.db_manager import DatabaseManager
from scripts.user_profile import UserProfileManager
from config.config import (
    DEFAULT_USER_ID,
    RDA_MALE,
    RDA_FEMALE,
    ATHLETE_MICRONUTRIENT_MULTIPLIERS
)

class NutritionCalculator(DatabaseManager):
    """Calculate nutrition targets and analyze progress."""

    def __init__(self):
        super().__init__()
        self.user_manager = UserProfileManager()

    def calculate_bmr(
        self,
        weight_lbs: float,
        height_inches: float,
        age: int,
        sex: str,
        body_fat_pct: Optional[float] = None
    ) -> int:
        """
        Calculate Basal Metabolic Rate.
        Uses Katch-McArdle if body fat % available, otherwise Mifflin-St Jeor.
        """

        if body_fat_pct:
            # Katch-McArdle (most accurate with body fat %)
            lean_mass_lbs = weight_lbs * (1 - body_fat_pct / 100)
            lean_mass_kg = lean_mass_lbs / 2.205
            bmr = 370 + (21.6 * lean_mass_kg)
        else:
            # Mifflin-St Jeor (without body fat %)
            weight_kg = weight_lbs / 2.205
            height_cm = height_inches * 2.54

            if sex == "male":
                bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
            else:
                bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161

        return int(bmr)

    def calculate_tdee(self, bmr: int, activity_level: str) -> int:
        """Calculate Total Daily Energy Expenditure."""

        multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'very_active': 1.725,
            'athlete': 1.9
        }

        return int(bmr * multipliers.get(activity_level, 1.55))

    def calculate_macro_targets(
        self,
        tdee: int,
        weight_lbs: float,
        goal_type: str,
        is_training_day: bool = False
    ) -> Dict:
        """Calculate macro targets based on TDEE and goals."""

        # Adjust calories for goal
        if goal_type == 'bulk':
            calories = tdee + 300
            protein_multiplier = 1.0
        elif goal_type == 'cut':
            calories = tdee - 500
            protein_multiplier = 1.2  # Higher protein to preserve muscle
        elif goal_type == 'recomp':
            calories = tdee
            protein_multiplier = 1.1
        else:  # maintain
            calories = tdee
            protein_multiplier = 0.8

        # Adjust for training day
        if is_training_day and goal_type != 'cut':
            calories += 150  # Extra carbs for training

        # Calculate macros
        protein_g = int(weight_lbs * protein_multiplier)
        protein_cals = protein_g * 4

        fat_g = int((calories * 0.30) / 9)  # 30% from fat
        fat_cals = fat_g * 9

        carbs_g = int((calories - protein_cals - fat_cals) / 4)

        # Fiber target
        fiber_g = int(14 * (calories / 1000))

        # Limits
        sugar_limit_g = int((calories * 0.10) / 4)  # < 10% from sugar
        saturated_fat_limit_g = int((calories * 0.10) / 9)  # < 10% from saturated fat

        return {
            'calories_target': calories,
            'protein_target_g': protein_g,
            'carbs_target_g': carbs_g,
            'fat_target_g': fat_g,
            'fiber_target_g': fiber_g,
            'sugar_limit_g': sugar_limit_g,
            'saturated_fat_limit_g': saturated_fat_limit_g,
            'sodium_limit_mg': 2300,
            'cholesterol_limit_mg': 300
        }

    def calculate_micronutrient_targets(
        self,
        sex: str,
        activity_level: str,
        training_days_per_week: int
    ) -> Dict:
        """Calculate micronutrient targets (top 10)."""

        # Get base RDA
        base_rda = RDA_MALE if sex == 'male' else RDA_FEMALE
        targets = base_rda.copy()

        # Adjust for athletes
        if activity_level in ['very_active', 'athlete'] or training_days_per_week >= 5:
            for nutrient, multiplier in ATHLETE_MICRONUTRIENT_MULTIPLIERS.items():
                if nutrient in targets:
                    targets[nutrient] = round(targets[nutrient] * multiplier, 1)

        # Return with _target suffix for database columns
        return {f"{key.replace('_mg', '').replace('_mcg', '').replace('_g', '')}_target_{key.split('_')[-1]}": value
                for key, value in targets.items()}

    def generate_daily_targets(
        self,
        user_id: int = DEFAULT_USER_ID,
        target_date: date = None,
        is_training_day: bool = False
    ) -> Dict:
        """Generate complete daily nutrition targets for a user."""

        if not target_date:
            target_date = date.today()

        # Get user profile
        user = self.user_manager.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Calculate BMR
        bmr = self.calculate_bmr(
            weight_lbs=user['weight_lbs'],
            height_inches=user['height_inches'],
            age=user['age'],
            sex=user['sex'],
            body_fat_pct=user.get('body_fat_pct')
        )

        # Calculate TDEE
        tdee = self.calculate_tdee(bmr, user['activity_level'])

        # Calculate macros
        macros = self.calculate_macro_targets(
            tdee=tdee,
            weight_lbs=user['weight_lbs'],
            goal_type=user['goal_type'],
            is_training_day=is_training_day
        )

        # Calculate micronutrients
        micros = self.calculate_micronutrient_targets(
            sex=user['sex'],
            activity_level=user['activity_level'],
            training_days_per_week=user['training_days_per_week']
        )

        # Combine everything
        targets = {
            'user_id': user_id,
            'date': target_date,
            'is_training_day': is_training_day,
            'goal_type': user['goal_type'],
            'tdee_kcal': tdee,
            **macros,
            **micros
        }

        return targets

    def save_daily_targets(
        self,
        targets: Dict,
        user_id: int = DEFAULT_USER_ID
    ) -> int:
        """Save daily targets to database."""

        # Check if targets already exist for this date
        existing = self.execute_single(
            "SELECT id FROM daily_nutrition_targets WHERE user_id = ? AND date = ?",
            (user_id, targets['date'])
        )

        if existing:
            # Update existing
            fields = ', '.join([f"{k} = ?" for k in targets.keys() if k not in ['user_id', 'date']])
            values = [v for k, v in targets.items() if k not in ['user_id', 'date']]
            values.extend([user_id, targets['date']])

            query = f"""
                UPDATE daily_nutrition_targets
                SET {fields}
                WHERE user_id = ? AND date = ?
            """
            self.execute_write(query, tuple(values))
            print(f"[SUCCESS] Daily targets updated for {targets['date']}")
            return existing['id']
        else:
            # Insert new
            columns = ', '.join(targets.keys())
            placeholders = ', '.join(['?' for _ in targets])

            query = f"""
                INSERT INTO daily_nutrition_targets ({columns})
                VALUES ({placeholders})
            """
            target_id = self.execute_write(query, tuple(targets.values()))
            print(f"[SUCCESS] Daily targets created for {targets['date']}")
            return target_id

    def get_daily_targets(
        self,
        user_id: int = DEFAULT_USER_ID,
        target_date: date = None
    ) -> Optional[Dict]:
        """Get nutrition targets for a specific date."""

        if not target_date:
            target_date = date.today()

        query = """
            SELECT * FROM daily_nutrition_targets
            WHERE user_id = ? AND date = ?
            ORDER BY created_at DESC
            LIMIT 1
        """

        return self.execute_single(query, (user_id, target_date))

    def get_or_create_daily_targets(
        self,
        user_id: int = DEFAULT_USER_ID,
        target_date: date = None,
        is_training_day: bool = False
    ) -> Dict:
        """Get targets for date, or generate if they don't exist."""

        if not target_date:
            target_date = date.today()

        targets = self.get_daily_targets(user_id, target_date)

        if not targets:
            # Generate and save new targets
            targets = self.generate_daily_targets(user_id, target_date, is_training_day)
            self.save_daily_targets(targets, user_id)
            targets = self.get_daily_targets(user_id, target_date)

        return targets

# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Nutrition Calculator")
    parser.add_argument('--generate', action='store_true', help='Generate today\'s targets')
    parser.add_argument('--view', action='store_true', help='View today\'s targets')
    parser.add_argument('--training-day', action='store_true', help='Mark as training day')
    parser.add_argument('--date', type=str, help='Target date (YYYY-MM-DD), default: today')

    args = parser.parse_args()

    calc = NutritionCalculator()

    # Parse date if provided
    target_date = None
    if args.date:
        target_date = date.fromisoformat(args.date)

    if args.generate:
        targets = calc.generate_daily_targets(
            target_date=target_date,
            is_training_day=args.training_day
        )
        calc.save_daily_targets(targets)
        print("\nDaily Targets Generated:")
        print("-" * 40)
        print(f"Date: {targets['date']}")
        print(f"Goal: {targets['goal_type']}")
        print(f"TDEE: {targets['tdee_kcal']} kcal")
        print(f"Training Day: {'Yes' if targets['is_training_day'] else 'No'}")
        print("\nMacronutrients:")
        print(f"  Calories: {targets['calories_target']} kcal")
        print(f"  Protein:  {targets['protein_target_g']}g")
        print(f"  Carbs:    {targets['carbs_target_g']}g")
        print(f"  Fat:      {targets['fat_target_g']}g")
        print(f"  Fiber:    {targets['fiber_target_g']}g")

    elif args.view:
        targets = calc.get_daily_targets(target_date=target_date)
        if targets:
            print("\nDaily Nutrition Targets:")
            print("-" * 40)
            print(f"Date: {targets['date']}")
            print(f"Goal: {targets['goal_type']}")
            print(f"TDEE: {targets['tdee_kcal']} kcal")
            print(f"Training Day: {'Yes' if targets['is_training_day'] else 'No'}")
            print("\nMacronutrients:")
            print(f"  Calories: {targets['calories_target']} kcal")
            print(f"  Protein:  {targets['protein_target_g']}g")
            print(f"  Carbs:    {targets['carbs_target_g']}g")
            print(f"  Fat:      {targets['fat_target_g']}g")
            print(f"  Fiber:    {targets['fiber_target_g']}g")
            print("\nLimits:")
            print(f"  Sugar:       < {targets['sugar_limit_g']}g")
            print(f"  Sat. Fat:    < {targets['saturated_fat_limit_g']}g")
            print(f"  Sodium:      < {targets['sodium_limit_mg']}mg")
            print(f"  Cholesterol: < {targets['cholesterol_limit_mg']}mg")

            # Show micronutrients if available
            micro_keys = ['vitamin_d_target_mcg', 'vitamin_c_target_mg', 'vitamin_a_target_mcg',
                         'calcium_target_mg', 'iron_target_mg', 'magnesium_target_mg',
                         'potassium_target_mg', 'zinc_target_mg', 'omega3_target_g']

            if any(targets.get(key) for key in micro_keys):
                print("\nMicronutrients:")
                if targets.get('vitamin_d_target_mcg'):
                    print(f"  Vitamin D:  {targets['vitamin_d_target_mcg']} mcg")
                if targets.get('vitamin_c_target_mg'):
                    print(f"  Vitamin C:  {targets['vitamin_c_target_mg']} mg")
                if targets.get('vitamin_a_target_mcg'):
                    print(f"  Vitamin A:  {targets['vitamin_a_target_mcg']} mcg")
                if targets.get('calcium_target_mg'):
                    print(f"  Calcium:    {targets['calcium_target_mg']} mg")
                if targets.get('iron_target_mg'):
                    print(f"  Iron:       {targets['iron_target_mg']} mg")
                if targets.get('magnesium_target_mg'):
                    print(f"  Magnesium:  {targets['magnesium_target_mg']} mg")
                if targets.get('potassium_target_mg'):
                    print(f"  Potassium:  {targets['potassium_target_mg']} mg")
                if targets.get('zinc_target_mg'):
                    print(f"  Zinc:       {targets['zinc_target_mg']} mg")
                if targets.get('omega3_target_g'):
                    print(f"  Omega-3:    {targets['omega3_target_g']} g")
        else:
            print(f"[ERROR] No targets found for {target_date or date.today()}. Use --generate to create them.")

    else:
        parser.print_help()
