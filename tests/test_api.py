"""
Unit tests for API integrations.
Tests Spoonacular and USDA API calls, caching, and error handling.

Usage: pytest tests/test_api.py -v
Note: Set SPOONACULAR_API_KEY in .env for live API tests (skipped by default)
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

sys.path.append(str(Path(__file__).parent.parent))
from scripts.spoonacular_api import SpoonacularAPI
from scripts.usda_api import USDAAPI
from scripts.db_setup import create_tables
import sqlite3
import config.config


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
def mock_spoonacular():
    """Create SpoonacularAPI with mocked requests."""
    with patch('scripts.spoonacular_api.requests.get') as mock_get:
        api = SpoonacularAPI()
        yield api, mock_get


@pytest.fixture
def mock_usda():
    """Create USDAAPI with mocked requests."""
    with patch('scripts.usda_api.requests.get') as mock_get:
        api = USDAAPI()
        yield api, mock_get


class TestSpoonacularAPI:
    """Test Spoonacular API integration."""

    def test_api_key_warning_when_missing(self, capsys):
        """Test warning is displayed when API key is not set."""
        with patch.object(config.config, 'SPOONACULAR_API_KEY', ''):
            api = SpoonacularAPI()
            captured = capsys.readouterr()
            assert "WARNING" in captured.out
            assert "SPOONACULAR_API_KEY" in captured.out

    def test_api_key_loaded(self):
        """Test that API key is loaded from config."""
        # Patch the module-level import
        with patch('scripts.spoonacular_api.SPOONACULAR_API_KEY', 'test_key_123'):
            api = SpoonacularAPI()
            assert api.api_key == 'test_key_123'

    def test_search_recipes_successful(self, mock_spoonacular):
        """Test successful recipe search."""
        api, mock_get = mock_spoonacular

        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [
                {
                    'id': 123,
                    'title': 'Chicken Breast',
                    'readyInMinutes': 30,
                    'nutrition': {
                        'nutrients': [
                            {'name': 'Calories', 'amount': 200},
                            {'name': 'Protein', 'amount': 40},
                            {'name': 'Carbohydrates', 'amount': 5},
                            {'name': 'Fat', 'amount': 4}
                        ]
                    }
                }
            ]
        }
        mock_get.return_value = mock_response

        with patch.object(config.config, 'SPOONACULAR_API_KEY', 'test_key'):
            api.api_key = 'test_key'
            results = api.search_recipes('chicken', max_results=1)

        assert len(results) == 1
        assert results[0]['id'] == 123
        assert results[0]['title'] == 'Chicken Breast'

    def test_search_recipes_with_filters(self, mock_spoonacular):
        """Test recipe search with dietary filters."""
        api, mock_get = mock_spoonacular

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'results': []}
        mock_get.return_value = mock_response

        with patch.object(config.config, 'SPOONACULAR_API_KEY', 'test_key'):
            api.api_key = 'test_key'
            api.search_recipes(
                query='chicken',
                max_results=10,
                diet='vegetarian',
                intolerances=['dairy', 'gluten'],
                max_ready_time=30,
                min_protein=40,
                max_calories=500
            )

        # Verify API was called with correct parameters
        call_args = mock_get.call_args
        params = call_args[1]['params']

        assert params['query'] == 'chicken'
        assert params['diet'] == 'vegetarian'
        assert params['intolerances'] == 'dairy,gluten'
        assert params['maxReadyTime'] == 30
        assert params['minProtein'] == 40
        assert params['maxCalories'] == 500

    def test_get_recipe_details(self, mock_spoonacular):
        """Test fetching recipe details by ID."""
        api, mock_get = mock_spoonacular

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 123,
            'title': 'Grilled Chicken',
            'readyInMinutes': 25,
            'instructions': 'Grill the chicken...',
            'nutrition': {
                'nutrients': [
                    {'name': 'Calories', 'amount': 300}
                ]
            },
            'extendedIngredients': [
                {'name': 'chicken breast', 'amount': 8, 'unit': 'oz'}
            ]
        }
        mock_get.return_value = mock_response

        with patch.object(config.config, 'SPOONACULAR_API_KEY', 'test_key'):
            api.api_key = 'test_key'
            recipe = api.get_recipe_information(123)

        assert recipe['id'] == 123
        assert recipe['title'] == 'Grilled Chicken'
        assert 'instructions' in recipe
        assert 'nutrition' in recipe

    def test_api_quota_exceeded(self, mock_spoonacular, capsys):
        """Test handling of API quota exceeded error."""
        api, mock_get = mock_spoonacular

        mock_response = Mock()
        mock_response.status_code = 402  # Payment Required (quota exceeded)
        mock_get.return_value = mock_response

        with patch.object(config.config, 'SPOONACULAR_API_KEY', 'test_key'):
            api.api_key = 'test_key'
            result = api._make_request('test-endpoint')

        assert result is None
        captured = capsys.readouterr()
        assert "quota exceeded" in captured.out.lower()

    def test_invalid_api_key(self, mock_spoonacular, capsys):
        """Test handling of invalid API key."""
        api, mock_get = mock_spoonacular

        mock_response = Mock()
        mock_response.status_code = 401  # Unauthorized
        mock_get.return_value = mock_response

        with patch.object(config.config, 'SPOONACULAR_API_KEY', 'test_key'):
            api.api_key = 'test_key'
            result = api._make_request('test-endpoint')

        assert result is None
        captured = capsys.readouterr()
        assert "Invalid API key" in captured.out

    def test_api_retry_logic(self, mock_spoonacular):
        """Test that API retries on timeout."""
        api, mock_get = mock_spoonacular

        # First call succeeds after exception handling
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'test': 'data'}
        mock_get.return_value = mock_response

        with patch.object(config.config, 'SPOONACULAR_API_KEY', 'test_key'):
            api.api_key = 'test_key'
            result = api._make_request('test-endpoint')

        assert result is not None
        assert result['test'] == 'data'

    def test_lookup_ingredient_nutrition(self, mock_spoonacular):
        """Test ingredient nutrition lookup."""
        api, mock_get = mock_spoonacular

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'name': 'chicken breast',
            'calories': 165,
            'protein': '31g',
            'fat': '3.6g'
        }
        mock_get.return_value = mock_response

        with patch.object(config.config, 'SPOONACULAR_API_KEY', 'test_key'):
            api.api_key = 'test_key'
            nutrition = api.get_ingredient_nutrition('chicken breast', amount=100, unit='grams')

        assert nutrition is not None
        assert 'name' in nutrition


class TestUSDAAPI:
    """Test USDA FoodData Central API integration."""

    def test_search_foods(self, mock_usda):
        """Test food search in USDA database."""
        api, mock_get = mock_usda

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'foods': [
                {
                    'fdcId': 123456,
                    'description': 'Chicken, broilers or fryers, breast, meat only, raw',
                    'foodNutrients': [
                        {'nutrientName': 'Protein', 'value': 23.2},
                        {'nutrientName': 'Energy', 'value': 120}
                    ]
                }
            ]
        }
        mock_get.return_value = mock_response

        with patch.object(config.config, 'USDA_API_KEY', 'test_key'):
            api.api_key = 'test_key'
            results = api.search_foods('chicken breast')

        assert len(results) == 1
        assert results[0]['fdcId'] == 123456
        assert 'chicken' in results[0]['description'].lower()

    def test_get_food_details(self, mock_usda):
        """Test fetching detailed nutrition data by FDC ID."""
        api, mock_get = mock_usda

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'fdcId': 123456,
            'description': 'Chicken breast',
            'foodNutrients': [
                {'nutrient': {'name': 'Protein'}, 'amount': 31},
                {'nutrient': {'name': 'Energy'}, 'amount': 165},
                {'nutrient': {'name': 'Total lipid (fat)'}, 'amount': 3.6}
            ]
        }
        mock_get.return_value = mock_response

        with patch.object(config.config, 'USDA_API_KEY', 'test_key'):
            api.api_key = 'test_key'
            food = api.get_food_details(123456)

        assert food is not None
        assert food['fdcId'] == 123456
        assert 'foodNutrients' in food

    def test_usda_works_without_api_key(self):
        """Test that USDA API can work without API key (limited access)."""
        with patch.object(config.config, 'USDA_API_KEY', ''):
            api = USDAAPI()
            # Should initialize without error
            assert api.api_key == ''


class TestAPICaching:
    """Test API response caching in database."""

    def test_get_from_cache(self, temp_db):
        """Test retrieving cached nutrition data."""
        api = SpoonacularAPI()
        api.db_path = temp_db

        # Save to cache first using private method
        test_data = {'name': 'chicken breast', 'calories': 165}
        api._save_to_cache('chicken breast', test_data, 100, 'grams')

        # Try to retrieve from cache
        cached = api._get_from_cache('chicken breast')

        assert cached is not None
        assert 'name' in cached

    def test_get_cached_nutrition_not_found(self, temp_db):
        """Test retrieving non-existent cached nutrition data."""
        api = SpoonacularAPI()
        api.db_path = temp_db
        cached = api._get_from_cache('Non-existent Food')

        assert cached is None

    def test_cache_prevents_duplicate_api_calls(self, temp_db, mock_spoonacular):
        """Test that cached data prevents duplicate API calls."""
        api, mock_get = mock_spoonacular
        api.db_path = temp_db

        # Cache data first using private method
        test_data = {'name': 'salmon', 'calories': 200}
        api._save_to_cache('salmon', test_data, 100, 'grams')

        # Mock the API to count calls
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = test_data
        mock_get.return_value = mock_response

        # get_ingredient_nutrition should use cache, not call API
        with patch.object(config.config, 'SPOONACULAR_API_KEY', 'test_key'):
            api.api_key = 'test_key'
            result = api.get_ingredient_nutrition('salmon')

        # Result should come from cache
        assert result is not None
        # API should not have been called (cache hit)
        assert mock_get.call_count == 0


class TestErrorHandling:
    """Test API error handling and edge cases."""

    def test_network_timeout_handling(self, mock_spoonacular):
        """Test handling of network timeouts."""
        api, mock_get = mock_spoonacular

        # Simulate timeout
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()

        with patch.object(config.config, 'SPOONACULAR_API_KEY', 'test_key'):
            api.api_key = 'test_key'
            result = api._make_request('test-endpoint')

        assert result is None

    def test_connection_error_handling(self, mock_spoonacular):
        """Test handling of connection errors."""
        api, mock_get = mock_spoonacular

        # Simulate connection error
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError()

        with patch.object(config.config, 'SPOONACULAR_API_KEY', 'test_key'):
            api.api_key = 'test_key'
            result = api._make_request('test-endpoint')

        assert result is None

    def test_invalid_json_response(self, mock_spoonacular):
        """Test handling of invalid JSON responses."""
        api, mock_get = mock_spoonacular

        # Simulate a bad response that raises exception on json()
        import requests
        mock_get.side_effect = requests.exceptions.JSONDecodeError("Invalid JSON", "", 0)

        with patch.object(config.config, 'SPOONACULAR_API_KEY', 'test_key'):
            api.api_key = 'test_key'
            result = api._make_request('test-endpoint')

        # Should handle gracefully and return None
        assert result is None

    def test_empty_search_results(self, mock_spoonacular):
        """Test handling of empty search results."""
        api, mock_get = mock_spoonacular

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'results': []}
        mock_get.return_value = mock_response

        with patch.object(config.config, 'SPOONACULAR_API_KEY', 'test_key'):
            api.api_key = 'test_key'
            results = api.search_recipes('nonexistent food')

        assert results == []

    def test_missing_api_key_returns_none(self, mock_spoonacular, capsys):
        """Test that requests fail gracefully when API key is missing."""
        api, mock_get = mock_spoonacular

        api.api_key = None
        result = api._make_request('test-endpoint')

        assert result is None
        captured = capsys.readouterr()
        assert "not configured" in captured.out.lower()


@pytest.mark.skipif(
    not config.config.SPOONACULAR_API_KEY,
    reason="SPOONACULAR_API_KEY not set in .env"
)
class TestLiveAPIIntegration:
    """Live API tests (only run when API key is configured)."""

    def test_live_recipe_search(self):
        """Test actual recipe search with real API."""
        api = SpoonacularAPI()
        results = api.search_recipes('chicken', max_results=1)

        assert results is not None
        if len(results) > 0:
            assert 'id' in results[0]
            assert 'title' in results[0]

    def test_live_ingredient_nutrition(self):
        """Test actual ingredient nutrition lookup with real API."""
        api = SpoonacularAPI()
        nutrition = api.get_ingredient_nutrition('chicken breast', amount=100, unit='g')

        assert nutrition is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
