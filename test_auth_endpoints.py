"""
Test script for password and email change endpoints.
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_password_and_email_change():
    """Test password and email change endpoints."""
    
    # Step 1: Register a test user
    print("Step 1: Registering test user...")
    register_data = {
        "email": "testauth@macrochef.com",
        "password": "originalpass123",
        "name": "Test Auth User",
        "age": 30
    }
    
    try:
        register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        print(f"Registration status: {register_response.status_code}")
        if register_response.status_code == 201:
            print(f"Registration response: {register_response.json()}")
        else:
            print(f"Registration error: {register_response.text}")
            # Try to login instead (user might already exist)
            print("User might already exist, trying to login...")
    except Exception as e:
        print(f"Registration error: {e}")
        return
    
    # Step 2: Login to get token
    print("\nStep 2: Logging in...")
    login_data = {
        "email": "testauth@macrochef.com",
        "password": "originalpass123"
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login-json", json=login_data)
        print(f"Login status: {login_response.status_code}")
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get("access_token")
            print(f"Token received: {token[:20]}...")
        else:
            print(f"Login error: {login_response.text}")
            return
    except Exception as e:
        print(f"Login error: {e}")
        return
    
    # Step 3: Test password change endpoint
    print("\nStep 3: Testing password change endpoint...")
    password_change_data = {
        "current_password": "originalpass123",
        "new_password": "newpass123",
        "confirm_password": "newpass123"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    try:
        password_response = requests.patch(
            f"{BASE_URL}/auth/change-password",
            json=password_change_data,
            headers=headers
        )
        print(f"Password change status: {password_response.status_code}")
        print(f"Password change headers: {dict(password_response.headers)}")
        print(f"Password change raw response: {password_response.text[:500]}")
        try:
            print(f"Password change JSON response: {password_response.json()}")
        except:
            print("Could not parse JSON response")
        
        if password_response.status_code == 200:
            print("✅ Password change successful!")
            
            # Verify new password works
            print("\nVerifying new password...")
            verify_login = requests.post(
                f"{BASE_URL}/auth/login-json",
                json={"email": "testauth@macrochef.com", "password": "newpass123"}
            )
            if verify_login.status_code == 200:
                print("✅ New password verified - login successful!")
                token = verify_login.json().get("access_token")  # Update token
            else:
                print(f"❌ New password verification failed: {verify_login.text}")
        else:
            print(f"❌ Password change failed")
    except Exception as e:
        print(f"Password change error: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 4: Test email change endpoint
    print("\nStep 4: Testing email change endpoint...")
    email_change_data = {
        "new_email": "newemail@macrochef.com",
        "password": "newpass123"
    }
    
    try:
        email_response = requests.patch(
            f"{BASE_URL}/auth/change-email",
            json=email_change_data,
            headers=headers
        )
        print(f"Email change status: {email_response.status_code}")
        print(f"Email change response: {email_response.json()}")
        
        if email_response.status_code == 200:
            print("✅ Email change successful!")
            
            # Verify new email works
            print("\nVerifying new email...")
            verify_email_login = requests.post(
                f"{BASE_URL}/auth/login-json",
                json={"email": "newemail@macrochef.com", "password": "newpass123"}
            )
            if verify_email_login.status_code == 200:
                print("✅ New email verified - login successful!")
            else:
                print(f"❌ New email verification failed: {verify_email_login.text}")
        else:
            print(f"❌ Email change failed: {email_response.text}")
    except Exception as e:
        print(f"Email change error: {e}")
    
    print("\n" + "="*50)
    print("Test completed!")

if __name__ == "__main__":
    test_password_and_email_change()
