#!/usr/bin/env python3
"""
Simple test script to debug the authentication issue
"""
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all modules can be imported"""
    try:
        print("Testing imports...")
        
        print("1. Importing FastAPI...")
        from fastapi import FastAPI
        print("   ✓ FastAPI imported successfully")
        
        print("2. Importing auth module...")
        import auth
        print("   ✓ Auth module imported successfully")
        
        print("3. Importing gateway...")
        import gateway
        print("   ✓ Gateway imported successfully")
        
        print("4. Testing auth components...")
        from auth.auth_utils import auth_manager
        from auth.database import db
        print("   ✓ Auth components imported successfully")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Import failed: {e}")
        return False

def test_auth_flow():
    """Test authentication flow"""
    try:
        print("\nTesting authentication flow...")
        
        from auth.auth_utils import auth_manager
        from auth.database import db
        
        # Test password hashing
        test_password = "testpassword123"
        hashed = auth_manager.get_password_hash(test_password)
        print(f"   ✓ Password hashing works")
        
        # Test token creation
        test_data = {"sub": "test@example.com"}
        token = auth_manager.create_access_token(data=test_data)
        print(f"   ✓ Token creation works")
        
        # Test token verification
        payload = auth_manager.verify_token(token)
        print(f"   ✓ Token verification works: {payload}")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Auth flow test failed: {e}")
        return False

def main():
    """Main test function"""
    print("=== Server Diagnostic Test ===\n")
    
    if not test_imports():
        print("\n❌ Import test failed - Cannot proceed")
        return False
    
    if not test_auth_flow():
        print("\n❌ Auth flow test failed")
        return False
    
    print("\n✅ All tests passed! Server should work properly.")
    print("\nStarting server...")
    
    try:
        import uvicorn
        uvicorn.run(
            "gateway:app", 
            host="127.0.0.1",
            port=8080,
            reload=False,
            log_level="debug",
        )
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        return False

if __name__ == "__main__":
    main()
