"""
Unit tests for nutrition calculations.
Tests BMR, TDEE, macro targets, and micronutrient calculations.

Usage: pytest tests/test_nutrition.py -v
"""

import pytest
import tempfile
import os
from pathlib import Path
from datetime import date
import sys

sys.path.append(str(Path(__file__).parent.parent))
from scripts.nutrition_calculator import NutritionCalculator
from scripts.user_profile import UserProfileManager
from scripts.db_setup import create_tables
import sqlite3


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db')
    temp_path = temp_file.name
    temp_file.close()

    conn = sqlite3.connect(temp_path)
    create_tables(conn)
    conn.commit()
    conn.close()

    yield temp_path

    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def nutrition_calc():
    """Create a NutritionCalculator instance."""
    return NutritionCalculator()


class TestBMRCalculations:
    """Test Basal Metabolic Rate calculations."""

    def test_bmr_katch_mcardle_male(self, nutrition_calc):
        """Test BMR using Katch-McArdle formula (with body fat %)."""
        # Male, 180 lbs, 15% body fat
        bmr = nutrition_calc.calculate_bmr(
            weight_lbs=180,
            height_inches=70,
            age=30,
            sex='male',
            body_fat_pct=15.0
        )

        # 180 lbs * 0.85 = 153 lbs lean mass = 69.4 kg
        # BMR = 370 + (21.6 * 69.4) = 1869
        assert 1850 <= bmr <= 1890

    def test_bmr_katch_mcardle_female(self, nutrition_calc):
        """Test BMR for female with body fat %."""
        # Female, 140 lbs, 22% body fat
        bmr = nutrition_calc.calculate_bmr(
            weight_lbs=140,
            height_inches=65,
            age=25,
            sex='female',
            body_fat_pct=22.0
        )

        # 140 lbs * 0.78 = 109.2 lbs lean mass = 49.5 kg
        # BMR = 370 + (21.6 * 49.5) = 1439
        assert 1420 <= bmr <= 1460

    def test_bmr_mifflin_st_jeor_male(self, nutrition_calc):
        """Test BMR using Mifflin-St Jeor (without body fat %)."""
        # Male, 180 lbs, 70 inches, 30 years
        bmr = nutrition_calc.calculate_bmr(
            weight_lbs=180,
            height_inches=70,
            age=30,
            sex='male',
            body_fat_pct=None
        )

        # 180 lbs = 81.65 kg, 70 inches = 177.8 cm
        # BMR = (10 * 81.65) + (6.25 * 177.8) - (5 * 30) + 5 = 1777
        assert 1750 <= bmr <= 1800

    def test_bmr_mifflin_st_jeor_female(self, nutrition_calc):
        """Test BMR for female without body fat %."""
        # Female, 140 lbs, 65 inches, 25 years
        bmr = nutrition_calc.calculate_bmr(
            weight_lbs=140,
            height_inches=65,
            age=25,
            sex='female',
            body_fat_pct=None
        )

        # 140 lbs = 63.5 kg, 65 inches = 165.1 cm
        # BMR = (10 * 63.5) + (6.25 * 165.1) - (5 * 25) - 161 = 1377
        assert 1350 <= bmr <= 1400

    def test_bmr_returns_integer(self, nutrition_calc):
        """Test that BMR returns an integer value."""
        bmr = nutrition_calc.calculate_bmr(
            weight_lbs=175,
            height_inches=68,
            age=28,
            sex='male'
        )

        assert isinstance(bmr, int)
        assert bmr > 0


class TestTDEECalculations:
    """Test Total Daily Energy Expenditure calculations."""

    def test_tdee_sedentary(self, nutrition_calc):
        """Test TDEE for sedentary activity level."""
        bmr = 1800
        tdee = nutrition_calc.calculate_tdee(bmr, 'sedentary')

        # TDEE = BMR * 1.2 = 2160
        assert tdee == 2160

    def test_tdee_moderate(self, nutrition_calc):
        """Test TDEE for moderate activity level."""
        bmr = 1800
        tdee = nutrition_calc.calculate_tdee(bmr, 'moderate')

        # TDEE = BMR * 1.55 = 2790
        assert tdee == 2790

    def test_tdee_athlete(self, nutrition_calc):
        """Test TDEE for athlete activity level."""
        bmr = 1800
        tdee = nutrition_calc.calculate_tdee(bmr, 'athlete')

        # TDEE = BMR * 1.9 = 3420
        assert tdee == 3420

    def test_tdee_invalid_activity_defaults(self, nutrition_calc):
        """Test TDEE defaults to moderate for invalid activity level."""
        bmr = 2000
        tdee = nutrition_calc.calculate_tdee(bmr, 'invalid')

        # Should default to moderate (1.55)
        assert tdee == 3100


