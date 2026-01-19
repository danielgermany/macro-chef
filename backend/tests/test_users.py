"""
Tests for user profile endpoints.
"""
import pytest
from fastapi.testclient import TestClient

def test_create_user(client: TestClient):
    """Test creating a user."""
    response = client.post(
        "/api/users/",
        json={
            "name": "John Doe",
            "age": 28,
            "sex": "male",
            "height_inches": 72.0,
            "weight_lbs": 180.0,
            "goal_type": "cut",
            "activity_level": "active",
            "training_days_per_week": 5,
            "weekly_budget_usd": 120.0,
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["age"] == 28
    assert data["goal_type"] == "cut"
    assert "id" in data

def test_get_user(client: TestClient, test_user):
    """Test getting a user by ID."""
    user_id = test_user["id"]
    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["name"] == "Test User"

def test_get_nonexistent_user(client: TestClient):
    """Test getting a user that doesn't exist."""
    response = client.get("/api/users/99999")
    assert response.status_code == 404

def test_update_user(client: TestClient, test_user):
    """Test updating a user."""
    user_id = test_user["id"]
    response = client.patch(
        f"/api/users/{user_id}",
        json={
            "weight_lbs": 175.0,
            "goal_type": "bulk",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["weight_lbs"] == 175.0
    assert data["goal_type"] == "bulk"

def test_log_body_metrics(client: TestClient, test_user):
    """Test logging body metrics."""
    user_id = test_user["id"]
    response = client.post(
        f"/api/users/{user_id}/metrics",
        json={
            "weight_lbs": 178.0,
            "body_fat_pct": 14.5,
            "waist_inches": 32.0,
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["weight_lbs"] == 178.0
    assert data["body_fat_pct"] == 14.5

def test_get_metrics_history(client: TestClient, test_user):
    """Test getting metrics history."""
    user_id = test_user["id"]
    
    # Log some metrics
    for weight in [180.0, 179.0, 178.0]:
        client.post(
            f"/api/users/{user_id}/metrics",
            json={"weight_lbs": weight}
        )
    
    # Get history
    response = client.get(f"/api/users/{user_id}/metrics?days=30")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
