#!/usr/bin/env python3

import requests
import json

def test_services():
    """Test all microservices are responding"""
    
    # Test individual services
    services = {
        "Budget Service": "http://localhost:8001",
        "Savings Service": "http://localhost:8002", 
        "Insights Service": "http://localhost:8003"
    }
    
    print("Testing individual microservices...")
    for name, url in services.items():
        try:
            response = requests.get(f"{url}/", timeout=5)
            print(f"✅ {name}: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
    
    print("\nTesting gateway API endpoints...")
    
    # Test budget calculation through gateway
    try:
        budget_data = {"amount": 10000, "duration": "monthly"}
        response = requests.post("http://localhost:8000/api/budget/calculate", 
                               json=budget_data, timeout=10)
        print(f"✅ Budget API: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Budget API: Error - {e}")
    
    # Test savings forecast through gateway
    try:
        savings_data = {
            "monthly_savings": 1000,
            "emergency_fund": 5000,
            "current_goal": 50000
        }
        response = requests.post("http://localhost:8000/api/savings/forecast", 
                               json=savings_data, timeout=10)
        print(f"✅ Savings API: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Savings API: Error - {e}")

if __name__ == "__main__":
    test_services()
