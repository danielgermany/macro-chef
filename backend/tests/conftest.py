"""
Pytest configuration and fixtures for backend tests.
"""
import pytest
import tempfile
import os
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app

@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    # Create temporary database file
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Set environment variable for test database
    os.environ['DATABASE_URL'] = f'sqlite:///{path}'
    
    yield path
    
    # Cleanup
    if os.path.exists(path):
        os.unlink(path)
    if 'DATABASE_URL' in os.environ:
        del os.environ['DATABASE_URL']

@pytest.fixture
def client(temp_db):
    """Create a test client with temporary database."""
    return TestClient(app)

@pytest.fixture
def test_user(client):
    """Create a test user and return user data."""
    response = client.post(
        "/api/users/",
        json={
            "name": "Test User",
            "age": 30,
            "sex": "male",
            "height_inches": 70.0,
            "weight_lbs": 180.0,
            "goal_type": "maintain",
            "activity_level": "moderate",
            "training_days_per_week": 3,
            "weekly_budget_usd": 100.0,
        }
    )
    assert response.status_code == 201
    return response.json()

@pytest.fixture
def auth_token(client, test_user):
    """Create a test user with auth and return token."""
    # First, we need to register a user with email/password
    # For testing, we'll use the auth register endpoint
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "name": "Test User",
            "age": 30,
            "sex": "male",
            "height_inches": 70.0,
            "weight_lbs": 180.0,
        }
    )
    assert response.status_code == 201
    
    # Login to get token
    login_response = client.post(
        "/api/auth/login-json",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
        }
    )
    assert login_response.status_code == 200
    return login_response.json()["access_token"]
