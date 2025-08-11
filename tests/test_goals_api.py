"""
Test FastAPI Goals Routes
"""
from fastapi.testclient import TestClient
from fastapi import FastAPI
from goals.routes import goals_bp
import json

# Create test app
app = FastAPI()
app.include_router(goals_bp)

client = TestClient(app)

def test_goals_api():
    print("Testing Goals API...")
    
    # Test GET goals (empty initially)
    response = client.get("/api/goals")
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'success'
    assert len(data['goals']) == 0
    print("✅ GET goals (empty) - success")
    
    # Test POST goal
    goal_data = {
        "name": "Vacation Fund",
        "target_amount": 5000,
        "target_date": "2025-12-31T00:00:00Z",
        "category": "travel",
        "priority": "medium",
        "monthly_contribution": 200,
        "description": "Save for vacation"
    }
    
    response = client.post("/api/goals", json=goal_data)
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'success'
    goal_id = data['goal']['id']
    print("✅ POST goal - success")
    
    # Test GET goals (with data)
    response = client.get("/api/goals")
    assert response.status_code == 200
    data = response.json()
    assert len(data['goals']) == 1
    print("✅ GET goals (with data) - success")
    
    # Test PUT goal progress
    update_data = {
        "current_amount": 1000
    }
    response = client.put(f"/api/goals/{goal_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'success'
    print("✅ PUT goal progress - success")
    
    # Test dashboard
    response = client.get("/api/goals/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'success'
    print("✅ GET dashboard - success")
    
    # Test templates
    response = client.get("/api/goals/templates")
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'success'
    print("✅ GET templates - success")
    
    print("🎉 All API tests passed!")

if __name__ == "__main__":
    test_goals_api()
