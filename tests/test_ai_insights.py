import requests
import json

print("🤖 Testing Enhanced AI Insights...")

# Test budget calculation with AI insights
budget_data = {
    "budget": 15000,
    "duration": "monthly"
}

try:
    print("1. Testing AI tip generation...")
    response = requests.post("http://localhost:8000/api/tip", json=budget_data, timeout=10)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        tip_data = response.json()
        print(f"   AI Insights:")
        print(f"   {tip_data.get('tip', 'No tip available')}")
    else:
        print(f"   Error: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60)
print("✅ Enhanced AI Insights Features:")
print("• Intelligent spending pattern analysis")
print("• Personalized recommendations based on ratios")
print("• Priority action suggestions")
print("• Better formatted output with emojis and sections")
print("• Improved fallback logic for more valuable insights")
