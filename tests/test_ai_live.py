#!/usr/bin/env python3
"""
Test the enhanced AI insights functionality
"""
import requests
import json

def test_budget_calculator():
    """Test the budget calculator with sample data"""
    print("🧮 Testing Budget Calculator...")
    
    # Sample budget data
    budget_data = {
        "income": 5000,
        "rent": 1500,
        "groceries": 600,
        "utilities": 200,
        "transportation": 300,
        "entertainment": 400,
        "other": 200
    }
    
    try:
        # Test budget analysis
        response = requests.post(
            "http://localhost:8000/demo/api/calculate",
            json=budget_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Budget calculation successful!")
            print(f"   Total expenses: ${result.get('total_expenses', 0)}")
            print(f"   Remaining: ${result.get('remaining', 0)}")
            return result
        else:
            print(f"❌ Budget calculation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Budget calculation error: {e}")
        return None

def test_ai_insights(budget_result):
    """Test the enhanced AI insights"""
    print("\n🤖 Testing Enhanced AI Insights...")
    
    if not budget_result:
        print("❌ Cannot test AI insights without budget data")
        return
    
    try:
        # Test AI insights
        response = requests.post(
            "http://localhost:8000/demo/api/ai-tip",
            json=budget_result,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ AI insights generated successfully!")
            
            tip = result.get('tip', '')
            if tip:
                print(f"\n📊 AI Financial Analysis:")
                print("=" * 50)
                
                # Parse and display sections nicely
                lines = tip.split('\n')
                for line in lines:
                    if line.strip():
                        if line.startswith('##'):
                            print(f"\n🔍 {line.replace('##', '').strip()}")
                        elif line.startswith('###'):
                            print(f"\n   📈 {line.replace('###', '').strip()}")
                        elif line.startswith('-'):
                            print(f"   {line}")
                        else:
                            print(f"   {line}")
                
                print("=" * 50)
            else:
                print("⚠️  No AI tip content received")
                
        else:
            print(f"❌ AI insights failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ AI insights error: {e}")

def main():
    print("🚀 Testing Enhanced Budget Calculator & AI Insights")
    print("=" * 60)
    
    # Test budget calculator
    budget_result = test_budget_calculator()
    
    # Test AI insights
    test_ai_insights(budget_result)
    
    print(f"\n✨ Test completed!")
    print(f"🌐 Access the app at: http://localhost:8000/demo")

if __name__ == "__main__":
    main()