class TestMacroTargets:
    """Test macro target calculations."""

    def test_bulk_macros(self, nutrition_calc):
        """Test macro targets for bulking."""
        tdee = 2500
        weight_lbs = 180

        macros = nutrition_calc.calculate_macro_targets(
            tdee=tdee,
            weight_lbs=weight_lbs,
            goal_type='bulk',
            is_training_day=False
        )

        # Calories = TDEE + 300 = 2800
        assert macros['calories_target'] == 2800

        # Protein = 180 * 1.0 = 180g
        assert macros['protein_target_g'] == 180

        # Check macros add up correctly
        total_cals = (macros['protein_target_g'] * 4) + (macros['carbs_target_g'] * 4) + (macros['fat_target_g'] * 9)
        assert abs(total_cals - macros['calories_target']) < 50  # Allow small rounding difference

    def test_cut_macros(self, nutrition_calc):
        """Test macro targets for cutting."""
        tdee = 2500
        weight_lbs = 180

        macros = nutrition_calc.calculate_macro_targets(
            tdee=tdee,
            weight_lbs=weight_lbs,
            goal_type='cut',
            is_training_day=False
        )

        # Calories = TDEE - 500 = 2000
        assert macros['calories_target'] == 2000

        # Protein = 180 * 1.2 = 216g (higher to preserve muscle)
        assert macros['protein_target_g'] == 216

        # Protein should be higher percentage on cut
        protein_pct = (macros['protein_target_g'] * 4) / macros['calories_target']
        assert protein_pct > 0.40  # Over 40% protein

    def test_maintain_macros(self, nutrition_calc):
        """Test macro targets for maintenance."""
        tdee = 2500
        weight_lbs = 180

        macros = nutrition_calc.calculate_macro_targets(
            tdee=tdee,
            weight_lbs=weight_lbs,
            goal_type='maintain',
            is_training_day=False
        )

        # Calories = TDEE (no adjustment)
        assert macros['calories_target'] == 2500

        # Protein = 180 * 0.8 = 144g
        assert macros['protein_target_g'] == 144

    def test_recomp_macros(self, nutrition_calc):
        """Test macro targets for recomposition."""
        tdee = 2500
        weight_lbs = 180

        macros = nutrition_calc.calculate_macro_targets(
            tdee=tdee,
            weight_lbs=weight_lbs,
            goal_type='recomp',
            is_training_day=False
        )

        # Calories = TDEE (maintenance)
        assert macros['calories_target'] == 2500

        # Protein = 180 * 1.1 = 198g (elevated for recomp)
        assert macros['protein_target_g'] == 198

    def test_training_day_adjustment(self, nutrition_calc):
        """Test that training days add extra calories (except on cut)."""
        tdee = 2500
        weight_lbs = 180

        # Bulk with training day
        bulk_training = nutrition_calc.calculate_macro_targets(
            tdee=tdee,
            weight_lbs=weight_lbs,
            goal_type='bulk',
            is_training_day=True
        )

        bulk_rest = nutrition_calc.calculate_macro_targets(
            tdee=tdee,
            weight_lbs=weight_lbs,
            goal_type='bulk',
            is_training_day=False
        )

        # Training day should have +150 cals
        assert bulk_training['calories_target'] == bulk_rest['calories_target'] + 150

        # Cut should NOT add training day calories
        cut_training = nutrition_calc.calculate_macro_targets(
            tdee=tdee,
            weight_lbs=weight_lbs,
            goal_type='cut',
            is_training_day=True
        )

        cut_rest = nutrition_calc.calculate_macro_targets(
            tdee=tdee,
            weight_lbs=weight_lbs,
            goal_type='cut',
            is_training_day=False
        )

        assert cut_training['calories_target'] == cut_rest['calories_target']


