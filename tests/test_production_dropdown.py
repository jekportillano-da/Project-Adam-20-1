#!/usr/bin/env python3
"""
Test production authentication and dropdown behavior
"""

import requests

def test_production_auth():
    print("=== TESTING PRODUCTION AUTHENTICATION ===")
    
    base_url = "http://localhost:8080"
    session = requests.Session()
    
    # Step 1: Try to access main page (should redirect to login)
    print("\n1. Testing main page access...")
    response = session.get(f"{base_url}/")
    print(f"Main page response: {response.status_code}")
    print(f"Final URL: {response.url}")
    
    # Step 2: Login with our test account
    print("\n2. Attempting login...")
    login_data = {
        "email": "jek.test@example.com",
        "password": "TestPassword123!"
    }
    
    response = session.post(f"{base_url}/auth/login", json=login_data)
    print(f"Login response: {response.status_code}")
    if response.status_code == 200:
        print("✅ Login successful!")
        print(f"Cookies set: {dict(session.cookies)}")
    else:
        print(f"❌ Login failed: {response.text}")
        return
    
    # Step 3: Test authentication endpoint
    print("\n3. Testing auth/me endpoint...")
    response = session.get(f"{base_url}/auth/me")
    print(f"Auth/me response: {response.status_code}")
    if response.status_code == 200:
        user_data = response.json()
        print(f"✅ User data: {user_data}")
    else:
        print(f"❌ Auth check failed: {response.text}")
    
    # Step 4: Test main page after login
    print("\n4. Testing main page after login...")
    response = session.get(f"{base_url}/")
    print(f"Main page response: {response.status_code}")
    if response.status_code == 200:
        print("✅ Main page accessible after login")
        # Check if the page contains the dropdown elements
        if 'id="auth-logout"' in response.text:
            print("✅ Logout button found in HTML")
        else:
            print("❌ Logout button NOT found in HTML")
    
if __name__ == "__main__":
    test_production_auth()
