#!/usr/bin/env python3
"""
Quick migration script to get Budget Buddy v2 working immediately.
This creates the database with essential tables and migrates existing users.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
import os

def create_budget_buddy_v2():
    """Create Budget Buddy v2 database with essential tables"""
    print("🚀 Creating Budget Buddy v2 Database")
    print("=" * 50)
    
    # Remove existing v2 database
    if os.path.exists('budget_buddy_v2.db'):
        os.remove('budget_buddy_v2.db')
        print("🧹 Removed existing v2 database")
    
    # Create new database
    conn = sqlite3.connect('budget_buddy_v2.db')
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Create essential tables
    print("📋 Creating essential tables...")
    
    # Enhanced Users table
    conn.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        hashed_password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1,
        
        -- Enhanced Profile Fields
        age INTEGER,
        civil_status TEXT CHECK(civil_status IN ('single', 'married', 'divorced', 'widowed', 'in_relationship')),
        number_of_dependents INTEGER DEFAULT 0,
        number_of_kids INTEGER DEFAULT 0,
        location TEXT,
        hobbies TEXT, -- JSON array
        free_time_activities TEXT, -- JSON array
        spending_personality TEXT CHECK(spending_personality IN ('saver', 'spender', 'balanced', 'investor')),
        financial_goals_priority TEXT
    )
    ''')
    
    # Income Sources
    conn.execute('''
    CREATE TABLE user_income (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        source_name TEXT NOT NULL,
        income_type TEXT NOT NULL CHECK(income_type IN ('salary', 'freelance', 'business', 'investment', 'other')),
        amount DECIMAL(12,2) NOT NULL,
        frequency TEXT NOT NULL CHECK(frequency IN ('weekly', 'bi_weekly', 'monthly', 'quarterly', 'annually')),
        description TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')
    
    # Enhanced Bills
    conn.execute('''
    CREATE TABLE user_bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        bill_name TEXT NOT NULL,
        category TEXT NOT NULL CHECK(category IN ('housing', 'utilities', 'insurance', 'subscriptions', 'loans', 'telecommunications', 'transportation', 'other')),
        current_amount DECIMAL(10,2) NOT NULL,
        due_date_day INTEGER,
        frequency TEXT NOT NULL CHECK(frequency IN ('weekly', 'monthly', 'quarterly', 'annually')) DEFAULT 'monthly',
        is_active BOOLEAN DEFAULT 1,
        is_auto_pay BOOLEAN DEFAULT 0,
        priority_level TEXT CHECK(priority_level IN ('essential', 'important', 'optional')) DEFAULT 'important',
        is_fixed_amount BOOLEAN DEFAULT 1,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')
    
    # Bill Payment History
    conn.execute('''
    CREATE TABLE bill_payment_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        amount_paid DECIMAL(10,2) NOT NULL,
        payment_date DATE NOT NULL,
        status TEXT CHECK(status IN ('paid', 'overdue', 'partial', 'cancelled')) DEFAULT 'paid',
        payment_method TEXT,
        was_amount_different BOOLEAN DEFAULT 0,
        previous_amount DECIMAL(10,2),
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (bill_id) REFERENCES user_bills(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')
    
    # Financial Goals
    conn.execute('''
    CREATE TABLE financial_goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        goal_name TEXT NOT NULL,
        description TEXT,
        target_amount DECIMAL(12,2) NOT NULL,
        current_amount DECIMAL(12,2) DEFAULT 0,
        target_date DATE NOT NULL,
        category TEXT NOT NULL CHECK(category IN ('emergency_fund', 'vacation', 'house_down_payment', 'car', 'education', 'retirement', 'debt_payoff', 'investment', 'other')),
        priority TEXT NOT NULL CHECK(priority IN ('high', 'medium', 'low')) DEFAULT 'medium',
        monthly_contribution DECIMAL(10,2) DEFAULT 0,
        status TEXT CHECK(status IN ('active', 'completed', 'paused', 'cancelled')) DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')
    
    # Goal Progress
    conn.execute('''
    CREATE TABLE goal_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        goal_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        amount_added DECIMAL(10,2) NOT NULL,
        new_total DECIMAL(10,2) NOT NULL,
        entry_date DATE NOT NULL,
        source TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (goal_id) REFERENCES financial_goals(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')
    
    # User Budgets
    conn.execute('''
    CREATE TABLE user_budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        budget_name TEXT NOT NULL,
        budget_month INTEGER NOT NULL,
        budget_year INTEGER NOT NULL,
        total_income DECIMAL(12,2) NOT NULL,
        budget_allocations TEXT NOT NULL, -- JSON
        actual_spending TEXT, -- JSON
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE(user_id, budget_month, budget_year)
    )
    ''')
    
    # AI Insights
    conn.execute('''
    CREATE TABLE ai_insights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        insight_type TEXT NOT NULL CHECK(insight_type IN ('spending_analysis', 'budget_recommendation', 'goal_progress', 'bill_optimization', 'income_opportunity')),
        insight_title TEXT NOT NULL,
        insight_content TEXT NOT NULL,
        confidence_score DECIMAL(3,2),
        is_read BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')
    
    # Create indexes
    print("📊 Creating indexes...")
    indexes = [
        "CREATE INDEX idx_user_income_user_id ON user_income(user_id)",
        "CREATE INDEX idx_user_bills_user_id ON user_bills(user_id)",
        "CREATE INDEX idx_financial_goals_user_id ON financial_goals(user_id)",
        "CREATE INDEX idx_ai_insights_user_id ON ai_insights(user_id)"
    ]
    
    for index in indexes:
        conn.execute(index)
    
    conn.commit()
    print(f"✅ Created {len(indexes)} indexes")
    
    # Get database statistics
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print(f"✅ Database created successfully!")
    print(f"📋 Tables created: {len(tables)}")
    for table in tables:
        print(f"   • {table[0]}")
    
    conn.close()
    return True

def migrate_existing_users():
    """Migrate users from budget_app.db to budget_buddy_v2.db"""
    print("\n🔄 Migrating existing users...")
    print("-" * 30)
    
    if not os.path.exists('budget_app.db'):
        print("⚠️ No budget_app.db found, skipping migration")
        return
    
    # Connect to both databases
    old_conn = sqlite3.connect('budget_app.db')
    new_conn = sqlite3.connect('budget_buddy_v2.db')
    
    old_conn.row_factory = sqlite3.Row
    
    try:
        # Get existing users
        old_cursor = old_conn.cursor()
        old_cursor.execute("SELECT * FROM users")
        users = old_cursor.fetchall()
        
        if not users:
            print("📭 No users to migrate")
            return
        
        print(f"👥 Found {len(users)} users to migrate")
        
        # Migrate each user
        new_cursor = new_conn.cursor()
        for user in users:
            new_cursor.execute('''
                INSERT INTO users (id, email, name, hashed_password, created_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user['id'], user['email'], user['name'], 
                user['hashed_password'], user['created_at'], user['is_active']
            ))
            print(f"   ✅ Migrated user: {user['name']} ({user['email']})")
        
        new_conn.commit()
        print(f"🎉 Successfully migrated {len(users)} users!")
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        new_conn.rollback()
    finally:
        old_conn.close()
        new_conn.close()

def test_new_database():
    """Test the new database functionality"""
    print("\n🧪 Testing new database functionality...")
    print("-" * 40)
    
    try:
        from common.database_v2 import BudgetBuddyDatabase
        
        # Test database connection
        db = BudgetBuddyDatabase('budget_buddy_v2.db')
        print("✅ Database connection successful")
        
        # Check table structure
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            
            expected_columns = ['age', 'civil_status', 'hobbies', 'spending_personality']
            found_columns = [col[1] for col in columns]
            
            missing = [col for col in expected_columns if col not in found_columns]
            
            if missing:
                print(f"❌ Missing columns: {missing}")
                return False
            else:
                print("✅ All expected columns present in users table")
                
            # Check user count
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"👥 Users in database: {user_count}")
            
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main execution"""
    print("🎯 Budget Buddy v2 Quick Setup")
    print("=" * 60)
    
    # Step 1: Create v2 database
    if create_budget_buddy_v2():
        print("✅ Step 1: Database creation successful")
    else:
        print("❌ Step 1: Database creation failed")
        return
    
    # Step 2: Migrate existing users
    migrate_existing_users()
    
    # Step 3: Test functionality
    if test_new_database():
        print("\n🎉 SUCCESS! Budget Buddy v2 is ready!")
        print("=" * 60)
        print("✅ Enhanced database with comprehensive financial management")
        print("✅ Existing users migrated successfully")
        print("✅ Ready for income sources, bills, goals, and AI insights")
        print("\n🚀 Next steps:")
        print("   1. Update auth system to use budget_buddy_v2.db")
        print("   2. Test the comprehensive API endpoints")
        print("   3. Begin frontend integration")
    else:
        print("\n❌ Setup completed but tests failed")
        print("Please check the database structure")

if __name__ == "__main__":
    main()
