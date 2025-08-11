#!/usr/bin/env python3
"""
Authentication debugging script
"""

import requests
import json

BASE_URL = "http://localhost:8080"

def test_auth_flow():
    print("=== Authentication Flow Debug ===")
    
    # Test 1: Debug endpoint without authentication
    print("\n1. Testing debug endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/debug/auth")
        print(f"Debug status: {response.status_code}")
        if response.status_code == 200:
            print(f"Debug data: {response.json()}")
    except Exception as e:
        print(f"Debug error: {e}")
    
    # Test 2: Try to access protected endpoint without auth
    print("\n2. Testing /auth/me without authentication...")
    try:
        response = requests.get(f"{BASE_URL}/auth/me")
        print(f"Auth/me status: {response.status_code}")
        if response.status_code != 401:
            print(f"Unexpected response: {response.text}")
    except Exception as e:
        print(f"Auth/me error: {e}")
    
    # Test 3: Register a test user
    print("\n3. Registering test user...")
    try:
        register_data = {
            "name": "Test User",
            "email": "testuser@example.com", 
            "password": "testpass123"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        print(f"Register status: {response.status_code}")
        if response.status_code == 200:
            print("Registration successful")
        else:
            print(f"Register response: {response.text}")
    except Exception as e:
        print(f"Register error: {e}")
    
    # Test 4: Login with test user
    print("\n4. Logging in...")
    try:
        login_data = {
            "email": "testuser@example.com",
            "password": "testpass123"
        }
        session = requests.Session()
        response = session.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Login status: {response.status_code}")
        
        if response.status_code == 200:
            print("Login successful!")
            print(f"Response headers: {dict(response.headers)}")
            print(f"Set-Cookie: {response.headers.get('Set-Cookie', 'None')}")
            
            # Test 5: Check authentication with cookies
            print("\n5. Testing /auth/me with cookies...")
            me_response = session.get(f"{BASE_URL}/auth/me")
            print(f"Auth/me with cookies status: {me_response.status_code}")
            if me_response.status_code == 200:
                print(f"User data: {me_response.json()}")
            else:
                print(f"Auth/me error: {me_response.text}")
                
            # Test 6: Debug with cookies
            print("\n6. Testing debug with cookies...")
            debug_response = session.get(f"{BASE_URL}/debug/auth")
            print(f"Debug with cookies: {debug_response.json()}")
                
        else:
            print(f"Login failed: {response.text}")
            
    except Exception as e:
        print(f"Login error: {e}")

if __name__ == "__main__":
    test_auth_flow()
