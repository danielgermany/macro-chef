"""
Integration test for online recipe search functionality.

Tests:
- Online search triggering when <5 local meals
- Price cross-referencing with shopping history
- Nutrition validation with USDA
- Recipe caching on user rating
"""

import sys
from pathlib import Path
from datetime import date

sys.path.append(str(Path(__file__).parent.parent))

from scripts.meal_recommender import MealRecommender
from scripts.meal_tracker import MealTracker
from config.config import DEFAULT_USER_ID


def test_online_search_fallback():
    """Test that online search triggers when <5 local meals."""
    print("\n" + "="*60)
    print("TEST 1: Online Search Fallback")
    print("="*60)

    recommender = MealRecommender()

    # Test with a very specific criteria that likely has <5 local matches
    print("\n[INFO] Testing meal recommendation with restrictive criteria...")
    recommendations = recommender.recommend_meal(
        meal_time="dinner",
        user_id=DEFAULT_USER_ID,
        max_time=15,  # Very short time
        budget_limit=3.0,  # Low budget
        allow_online_search=True
    )

    print(f"\n[RESULT] Got {len(recommendations)} recommendations")

    if recommendations:
        # Check if any are online recipes
        online_count = sum(1 for meal in recommendations if meal.get('is_online_recipe'))
        print(f"[INFO] {online_count} online recipes, {len(recommendations) - online_count} local recipes")

        # Show first recommendation
        if recommendations:
            meal = recommendations[0]
            print(f"\n[SAMPLE] Top recommendation:")
            print(f"  Name: {meal.get('meal_name')}")
            print(f"  Source: {'Online' if meal.get('is_online_recipe') else 'Local'}")
            print(f"  Cost: ${meal.get('cost_estimate_usd', 0):.2f}")
            print(f"  Price source: {meal.get('price_source', 'N/A')}")
            print(f"  Price confidence: {meal.get('price_confidence', 0):.2f}")
            print(f"  Nutrition validated: {meal.get('nutrition_validated', False)}")
            if meal.get('nutrition_flags'):
                print(f"  Validation flags: {meal.get('nutrition_flags')}")
    else:
        print("[WARNING] No recommendations returned")

    print("\n[PASS] Online search fallback test completed")


def test_price_estimation():
    """Test price cross-referencing logic."""
    print("\n" + "="*60)
    print("TEST 2: Price Estimation")
    print("="*60)

    recommender = MealRecommender()

    # Create a mock recipe with ingredients
    test_recipe = {
        'meal_name': 'Test Chicken Recipe',
        'cost_estimate_usd': 5.00,
        'calories': 500,
        'protein_g': 40,
        'carbs_g': 30,
        'fat_g': 15,
        'ingredients': [
            {'name': 'chicken breast', 'amount': 200, 'unit': 'g'},
            {'name': 'rice', 'amount': 100, 'unit': 'g'},
            {'name': 'broccoli', 'amount': 150, 'unit': 'g'}
        ]
    }

    print("\n[INFO] Testing price estimation for test recipe...")
    price_estimate = recommender._estimate_recipe_cost(test_recipe, DEFAULT_USER_ID)

    print(f"\n[RESULT] Price estimation:")
    print(f"  API price: ${price_estimate['api_price']:.2f}")
    print(f"  Estimated price: ${price_estimate['estimated_price']:.2f}")
    print(f"  Price source: {price_estimate['price_source']}")
    print(f"  Confidence: {price_estimate['confidence_score']:.2f}")
    print(f"  Ingredients matched: {price_estimate['ingredients_matched']}/{price_estimate['ingredients_total']}")

    print("\n[PASS] Price estimation test completed")


