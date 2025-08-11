"""
Test script to demonstrate the goals tracking system functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from goals_tracker import GoalsTracker, FinancialGoal
from datetime import datetime, timedelta

def test_goals_system():
    """Test the complete goals tracking system"""
    print("🎯 Testing Financial Goals Tracking System")
    print("=" * 50)
    
    # Create a new goals tracker
    tracker = GoalsTracker()
    
    # Test 1: Add some sample goals
    print("\n1. Creating Sample Goals:")
    
    # Emergency Fund Goal
    emergency_goal = tracker.add_goal(
        name="Emergency Fund",
        target_amount=150000,
        target_date=datetime.now() + timedelta(days=365),
        category="emergency_fund",
        priority="high",
        monthly_contribution=10000,
        description="6 months of living expenses as emergency fund"
    )
    print(f"   ✓ {emergency_goal.name}: ₱{emergency_goal.target_amount:,} target")
    
    # Vacation Goal
    vacation_goal = tracker.add_goal(
        name="Japan Vacation",
        target_amount=120000,
        target_date=datetime.now() + timedelta(days=240),
        category="vacation",
        priority="medium", 
        monthly_contribution=15000,
        description="Dream vacation to Japan"
    )
    print(f"   ✓ {vacation_goal.name}: ₱{vacation_goal.target_amount:,} target")
    
    # House Down Payment Goal
    house_goal = tracker.add_goal(
        name="House Down Payment",
        target_amount=800000,
        target_date=datetime.now() + timedelta(days=730),
        category="real_estate",
        priority="high",
        monthly_contribution=25000,
        description="20% down payment for first home"
    )
    print(f"   ✓ {house_goal.name}: ₱{house_goal.target_amount:,} target")
    
    # Test 2: Update progress on goals
    print("\n2. Updating Goal Progress:")
    
    # Simulate some progress
    tracker.update_goal_progress(emergency_goal.id, 45000)
    tracker.update_goal_progress(vacation_goal.id, 30000)
    tracker.update_goal_progress(house_goal.id, 75000)
    
    print(f"   ✓ Emergency Fund: ₱45,000 saved (30% complete)")
    print(f"   ✓ Japan Vacation: ₱30,000 saved (25% complete)")
    print(f"   ✓ House Down Payment: ₱75,000 saved (9% complete)")
    
    # Test 3: Show goal details
    print("\n3. Goal Analysis:")
    
    for goal in tracker.goals:
        progress = goal.progress_percentage
        remaining = goal.remaining_amount
        months_left = goal.months_remaining
        required_monthly = goal.required_monthly_contribution
        on_track = goal.is_on_track
        
        print(f"\n   📋 {goal.name}")
        print(f"      Progress: {progress:.1f}% complete")
        print(f"      Remaining: ₱{remaining:,}")
        print(f"      Time left: {months_left} months")
        print(f"      Required monthly: ₱{required_monthly:,.0f}")
        print(f"      Current monthly: ₱{goal.monthly_contribution:,}")
        print(f"      Status: {'✅ On Track' if on_track else '⚠️ Needs Attention'}")
    
    # Test 4: Dashboard Summary
    print("\n4. Dashboard Summary:")
    
    dashboard = tracker.get_dashboard_summary()
    
    print(f"   📊 Total Goals: {dashboard['total_goals']}")
    print(f"   ✅ Goals On Track: {dashboard['goals_on_track']}")
    print(f"   💰 Total Target: ₱{dashboard['total_target_amount']:,}")
    print(f"   💵 Total Saved: ₱{dashboard['total_current_amount']:,}")
    print(f"   📈 Overall Progress: {dashboard['overall_progress']:.1f}%")
    
    # Test 5: Savings Allocation Suggestions
    print("\n5. Smart Savings Allocation (₱50,000 available):")
    
    suggestions = tracker.suggest_monthly_allocations(50000)
    
    print(f"   Available for allocation: ₱50,000")
    print(f"   Recommended allocations:")
    
    for suggestion in suggestions['suggestions']:
        sufficient = "✅" if suggestion['is_sufficient'] else "⚠️"
        print(f"      {sufficient} {suggestion['goal_name']}: ₱{suggestion['suggested_amount']:,}")
        
    print(f"   Total allocated: ₱{suggestions['total_allocated']:,}")
    print(f"   Remaining: ₱{suggestions['remaining_unallocated']:,}")
    
    # Test 6: Goal Templates
    print("\n6. Available Goal Templates:")
    
    templates = tracker.get_goal_templates()
    
    for template_id, template in templates.items():
        print(f"   📝 {template['name']} ({template['category']})")
        print(f"      Priority: {template['priority']}")
        print(f"      {template['description']}")
    
    # Test 7: Create goal from template
    print("\n7. Creating Goal from Template:")
    
    education_goal = tracker.create_goal_from_template(
        template_id="education_fund",
        target_amount=75000,
        target_date=datetime.now() + timedelta(days=180),
        monthly_contribution=12000
    )
    
    if education_goal:
        print(f"   ✓ Created: {education_goal.name}")
        print(f"   📚 Target: ₱{education_goal.target_amount:,}")
        print(f"   🎓 Category: {education_goal.category}")
    
    print("\n" + "=" * 50)
    print("✅ Goals Tracking System Test Complete!")
    print(f"📊 Final Stats: {len(tracker.goals)} goals created")
    
    return tracker

if __name__ == "__main__":
    test_goals_system()
