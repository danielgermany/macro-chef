"""
Tests for authentication endpoints.
"""
import pytest
from fastapi.testclient import TestClient

def test_register_user(client: TestClient):
    """Test user registration."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "securepass123",
            "name": "New User",
        }
    )
    if response.status_code != 201:
        print(f"ERROR: Status {response.status_code}, Response: {response.text}")
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["name"] == "New User"
    assert "id" in data

def test_register_duplicate_email(client: TestClient):
    """Test that duplicate email registration fails."""
    # Register first user
    client.post(
        "/api/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "password123",
            "name": "First User",
        }
    )
    
    # Try to register again with same email
    response = client.post(
        "/api/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "password123",
            "name": "Second User",
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()

def test_login_success(client: TestClient):
    """Test successful login."""
    # Register user first
    client.post(
        "/api/auth/register",
        json={
            "email": "login@example.com",
            "password": "mypassword123",
            "name": "Login User",
        }
    )
    
    # Login
    response = client.post(
        "/api/auth/login-json",
        json={
            "email": "login@example.com",
            "password": "mypassword123",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client: TestClient):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/auth/login-json",
        json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword",
        }
    )
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()

def test_get_current_user(client: TestClient, auth_token: str):
    """Test getting current user with valid token."""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"

def test_get_current_user_no_token(client: TestClient):
    """Test getting current user without token."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401

def test_get_current_user_invalid_token(client: TestClient):
    """Test getting current user with invalid token."""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token_here"}
    )
    assert response.status_code == 401
