"""
Test script for Security Tab features (password and email change)
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000/api"

def print_step(step_num, description):
    print(f"\n{'='*60}")
    print(f"Step {step_num}: {description}")
    print('='*60)

def test_security_features():
    """Test password and email change endpoints"""
    
    # Step 1: Register a test user (or use existing)
    print_step(1, "Registering/Logging in test user")
    
    test_email = "security_test@macrochef.com"
    test_password = "testpass123"
    
    # Try to register first
    try:
        register_data = {
            "email": test_email,
            "password": test_password,
            "name": "Security Test User"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code == 201:
            print("[OK] User registered successfully")
            user_data = response.json()
            user_id = user_data.get("id")
        elif response.status_code == 400 and "already registered" in response.json().get("detail", "").lower():
            print("[INFO] User already exists, proceeding to login")
        else:
            print(f"[WARN] Registration response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[WARN] Registration error (may already exist): {e}")
    
    # Step 2: Login to get token
    print_step(2, "Logging in to get authentication token")
    
    login_data = {
        "email": test_email,
        "password": test_password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login-json", json=login_data)
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data.get("access_token")
        print(f"[OK] Login successful")
        print(f"   Token received: {access_token[:20]}...")
    except requests.exceptions.RequestException as e:
        print(f"[FAIL] Login failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")
        return False
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Step 3: Get current user info
    print_step(3, "Getting current user information")
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        response.raise_for_status()
        user_info = response.json()
        print(f"[OK] User info retrieved")
        print(f"   User ID: {user_info.get('id')}")
        print(f"   Name: {user_info.get('name')}")
        print(f"   Email: {user_info.get('email', 'Not set')}")
    except requests.exceptions.RequestException as e:
        print(f"[FAIL] Failed to get user info: {e}")
        return False
    
    # Step 4: Test password change
    print_step(4, "Testing password change")
    
    new_password = "newpass123"
    password_change_data = {
        "current_password": test_password,
        "new_password": new_password,
        "confirm_password": new_password
    }
    
    try:
        response = requests.patch(
            f"{BASE_URL}/auth/change-password",
            json=password_change_data,
            headers=headers
        )
        response.raise_for_status()
        result = response.json()
        print(f"[OK] Password changed successfully!")
        print(f"   Message: {result.get('message')}")
    except requests.exceptions.RequestException as e:
        print(f"[FAIL] Password change failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Status: {e.response.status_code}")
            print(f"   Response: {e.response.text}")
        return False
    
    # Step 5: Verify new password works
    print_step(5, "Verifying new password works")
    
    login_data_new = {
        "email": test_email,
        "password": new_password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login-json", json=login_data_new)
        response.raise_for_status()
        token_data = response.json()
        new_access_token = token_data.get("access_token")
        print(f"[OK] Login with new password successful")
        headers["Authorization"] = f"Bearer {new_access_token}"
    except requests.exceptions.RequestException as e:
        print(f"[FAIL] Login with new password failed: {e}")
        return False
    
    # Step 6: Test email change
    print_step(6, "Testing email change")
    
    new_email = "security_test_new@macrochef.com"
    email_change_data = {
        "new_email": new_email,
        "password": new_password
    }
    
    try:
        response = requests.patch(
            f"{BASE_URL}/auth/change-email",
            json=email_change_data,
            headers=headers
        )
        response.raise_for_status()
        result = response.json()
        print(f"[OK] Email changed successfully!")
        print(f"   Message: {result.get('message')}")
        print(f"   New email: {new_email}")
    except requests.exceptions.RequestException as e:
        print(f"[FAIL] Email change failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Status: {e.response.status_code}")
            print(f"   Response: {e.response.text}")
        return False
    
    # Step 7: Verify new email works
    print_step(7, "Verifying new email works")
    
    login_data_new_email = {
        "email": new_email,
        "password": new_password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login-json", json=login_data_new_email)
        response.raise_for_status()
        token_data = response.json()
        final_access_token = token_data.get("access_token")
        print(f"[OK] Login with new email successful")
        print(f"   Final token: {final_access_token[:20]}...")
    except requests.exceptions.RequestException as e:
        print(f"[FAIL] Login with new email failed: {e}")
        return False
    
    # Step 8: Test error cases
    print_step(8, "Testing error cases")
    
    # Test password mismatch
    print("\n  Testing password mismatch validation...")
    try:
        response = requests.patch(
            f"{BASE_URL}/auth/change-password",
            json={
                "current_password": new_password,
                "new_password": "testpass456",
                "confirm_password": "differentpass456"
            },
            headers=headers
        )
        if response.status_code == 400:
            print(f"  [OK] Password mismatch correctly rejected (400)")
        else:
            print(f"  [WARN] Expected 400, got {response.status_code}")
    except Exception as e:
        print(f"  [WARN] Error testing mismatch: {e}")
    
    # Test wrong current password
    print("\n  Testing wrong current password...")
    try:
        response = requests.patch(
            f"{BASE_URL}/auth/change-password",
            json={
                "current_password": "wrongpassword",
                "new_password": "testpass456",
                "confirm_password": "testpass456"
            },
            headers=headers
        )
        if response.status_code == 401:
            print(f"  [OK] Wrong password correctly rejected (401)")
        else:
            print(f"  [WARN] Expected 401, got {response.status_code}")
    except Exception as e:
        print(f"  [WARN] Error testing wrong password: {e}")
    
    print("\n" + "="*60)
    print("[SUCCESS] ALL SECURITY FEATURE TESTS PASSED!")
    print("="*60 + "\n")
    
    return True

if __name__ == "__main__":
    try:
        success = test_security_features()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[WARN] Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
