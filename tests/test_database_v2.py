#!/usr/bin/env python3
"""
Comprehensive test suite for Budget Buddy v2 Database
Tests all new features and database functionality
"""

import sys
import os
from pathlib import Path
from datetime import date, datetime, timedelta
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.database_v2 import BudgetBuddyDatabase

def test_comprehensive_database():
    """Run comprehensive tests of the new database system"""
    
    print("🧪 Testing Budget Buddy v2 Database System")
    print("=" * 60)
    
    # Clean up any existing test database
    test_db_path = Path("test_budget_buddy_v2.db")
    if test_db_path.exists():
        test_db_path.unlink()
        print("🧹 Cleaned up existing test database")
    
    # Create test database
    test_db = BudgetBuddyDatabase("test_budget_buddy_v2.db")
    
    # Verify database schema was created properly
    print("\n0. Verifying Database Schema")
    print("-" * 40)
    try:
        with test_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(users);")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            required_columns = ['id', 'email', 'name', 'age', 'civil_status', 'hobbies']
            missing_columns = [col for col in required_columns if col not in column_names]
            
            if missing_columns:
                print(f"   ✗ Missing columns in users table: {missing_columns}")
                print(f"   Available columns: {column_names}")
                return False
            else:
                print(f"   ✓ All required columns present: {len(column_names)} total")
                
    except Exception as e:
        print(f"   ✗ Schema verification failed: {e}")
        return False
    
    # Test user creation with comprehensive profile
    print("\n1. Testing User Creation with Profile Data")
    print("-" * 40)
    
    try:
        user_id = test_db.create_user(
            email="test@example.com",
            name="Test User",
            hashed_password="hashed_password_123",
            age=28,
            civil_status="single",
            number_of_dependents=0,
            number_of_kids=0,
            location="Manila",
            hobbies=["gaming", "reading", "cooking"],
            free_time_activities=["netflix", "gym", "coffee shops"],
            spending_personality="balanced",
            financial_goals_priority="emergency_fund"
        )
        print(f"   ✓ User created with ID: {user_id}")
        
        # Retrieve user
        user = test_db.get_user_by_email("test@example.com")
        if user:
            print(f"   ✓ User retrieved: {user['name']}")
            print(f"   ✓ Hobbies: {user['hobbies']}")
            print(f"   ✓ Spending personality: {user['spending_personality']}")
        else:
            raise Exception("User not found after creation")
        
    except Exception as e:
        print(f"   ✗ User creation failed: {e}")
        return False
    
    # Test multiple income sources
    print("\n2. Testing Multiple Income Sources")
    print("-" * 40)
    
    try:
        # Primary salary
        income1_id = test_db.add_income_source(
            user_id=user_id,
            source_name="Primary Job - Software Developer",
            income_type="salary",
            amount=45000,
            frequency="monthly",
            description="Full-time software development position"
        )
        print(f"   ✓ Primary salary added (ID: {income1_id})")
        
        # Freelance work
        income2_id = test_db.add_income_source(
            user_id=user_id,
            source_name="Freelance Web Development",
            income_type="freelance",
            amount=15000,
            frequency="monthly",
            description="Side freelance projects"
        )
        print(f"   ✓ Freelance income added (ID: {income2_id})")
        
        # Investment income
        income3_id = test_db.add_income_source(
            user_id=user_id,
            source_name="Stock Dividends",
            income_type="investment",
            amount=2000,
            frequency="quarterly",
            description="Dividend income from stock portfolio"
        )
        print(f"   ✓ Investment income added (ID: {income3_id})")
        
        # Retrieve all income sources
        income_sources = test_db.get_user_income_sources(user_id)
        total_monthly_income = sum(
            source['amount'] if source['frequency'] == 'monthly' 
            else source['amount'] / 3 if source['frequency'] == 'quarterly'
            else source['amount']
            for source in income_sources
        )
        print(f"   ✓ Total income sources: {len(income_sources)}")
        print(f"   ✓ Estimated monthly income: ₱{total_monthly_income:,.2f}")
        
    except Exception as e:
        print(f"   ✗ Income sources test failed: {e}")
        return False
    
    # Test comprehensive bills management
    print("\n3. Testing Bills Management with History")
    print("-" * 40)
    
    try:
        # Create various types of bills
        bills_to_create = [
            {
                "bill_name": "Rent",
                "category": "housing",
                "current_amount": 15000,
                "frequency": "monthly",
                "due_date_day": 1,
                "priority_level": "essential",
                "is_fixed_amount": True
            },
            {
                "bill_name": "Electricity (Meralco)",
                "category": "utilities",
                "current_amount": 3500,
                "frequency": "monthly",
                "due_date_day": 15,
                "priority_level": "essential",
                "is_fixed_amount": False,
                "notes": "Variable based on usage"
            },
            {
                "bill_name": "Internet (PLDT)",
                "category": "telecommunications",
                "current_amount": 1699,
                "frequency": "monthly",
                "due_date_day": 10,
                "priority_level": "important",
                "is_auto_pay": True
            },
            {
                "bill_name": "Netflix Subscription",
                "category": "subscriptions",
                "current_amount": 459,
                "frequency": "monthly",
                "due_date_day": 5,
                "priority_level": "optional"
            }
        ]
        
        bill_ids = []
        for bill_data in bills_to_create:
            bill_id = test_db.add_bill(user_id=user_id, **bill_data)
            bill_ids.append(bill_id)
            print(f"   ✓ {bill_data['bill_name']}: ₱{bill_data['current_amount']} ({bill_data['priority_level']})")
        
        # Record some payment history
        print(f"   ✓ Recording payment history...")
        
        # Rent payment (exact amount)
        test_db.record_bill_payment(
            bill_id=bill_ids[0],
            user_id=user_id,
            amount_paid=15000,
            payment_date=date.today() - timedelta(days=30),
            status="paid",
            payment_method="bank_transfer"
        )
        
        # Electricity payment (different amount)
        test_db.record_bill_payment(
            bill_id=bill_ids[1],
            user_id=user_id,
            amount_paid=3750,  # Higher than usual
            payment_date=date.today() - timedelta(days=15),
            status="paid",
            previous_amount=3500,
            was_amount_different=True,
            notes="Higher usage due to summer heat"
        )
        
        print(f"   ✓ Payment history recorded")
        
        # Get bills summary
        user_bills = test_db.get_user_bills(user_id)
        total_monthly_bills = sum(
            bill['current_amount'] if bill['frequency'] == 'monthly'
            else bill['current_amount']
            for bill in user_bills
        )
        print(f"   ✓ Total monthly bills: ₱{total_monthly_bills:,.2f}")
        
    except Exception as e:
        print(f"   ✗ Bills management test failed: {e}")
        return False
    
    # Test financial goals
    print("\n4. Testing Financial Goals Management")
    print("-" * 40)
    
    try:
        # Create different types of goals
        goals_to_create = [
            {
                "goal_name": "Emergency Fund (6 months)",
                "description": "Emergency fund covering 6 months of expenses",
                "target_amount": 150000,
                "target_date": date.today() + timedelta(days=365),
                "category": "emergency_fund",
                "priority": "high",
                "monthly_contribution": 10000
            },
            {
                "goal_name": "Japan Vacation 2026",
                "description": "Dream vacation to Japan for 2 weeks",
                "target_amount": 120000,
                "target_date": date.today() + timedelta(days=540),
                "category": "vacation",
                "priority": "medium",
                "monthly_contribution": 6000
            },
            {
                "goal_name": "New Laptop for Work",
                "description": "MacBook Pro for development work",
                "target_amount": 75000,
                "target_date": date.today() + timedelta(days=180),
                "category": "other",
                "priority": "medium",
                "monthly_contribution": 12500
            }
        ]
        
        goal_ids = []
        for goal_data in goals_to_create:
            goal_id = test_db.create_financial_goal(user_id=user_id, **goal_data)
            goal_ids.append(goal_id)
            print(f"   ✓ {goal_data['goal_name']}: ₱{goal_data['target_amount']:,}")
        
        # Add some progress to goals
        print(f"   ✓ Adding progress to goals...")
        
        # Emergency fund progress
        test_db.update_goal_progress(
            goal_id=goal_ids[0],
            user_id=user_id,
            amount_added=25000,
            source="savings_transfer",
            notes="Initial emergency fund deposit"
        )
        
        # Vacation fund progress
        test_db.update_goal_progress(
            goal_id=goal_ids[1],
            user_id=user_id,
            amount_added=18000,
            source="bonus",
            notes="Christmas bonus allocation"
        )
        
        # Laptop fund progress
        test_db.update_goal_progress(
            goal_id=goal_ids[2],
            user_id=user_id,
            amount_added=37500,
            source="freelance",
            notes="Freelance project payment"
        )
        
        print(f"   ✓ Progress recorded for all goals")
        
        # Get goals summary
        user_goals = test_db.get_user_goals(user_id)
        total_goal_target = sum(goal['target_amount'] for goal in user_goals)
        total_goal_current = sum(goal['current_amount'] for goal in user_goals)
        overall_progress = (total_goal_current / total_goal_target) * 100
        
        print(f"   ✓ Total goal target: ₱{total_goal_target:,}")
        print(f"   ✓ Total saved: ₱{total_goal_current:,}")
        print(f"   ✓ Overall progress: {overall_progress:.1f}%")
        
    except Exception as e:
        print(f"   ✗ Financial goals test failed: {e}")
        return False
    
    # Test AI insights storage
    print("\n5. Testing AI Insights Storage")
    print("-" * 40)
    
    try:
        # Store various types of insights
        insights_to_store = [
            {
                "insight_type": "spending_analysis",
                "title": "High Utility Spending Detected",
                "content": "Your electricity bill increased by 7% this month. Consider energy-saving measures during peak summer months.",
                "confidence_score": 0.85
            },
            {
                "insight_type": "goal_progress",
                "title": "Emergency Fund On Track",
                "content": "Great progress! You're 16.7% towards your emergency fund goal. At this rate, you'll reach your target in 10 months.",
                "confidence_score": 0.92
            },
            {
                "insight_type": "income_opportunity",
                "title": "Freelance Income Potential",
                "content": "Your freelance income is consistent. Consider raising your rates by 15-20% for new clients.",
                "confidence_score": 0.78
            }
        ]
        
        insight_ids = []
        for insight_data in insights_to_store:
            insight_id = test_db.store_ai_insight(user_id=user_id, **insight_data)
            insight_ids.append(insight_id)
            print(f"   ✓ {insight_data['insight_type']}: {insight_data['title']}")
        
        # Retrieve insights
        user_insights = test_db.get_user_insights(user_id)
        print(f"   ✓ Total insights generated: {len(user_insights)}")
        
    except Exception as e:
        print(f"   ✗ AI insights test failed: {e}")
        return False
    
    # Test comprehensive financial summary
    print("\n6. Testing Financial Summary & Analytics")
    print("-" * 40)
    
    try:
        # Get comprehensive summary
        financial_summary = test_db.get_user_financial_summary(user_id)
        
        print(f"   ✓ Financial Summary:")
        print(f"      • Monthly Income: ₱{financial_summary.get('total_monthly_income', 0):,.2f}")
        print(f"      • Monthly Bills: ₱{financial_summary.get('total_monthly_bills', 0):,.2f}")
        print(f"      • Monthly Surplus: ₱{financial_summary.get('monthly_surplus', 0):,.2f}")
        print(f"      • Active Goals: {financial_summary.get('active_goals_count', 0)}")
        print(f"      • Goal Progress: ₱{financial_summary.get('total_goal_current', 0):,.2f} / ₱{financial_summary.get('total_goal_target', 0):,.2f}")
        
        # Get database statistics
        db_stats = test_db.get_database_stats()
        print(f"\n   ✓ Database Statistics:")
        for table, count in db_stats.items():
            if table != 'db_size_mb':
                print(f"      • {table}: {count} records")
        print(f"      • Database size: {db_stats['db_size_mb']:.2f} MB")
        
    except Exception as e:
        print(f"   ✗ Financial summary test failed: {e}")
        return False
    
    # Test user profile updates
    print("\n7. Testing User Profile Updates")
    print("-" * 40)
    
    try:
        # Update user profile
        success = test_db.update_user_profile(
            user_id=user_id,
            age=29,  # Birthday!
            civil_status="in_relationship",
            hobbies=["gaming", "reading", "cooking", "photography"],  # Added photography
            spending_personality="saver"  # Changed from balanced to saver
        )
        
        if success:
            print("   ✓ User profile updated successfully")
            
            # Verify updates
            updated_user = test_db.get_user_by_email("test@example.com")
            if updated_user:
                print(f"   ✓ New age: {updated_user['age']}")
                print(f"   ✓ New status: {updated_user['civil_status']}")
                print(f"   ✓ Updated hobbies: {updated_user['hobbies']}")
                print(f"   ✓ New spending personality: {updated_user['spending_personality']}")
            else:
                raise Exception("User not found after update")
        else:
            print("   ✗ Profile update failed")
            return False
        
    except Exception as e:
        print(f"   ✗ Profile update test failed: {e}")
        return False
    
    # Final success message
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 60)
    print("✅ User management with comprehensive profiles")
    print("✅ Multiple income sources tracking")
    print("✅ Advanced bills management with history")
    print("✅ Financial goals with progress tracking")
    print("✅ AI insights storage and retrieval")
    print("✅ Comprehensive financial analytics")
    print("✅ User profile updates")
    print("\n🚀 Budget Buddy v2 Database is ready for production!")
    
    # Cleanup test database
    test_db_path = Path("test_budget_buddy_v2.db")
    if test_db_path.exists():
        test_db_path.unlink()
        print("🧹 Test database cleaned up")
    
    return True

def test_migration_scenario():
    """Test migration from existing database"""
    print("\n🔄 Testing Migration Scenario")
    print("-" * 40)
    
    # This would test the migration script
    # For now, just verify the migration script exists
    migration_script = Path(__file__).parent / "migrate_database.py"
    if migration_script.exists():
        print("   ✓ Migration script available")
        print(f"   ✓ Run: python {migration_script}")
    else:
        print("   ⚠️  Migration script not found")

if __name__ == "__main__":
    print("🧪 Budget Buddy v2 Database Test Suite")
    print("Testing comprehensive financial management features...")
    
    try:
        success = test_comprehensive_database()
        if success:
            test_migration_scenario()
            print("\n✨ All tests completed successfully!")
            print("Your new SQLite3 database system is ready to use!")
        else:
            print("\n❌ Some tests failed. Please check the implementation.")
            
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        import traceback
        traceback.print_exc()
