"""
Test the Goals API integration
"""
import requests
import json

def test_goals_integration():
    base_url = "http://localhost:8000"
    
    try:
        # Test 1: Get goals (should be empty initially)
        print("🧪 Testing GET /api/goals...")
        response = requests.get(f"{base_url}/api/goals")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {len(data['goals'])} goals found")
        else:
            print(f"❌ Failed: {response.text}")
        
        # Test 2: Create a new goal
        print("\n🧪 Testing POST /api/goals...")
        goal_data = {
            "name": "Emergency Fund",
            "target_amount": 10000,
            "target_date": "2025-12-31T00:00:00Z",
            "category": "savings",
            "priority": "high",
            "monthly_contribution": 500,
            "description": "Build emergency savings"
        }
        
        response = requests.post(f"{base_url}/api/goals", json=goal_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            goal_id = data['goal']['id']
            print(f"✅ Success: Created goal with ID {goal_id}")
            
            # Test 3: Get goals again (should have 1 goal)
            print("\n🧪 Testing GET /api/goals (with data)...")
            response = requests.get(f"{base_url}/api/goals")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success: {len(data['goals'])} goals found")
                print(f"Goal: {data['goals'][0]['name']} - {data['goals'][0]['progress_percentage']:.1f}%")
            
            # Test 4: Update goal progress
            print("\n🧪 Testing PUT /api/goals/{goal_id}...")
            update_data = {"current_amount": 2500}
            response = requests.put(f"{base_url}/api/goals/{goal_id}", json=update_data)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success: Updated progress to {data['goal']['progress_percentage']:.1f}%")
            
            # Test 5: Get dashboard
            print("\n🧪 Testing GET /api/goals/dashboard...")
            response = requests.get(f"{base_url}/api/goals/dashboard")
            if response.status_code == 200:
                data = response.json()
                dashboard = data['dashboard']
                print(f"✅ Success: Dashboard shows {dashboard['total_goals']} goals, {dashboard['overall_progress']:.1f}% progress")
        else:
            print(f"❌ Failed to create goal: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_goals_integration()
