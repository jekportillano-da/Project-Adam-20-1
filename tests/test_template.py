import requests
import json

# Test the template functionality
def test_template_integration():
    # Test data that matches what the frontend sends
    test_data = {
        "amount": 20000,
        "duration": "monthly",
        "template": {
            "template_id": "fresh_graduate",
            "template_name": "Fresh Graduate",
            "allocations": {
                "Food & Dining": 5000,
                "Transportation": 3000,
                "Utilities": 2400,
                "Personal Care": 1600,
                "Entertainment": 2000,
                "Emergency Fund": 3000,
                "Savings": 3000
            }
        }
    }
    
    try:
        # Test budget calculation with template
        response = requests.post("http://localhost:8001/calculate", json=test_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Template integration working!")
        else:
            print("❌ Template integration failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_template_integration()
