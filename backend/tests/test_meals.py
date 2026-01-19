"""
Tests for meal tracking endpoints.
"""
import pytest
from fastapi.testclient import TestClient

def test_log_meal(client: TestClient, test_user):
    """Test logging a meal."""
    user_id = test_user["id"]
    response = client.post(
        f"/api/meals/log?user_id={user_id}",
        json={
            "meal_name": "Test Meal",
            "calories": 500,
            "protein_g": 30,
            "carbs_g": 50,
            "fat_g": 20,
            "meal_time": "lunch"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["meal_name"] == "Test Meal"
    assert data["calories"] == 500
    assert data["protein_g"] == 30

def test_get_daily_progress(client: TestClient, test_user):
    """Test getting daily progress."""
    user_id = test_user["id"]
    
    # First log a meal
    client.post(
        f"/api/meals/log?user_id={user_id}",
        json={
            "meal_name": "Breakfast",
            "calories": 400,
            "protein_g": 25,
            "carbs_g": 40,
            "fat_g": 15,
            "meal_time": "breakfast"
        }
    )
    
    # Get progress
    response = client.get(f"/api/meals/progress?user_id={user_id}")
    assert response.status_code == 200
    data = response.json()
    assert "totals" in data
    assert "targets" in data
    assert data["totals"]["calories"] == 400

def test_get_meal_history(client: TestClient, test_user):
    """Test getting meal history."""
    user_id = test_user["id"]
    
    # Log multiple meals
    for i in range(3):
        client.post(
            f"/api/meals/log?user_id={user_id}",
            json={
                "meal_name": f"Meal {i+1}",
                "calories": 300 + i * 100,
                "protein_g": 20,
                "carbs_g": 30,
                "fat_g": 10,
                "meal_time": "lunch"
            }
        )
    
    # Get history
    response = client.get(f"/api/meals/history?user_id={user_id}&days=7")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3

def test_delete_meal(client: TestClient, test_user):
    """Test deleting a meal."""
    user_id = test_user["id"]
    
    # Log a meal
    log_response = client.post(
        f"/api/meals/log?user_id={user_id}",
        json={
            "meal_name": "To Delete",
            "calories": 200,
            "protein_g": 10,
            "carbs_g": 20,
            "fat_g": 5,
            "meal_time": "snack"
        }
    )
    meal_id = log_response.json()["id"]
    
    # Delete the meal
    delete_response = client.delete(f"/api/meals/{meal_id}")
    assert delete_response.status_code == 200
    
    # Verify it's deleted (history should not include it)
    history_response = client.get(f"/api/meals/history?user_id={user_id}&days=1")
    meal_ids = [meal["id"] for meal in history_response.json()]
    assert meal_id not in meal_ids
