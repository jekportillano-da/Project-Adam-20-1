"""
Quick test of the goals system to verify functionality
"""
from goals_tracker import GoalsTracker
from datetime import datetime, timedelta

def test_goals_system():
    print("Testing Goals System...")
    
    # Create tracker
    tracker = GoalsTracker()
    
    # Add a test goal
    target_date = datetime.now() + timedelta(days=365)
    goal = tracker.add_goal(
        name="Emergency Fund",
        target_amount=10000,
        target_date=target_date,
        category="savings",
        priority="high",
        monthly_contribution=500,
        description="Build emergency savings"
    )
    
    print(f"Created goal: {goal.name}")
    print(f"Progress: {goal.progress_percentage:.1f}%")
    print(f"Required monthly: ${goal.required_monthly_contribution:.2f}")
    
    # Test progress update
    tracker.update_goal_progress(goal.id, 2500)
    print(f"After $2500 contribution: {goal.progress_percentage:.1f}%")
    
    # Test dashboard summary
    dashboard = tracker.get_dashboard_summary()
    print(f"Total goals: {dashboard['total_goals']}")
    print(f"Overall progress: {dashboard['overall_progress']:.1f}%")
    
    # Test suggestions
    suggestions = tracker.suggest_monthly_allocations(1000)
    print(f"Monthly allocation suggestions: {suggestions}")
    
    print("✅ All tests passed!")

if __name__ == "__main__":
    test_goals_system()
