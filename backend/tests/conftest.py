"""
Pytest configuration and fixtures for backend tests.
"""
import pytest
import tempfile
import os
import sqlite3
import sys
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app

# Add project root to path to import db_setup
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
from scripts.db_setup import create_tables

def add_auth_columns(conn):
    """Add email and password_hash columns for authentication."""
    cursor = conn.cursor()
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(user_profile)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'email' not in columns:
            cursor.execute("ALTER TABLE user_profile ADD COLUMN email TEXT")
        
        if 'password_hash' not in columns:
            cursor.execute("ALTER TABLE user_profile ADD COLUMN password_hash TEXT")
        
        # Create unique index on email
        try:
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_user_email ON user_profile(email)")
        except sqlite3.OperationalError:
            pass  # Index might already exist or have duplicates
        
        conn.commit()
    except Exception:
        conn.rollback()
        raise

@pytest.fixture
def temp_db():
    """Create a temporary database for testing with schema initialized."""
    # Create temporary database file
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Set environment variable for test database
    os.environ['DATABASE_URL'] = f'sqlite:///{path}'
    
    # Initialize database schema
    conn = sqlite3.connect(path)
    try:
        create_tables(conn)
        add_auth_columns(conn)
    finally:
        conn.close()
    
    yield path
    
    # Cleanup - ensure connection is closed
    try:
        if os.path.exists(path):
            # Try to close any remaining connections
            conn = sqlite3.connect(path)
            conn.close()
            # Small delay to allow file system to release the file
            import time
            time.sleep(0.1)
            os.unlink(path)
    except (PermissionError, OSError):
        # File might still be locked, but that's OK for temp files
        # Windows will clean up temp files eventually
        pass
    
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