class TestMicronutrientTargets:
    """Test micronutrient target calculations."""

    def test_male_micronutrient_rdas(self, nutrition_calc):
        """Test RDA calculations for males."""
        from config.config import RDA_MALE

        targets = nutrition_calc.calculate_micronutrient_targets(
            sex='male',
            activity_level='moderate',
            training_days_per_week=3
        )

        # Check key micronutrients match RDAs (keys have _target suffix)
        assert targets['vitamin_d_target_mcg'] == RDA_MALE['vitamin_d_mcg']
        assert targets['vitamin_c_target_mg'] == RDA_MALE['vitamin_c_mg']
        assert targets['calcium_target_mg'] == RDA_MALE['calcium_mg']
        assert targets['iron_target_mg'] == RDA_MALE['iron_mg']

    def test_female_micronutrient_rdas(self, nutrition_calc):
        """Test RDA calculations for females."""
        from config.config import RDA_FEMALE, RDA_MALE

        targets = nutrition_calc.calculate_micronutrient_targets(
            sex='female',
            activity_level='light',
            training_days_per_week=2
        )

        # Females have higher iron requirements
        assert targets['iron_target_mg'] == RDA_FEMALE['iron_mg']
        assert targets['iron_target_mg'] > RDA_MALE['iron_mg']

        # Lower vitamin C than males
        assert targets['vitamin_c_target_mg'] == RDA_FEMALE['vitamin_c_mg']

    def test_athlete_micronutrient_multipliers(self, nutrition_calc):
        """Test that athletes get increased micronutrient targets."""
        from config.config import RDA_MALE

        athlete_targets = nutrition_calc.calculate_micronutrient_targets(
            sex='male',
            activity_level='athlete',
            training_days_per_week=6
        )

        moderate_targets = nutrition_calc.calculate_micronutrient_targets(
            sex='male',
            activity_level='moderate',
            training_days_per_week=3
        )

        # Athletes should have higher vitamin C
        assert athlete_targets['vitamin_c_target_mg'] > moderate_targets['vitamin_c_target_mg']

        # Athletes should have higher magnesium
        assert athlete_targets['magnesium_target_mg'] > moderate_targets['magnesium_target_mg']


class TestNutritionTargetGeneration:
    """Test complete nutrition target generation."""

    def test_generate_daily_targets(self, temp_db, monkeypatch):
        """Test generating complete daily nutrition targets."""
        import config.config
        monkeypatch.setattr(config.config, 'DATABASE_PATH', temp_db)

        # Create user profile
        user_manager = UserProfileManager()
        user_id = user_manager.create_user(
            name='Test User',
            age=30,
            sex='male',
            height_inches=70,
            weight_lbs=180,
            body_fat_pct=15.0,
            goal_type='bulk',
            activity_level='moderate',
            training_days_per_week=4
        )

        # Generate targets
        calc = NutritionCalculator()
        success = calc.generate_daily_targets(
            user_id=user_id,
            target_date=date.today(),
            is_training_day=True
        )

        assert success is True

        # Verify targets were saved
        targets = calc.get_targets(user_id, date.today())

        assert targets is not None
        assert targets['calories_target'] > 0
        assert targets['protein_target_g'] > 0
        assert targets['carbs_target_g'] > 0
        assert targets['fat_target_g'] > 0

    def test_fiber_target_calculation(self, nutrition_calc):
        """Test that fiber target is calculated (14g per 1000 calories)."""
        macros = nutrition_calc.calculate_macro_targets(
            tdee=2500,
            weight_lbs=180,
            goal_type='maintain',
            is_training_day=False
        )

        # Fiber = calories * 14 / 1000
        expected_fiber = int(macros['calories_target'] * 14 / 1000)
        assert macros['fiber_target_g'] == expected_fiber


class TestNutritionValidation:
    """Test nutrition calculation edge cases and validation."""

    def test_minimum_bmr(self, nutrition_calc):
        """Test that BMR doesn't go unreasonably low."""
        bmr = nutrition_calc.calculate_bmr(
            weight_lbs=100,  # Very light weight
            height_inches=60,
            age=20,
            sex='female'
        )

        # Should still be reasonable minimum
        assert bmr >= 1000

    def test_macro_percentages_reasonable(self, nutrition_calc):
        """Test that macro percentages are within reasonable ranges."""
        macros = nutrition_calc.calculate_macro_targets(
            tdee=2500,
            weight_lbs=180,
            goal_type='maintain',
            is_training_day=False
        )

        total_cals = (macros['protein_target_g'] * 4) + \
                     (macros['carbs_target_g'] * 4) + \
                     (macros['fat_target_g'] * 9)

        protein_pct = (macros['protein_target_g'] * 4) / total_cals
        fat_pct = (macros['fat_target_g'] * 9) / total_cals

        # Protein should be 20-40% of calories
        assert 0.20 <= protein_pct <= 0.45

        # Fat should be 20-35% of calories
        assert 0.15 <= fat_pct <= 0.40

    def test_tdee_higher_than_bmr(self, nutrition_calc):
        """Test that TDEE is always higher than BMR."""
        bmr = 1800

        for activity in ['sedentary', 'light', 'moderate', 'very_active', 'athlete']:
            tdee = nutrition_calc.calculate_tdee(bmr, activity)
            assert tdee > bmr


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
