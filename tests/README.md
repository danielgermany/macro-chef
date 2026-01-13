# Test Suite for Macro Chef

Comprehensive unit tests for the meal planning system covering database operations, nutrition calculations, and API integrations.

## Test Files

### `test_database.py`
Tests database initialization and operations:
- Database schema creation (13 tables)
- CRUD operations for user profiles and inventory
- Foreign key constraints and cascading deletes
- Data integrity and uniqueness constraints
- Index creation for performance

### `test_nutrition.py`
Tests nutrition calculation logic:
- BMR calculations (Katch-McArdle and Mifflin-St Jeor formulas)
- TDEE calculations for different activity levels
- Macro target calculations for bulk/cut/maintain/recomp
- Training day adjustments
- Micronutrient RDA calculations (male/female/athlete)
- Validation of calculation edge cases

### `test_api.py`
Tests API integrations and caching:
- Spoonacular API recipe search and nutrition lookup
- USDA FoodData Central integration
- API error handling (timeouts, quota exceeded, invalid keys)
- Retry logic for failed requests
- Nutrition data caching in database
- Mock tests (run without API keys)
- Live tests (only run when API keys configured)

## Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_database.py -v
pytest tests/test_nutrition.py -v
pytest tests/test_api.py -v
```

### Run Specific Test Class
```bash
pytest tests/test_database.py::TestDatabaseSetup -v
pytest tests/test_nutrition.py::TestBMRCalculations -v
pytest tests/test_api.py::TestSpoonacularAPI -v
```

### Run Specific Test Function
```bash
pytest tests/test_database.py::TestDatabaseSetup::test_all_tables_created -v
pytest tests/test_nutrition.py::TestBMRCalculations::test_bmr_katch_mcardle_male -v
```

### Run with Coverage Report
```bash
pytest tests/ --cov=scripts --cov-report=html
```

Then open `htmlcov/index.html` in your browser to see detailed coverage.

### Run Tests in Parallel (faster)
```bash
pip install pytest-xdist
pytest tests/ -v -n auto
```

## Test Configuration

### Mock Tests vs Live Tests

By default, API tests use mocked responses and don't require API keys. To run live API tests:

1. Set up your `.env` file with API keys:
```bash
SPOONACULAR_API_KEY=your_key_here
USDA_API_KEY=your_key_here  # Optional
```

2. Run tests with live API enabled:
```bash
pytest tests/test_api.py -v
```

Live tests are automatically skipped if API keys are not configured.

### Temporary Test Database

All tests use temporary SQLite databases that are:
- Created fresh for each test
- Isolated from your production database
- Automatically deleted after tests complete

Your actual `database/meal_planner.db` is never touched during testing.

## Test Coverage

Current test coverage includes:

**Database Layer:**
-  Schema creation and validation
-  User profile management
-  Inventory operations
-  Foreign key constraints
-  Data integrity checks

**Nutrition Logic:**
-  BMR/TDEE calculations
-  Macro distribution algorithms
-  Micronutrient RDA calculations
-  Training day adjustments
-  Edge case validation

**API Integration:**
-  Spoonacular recipe search
-  USDA nutrition lookup
-  Error handling and retries
-  Response caching
-  Rate limiting awareness

## Continuous Integration

To set up CI/CD with GitHub Actions:

1. Create `.github/workflows/tests.yml`:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: pytest tests/ -v --cov=scripts
```

## Troubleshooting

### Import Errors
If you get import errors, ensure you're running tests from the project root:
```bash
cd /path/to/macro-chef
pytest tests/ -v
```

### Database Locked Errors
If tests fail with "database is locked" errors, ensure no other process is accessing the test database. Tests use temporary databases to avoid this.

### API Test Failures
If API tests fail:
1. Check your internet connection
2. Verify API keys are correct in `.env`
3. Check if you've exceeded API rate limits
4. Mock tests should always pass without API keys

## Adding New Tests

When adding new functionality, follow these patterns:

1. **Create test fixtures** for reusable setup (e.g., `temp_db`, `mock_api`)
2. **Use descriptive test names** that explain what is being tested
3. **Test both success and failure cases**
4. **Mock external dependencies** (APIs, file I/O) for unit tests
5. **Use assertions** that provide clear failure messages

Example:
```python
def test_feature_name(self, temp_db, monkeypatch):
    """Test that feature works correctly with valid input."""
    # Arrange
    setup_test_data()

    # Act
    result = function_under_test()

    # Assert
    assert result == expected_value
    assert some_condition is True
```

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)
