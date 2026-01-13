# Online Recipe Search with Cross-Referencing

## Overview

The meal recommendation system now intelligently falls back to online recipe search when the local database has insufficient meal options (<5 meals). Online recipes are cross-referenced with your shopping history for realistic pricing and validated with USDA nutrition data for accuracy.

## Features

### 1. **Intelligent Fallback Search**
- Automatically triggers when local database has <5 suitable meals
- Searches Spoonacular API with dietary restrictions and macro filters
- Seamlessly integrates online recipes into recommendation scoring
- Gracefully degrades if API unavailable

### 2. **Price Cross-Referencing**
- Compares Spoonacular prices with your shopping history (last 90 days)
- Uses hybrid calculation: 70% shopping history + 30% API when ingredients matched
- Provides confidence score (0.0-1.0) based on ingredient match rate
- Falls back to API price if no shopping history available

### 3. **Nutrition Validation**
- Cross-validates Spoonacular nutrition with USDA database
- Validates at ingredient level for accuracy
- Flags discrepancies >10% for review
- Provides validation confidence score

### 4. **Selective Recipe Caching**
- Saves online recipes to database only when you rate them ≥3 stars
- Prevents duplicates by checking API recipe ID
- Saves complete recipe with ingredients
- Cached recipes appear in future recommendations as local meals

## Database Changes

Added 5 new columns to `meal_templates` table:
- `api_source` - Source API (e.g., 'spoonacular')
- `api_recipe_id` - External recipe ID for duplicate detection
- `nutrition_validated` - Boolean flag for USDA validation
- `price_confidence` - Price estimate confidence (0.0-1.0)
- `price_source` - Price source: 'spoonacular', 'shopping_history', 'hybrid'

## Usage

### Automatic Usage
Online search happens automatically when using `meal_recommender.py`:

```bash
python scripts/meal_recommender.py --recommend dinner --count 5
```

If local database has <5 dinners, the system will automatically search online.

### Disable Online Search
```python
from scripts.meal_recommender import MealRecommender

recommender = MealRecommender()
meals = recommender.recommend_meal(
    meal_time="dinner",
    allow_online_search=False  # Only search locally
)
```

### View Online Recipe Indicators
Online recipes display in recommendations with:
- "New recipe from online search" indicator
- Price source and confidence
- Nutrition validation status

### Save Recipes You Like
When logging a meal from an online recipe:

```python
from scripts.meal_tracker import MealTracker

tracker = MealTracker()
tracker.log_meal(
    meal_name="Spicy Chicken Stir Fry",
    calories=450,
    protein_g=40,
    carbs_g=35,
    fat_g=15,
    meal_time="dinner",
    rating=4,  # Rating ≥3 saves to database
    online_recipe_data=meal_dict  # Pass the online recipe data
)
```

## Configuration

### Required
- **Spoonacular API Key**: Get free key at https://spoonacular.com/food-api
- Add to `.env` file: `SPOONACULAR_API_KEY=your_key_here`

### Optional
- **USDA API Key**: For nutrition validation (has public access without key)
- Add to `.env` file: `USDA_API_KEY=your_key_here`

## Error Handling

The system handles all failure modes gracefully:

| Scenario | Behavior |
|----------|----------|
| No API key configured | Skip online search, use local only |
| API quota exceeded | Fall back to local recipes |
| API request fails | Continue with local results |
| No shopping history | Use Spoonacular price only (low confidence) |
| USDA validation fails | Mark as unvalidated, use Spoonacular nutrition |

## Performance

- **Caching**: API responses cached in `food_nutrition_cache` table
- **Query optimization**: Added indexes on `api_source` and `api_recipe_id`
- **Lazy loading**: Online search only when needed

## Testing

Run integration tests:

```bash
python scripts/test_online_recipe_integration.py
```

Tests cover:
1. Online search fallback triggering
2. Price cross-referencing with shopping history
3. USDA nutrition validation
4. Selective recipe caching on rating

## Migration

Existing databases are automatically migrated:

```bash
python scripts/migrate_add_online_recipe_support.py
```

Adds 5 new columns and 2 indexes. Safe to run multiple times (idempotent).

## Files Modified

1. `scripts/db_setup.py` - Added 5 columns and 2 indexes to meal_templates
2. `scripts/meal_recommender.py` - Added online search, price estimation, nutrition validation (~450 lines)
3. `scripts/meal_tracker.py` - Added selective recipe caching (~120 lines)
4. `scripts/migrate_add_online_recipe_support.py` - Database migration script (new)
5. `scripts/test_online_recipe_integration.py` - Integration tests (new)

## Backward Compatibility

 Fully backward compatible:
- New columns are nullable
- Online search is opt-in (enabled by default, can disable)
- Existing meal recommendations work unchanged
- No breaking changes to method signatures

## Future Enhancements

- [ ] User preference to auto-save all online recipes
- [ ] Batch import from recipe URLs
- [ ] Multiple API source support (Edamam, USDA, etc.)
- [ ] Price tracking over time
- [ ] Nutrition validation reports

## Example Workflow

1. User requests dinner recommendations with tight budget constraint
2. System finds only 2 local meals matching criteria
3. Automatically searches Spoonacular for additional options
4. Cross-references prices with user's shopping history (hybrid pricing)
5. Validates nutrition with USDA database
6. Returns 8 total recommendations (2 local + 6 online)
7. User tries "Thai Chicken Bowl" (online recipe) and rates it 4 stars
8. Recipe automatically saved to local database with hybrid price
9. Next time, "Thai Chicken Bowl" appears as local recommendation

---

**Implementation Date**: December 31, 2025
**Version**: 1.0
**Status**: Production Ready
