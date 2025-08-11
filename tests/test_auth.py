#!/usr/bin/env python3
"""
Test script for the authentication system
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_registration():
    """Test user registration"""
    print("Testing user registration...")
    
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"Registration Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Registration successful!")
        print(f"Response: {response.json()}")
        return True
    else:
        print("❌ Registration failed!")
        print(f"Error: {response.text}")
        return False

def test_login():
    """Test user login"""
    print("\nTesting user login...")
    
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Login Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Login successful!")
        token_data = response.json()
        print(f"Token received: {token_data['access_token'][:20]}...")
        return token_data['access_token']
    else:
        print("❌ Login failed!")
        print(f"Error: {response.text}")
        return None

def test_protected_endpoint(token):
    """Test accessing a protected endpoint"""
    print("\nTesting protected endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Protected endpoint status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Protected endpoint access successful!")
        print(f"User info: {response.json()}")
        return True
    else:
        print("❌ Protected endpoint access failed!")
        print(f"Error: {response.text}")
        return False

def test_tip_endpoint(token=None):
    """Test the budget tip endpoint with optional authentication"""
    print("\nTesting budget tip endpoint...")
    
    tip_data = {
        "budget": 5000,
        "duration": "monthly"
    }
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    response = requests.post(f"{BASE_URL}/api/tip", json=tip_data, headers=headers)
    print(f"Tip endpoint status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Budget tip endpoint working!")
        # Don't print the full response as it might be large
        print("Tip generated successfully")
        return True
    else:
        print("❌ Budget tip endpoint failed!")
        print(f"Error: {response.text}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting authentication system tests...")
    print("=" * 50)
    
    # Test registration
    reg_success = test_registration()
    
    # Test login
    token = test_login() if reg_success else None
    
    # Test protected endpoint
    if token:
        test_protected_endpoint(token)
        test_tip_endpoint(token)
    else:
        print("\n⚠️ Skipping protected endpoint tests due to login failure")
    
    # Test tip endpoint without auth
    test_tip_endpoint()
    
    print("\n" + "=" * 50)
    print("🏁 Tests completed!")

if __name__ == "__main__":
    main()