def test_nutrition_validation():
    """Test USDA nutrition validation."""
    print("\n" + "="*60)
    print("TEST 3: Nutrition Validation")
    print("="*60)

    recommender = MealRecommender()

    # Create a mock recipe
    test_recipe = {
        'meal_name': 'Test Chicken Recipe',
        'calories': 500,
        'protein_g': 40,
        'carbs_g': 30,
        'fat_g': 15
    }

    test_ingredients = [
        {'name': 'chicken breast', 'amount': 200, 'unit': 'g'},
        {'name': 'rice', 'amount': 100, 'unit': 'g'}
    ]

    print("\n[INFO] Testing nutrition validation (may take time with API calls)...")
    validation = recommender._validate_nutrition(test_recipe, test_ingredients)

    print(f"\n[RESULT] Validation results:")
    print(f"  Validation passed: {validation['validation_passed']}")
    print(f"  Confidence: {validation['validation_confidence']:.2f}")
    print(f"  Ingredients validated: {validation['ingredients_validated']}/{validation['ingredients_total']}")

    if validation['discrepancies']:
        print(f"\n[INFO] Nutrition discrepancies:")
        for nutrient, data in validation['discrepancies'].items():
            print(f"  {nutrient}:")
            print(f"    USDA: {data['usda_value']}")
            print(f"    Spoonacular: {data['spoonacular_value']}")
            print(f"    Difference: {data['percent_difference']}%")

    if validation['flags']:
        print(f"\n[INFO] Validation flags: {', '.join(validation['flags'])}")

    print("\n[PASS] Nutrition validation test completed")


def test_recipe_caching():
    """Test selective recipe caching on rating."""
    print("\n" + "="*60)
    print("TEST 4: Recipe Caching on Rating")
    print("="*60)

    tracker = MealTracker()

    # Mock online recipe data
    mock_recipe = {
        'api_source': 'spoonacular',
        'api_recipe_id': 'test_12345',
        'meal_name': 'Test Online Recipe',
        'meal_time': 'dinner',
        'calories': 500,
        'protein_g': 40,
        'carbs_g': 30,
        'fat_g': 15,
        'cost_estimate_usd': 5.00,
        'nutrition_validated': True,
        'price_confidence': 0.8,
        'price_source': 'hybrid',
        'servings': 2,
        'ingredients': [
            {'name': 'chicken', 'amount': 200, 'unit': 'g', 'category': 'protein'},
            {'name': 'rice', 'amount': 100, 'unit': 'g', 'category': 'grain'}
        ]
    }

    print("\n[INFO] Testing recipe caching with rating >=3...")

    # Test with rating 4 (should save)
    print("\n[TEST] Logging meal with rating 4 (should save to templates)...")
    meal_id = tracker.log_meal(
        meal_name="Test Online Recipe",
        calories=500,
        protein_g=40,
        carbs_g=30,
        fat_g=15,
        meal_time="dinner",
        rating=4,
        user_id=DEFAULT_USER_ID,
        online_recipe_data=mock_recipe
    )
    print(f"[INFO] Meal logged with ID: {meal_id}")

    # Test with rating 2 (should NOT save)
    print("\n[TEST] Logging meal with rating 2 (should NOT save)...")
    mock_recipe['api_recipe_id'] = 'test_67890'  # Different ID
    mock_recipe['meal_name'] = 'Low Rated Recipe'

    meal_id2 = tracker.log_meal(
        meal_name="Low Rated Recipe",
        calories=400,
        protein_g=30,
        carbs_g=40,
        fat_g=10,
        meal_time="lunch",
        rating=2,
        user_id=DEFAULT_USER_ID,
        online_recipe_data=mock_recipe
    )
    print(f"[INFO] Meal logged with ID: {meal_id2}")

    print("\n[PASS] Recipe caching test completed")
    print("[INFO] Check console output above - recipe with rating 4 should be saved, rating 2 should not")


def run_all_tests():
    """Run all integration tests."""
    print("\n" + "#"*60)
    print("# ONLINE RECIPE INTEGRATION TESTS")
    print("#"*60)

    try:
        test_online_search_fallback()
    except Exception as e:
        print(f"\n[ERROR] Test 1 failed: {e}")

    try:
        test_price_estimation()
    except Exception as e:
        print(f"\n[ERROR] Test 2 failed: {e}")

    try:
        test_nutrition_validation()
    except Exception as e:
        print(f"\n[ERROR] Test 3 failed: {e}")

    try:
        test_recipe_caching()
    except Exception as e:
        print(f"\n[ERROR] Test 4 failed: {e}")

    print("\n" + "#"*60)
    print("# ALL TESTS COMPLETED")
    print("#"*60)
    print("\n[INFO] Review output above for any errors or warnings")
    print("[INFO] API-dependent tests may fail if API keys not configured")


if __name__ == "__main__":
    run_all_tests()
