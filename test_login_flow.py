#!/usr/bin/env python3
"""
Test script to verify the login flow and cookie authentication.
This script will help diagnose the login loop issue.
"""

import asyncio
import httpx
import sys
from pathlib import Path

# Add the project directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

BASE_URL = "http://localhost:8000"

async def test_login_flow():
    """Test the complete login flow"""
    print("🧪 Testing Login Flow")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Check if server is running
        print("\n1. Testing server connectivity...")
        try:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("✅ Server is running")
            else:
                print(f"❌ Server returned status {response.status_code}")
                return
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            print("💡 Make sure to start the server with: python gateway_enhanced.py")
            return
        
        # Test 2: Check unauthenticated home page (should redirect to login)
        print("\n2. Testing unauthenticated home page access...")
        response = await client.get(f"{BASE_URL}/", follow_redirects=False)
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print(f"✅ Redirected to: {response.headers.get('location', 'unknown')}")
        else:
            print(f"❌ Expected redirect (302), got {response.status_code}")
        
        # Test 3: Test login endpoint
        print("\n3. Testing login with test credentials...")
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        # First, try to register the test user (in case it doesn't exist)
        register_data = {
            "name": "Test User",
            "email": "test@example.com", 
            "password": "password123"
        }
        
        try:
            register_response = await client.post(
                f"{BASE_URL}/auth/register",
                json=register_data
            )
            if register_response.status_code == 200:
                print("✅ Test user registered successfully")
            else:
                print(f"ℹ️  User already exists or registration failed: {register_response.status_code}")
        except Exception as e:
            print(f"ℹ️  Registration error (user might already exist): {e}")
        
        # Now test login
        login_response = await client.post(
            f"{BASE_URL}/auth/login",
            json=login_data
        )
        
        print(f"   Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("✅ Login successful")
            login_result = login_response.json()
            print(f"   Token received: {login_result.get('access_token', 'None')[:20]}...")
            
            # Check Set-Cookie headers
            set_cookie = login_response.headers.get('set-cookie')
            if set_cookie:
                print(f"✅ Set-Cookie header: {set_cookie}")
            else:
                print("❌ No Set-Cookie header found")
            
            # Extract cookies from response
            cookies = login_response.cookies
            print(f"   Cookies received: {dict(cookies)}")
            
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            try:
                error_detail = login_response.json()
                print(f"   Error: {error_detail}")
            except:
                print(f"   Raw response: {login_response.text}")
            return
        
        # Test 4: Check /auth/me with cookies
        print("\n4. Testing /auth/me with cookies...")
        me_response = await client.get(f"{BASE_URL}/auth/me")
        print(f"   Status: {me_response.status_code}")
        
        if me_response.status_code == 200:
            print("✅ User info retrieved successfully")
            user_info = me_response.json()
            print(f"   User: {user_info.get('email', 'unknown')}")
        else:
            print(f"❌ Failed to get user info: {me_response.status_code}")
            try:
                error = me_response.json()
                print(f"   Error: {error}")
            except:
                print(f"   Raw response: {me_response.text}")
        
        # Test 5: Test home page with authentication
        print("\n5. Testing authenticated home page access...")
        home_response = await client.get(f"{BASE_URL}/", follow_redirects=False)
        print(f"   Status: {home_response.status_code}")
        
        if home_response.status_code == 200:
            print("✅ Home page loaded successfully (user is authenticated)")
        elif home_response.status_code == 302:
            print(f"❌ Still redirecting to: {home_response.headers.get('location', 'unknown')}")
            print("   This indicates the login loop issue!")
        else:
            print(f"❌ Unexpected status: {home_response.status_code}")
        
        # Test 6: Debug endpoint
        print("\n6. Testing debug endpoint...")
        try:
            debug_response = await client.get(f"{BASE_URL}/debug/auth")
            if debug_response.status_code == 200:
                debug_info = debug_response.json()
                print("✅ Debug info:")
                for key, value in debug_info.items():
                    print(f"   {key}: {value}")
            else:
                print(f"❌ Debug endpoint failed: {debug_response.status_code}")
        except Exception as e:
            print(f"ℹ️  Debug endpoint not available: {e}")

if __name__ == "__main__":
    print("🚀 Starting Login Flow Test")
    print("Make sure the server is running on http://localhost:8000")
    print("Start it with: python gateway_enhanced.py")
    print()
    
    try:
        asyncio.run(test_login_flow())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
