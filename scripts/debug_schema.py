#!/usr/bin/env python3
"""
Debug script to test database schema creation
"""

import sqlite3
import os
from pathlib import Path

def test_direct_schema_loading():
    """Test loading schema directly"""
    print("🧪 Testing Direct Schema Loading")
    print("-" * 40)
    
    # Remove test database if exists
    if os.path.exists('test_schema_debug.db'):
        os.remove('test_schema_debug.db')
    
    # Read schema file
    schema_file = Path('database_schema_v2.sql')
    print(f"📁 Schema file: {schema_file}")
    print(f"✅ Exists: {schema_file.exists()}")
    
    if not schema_file.exists():
        print("❌ Schema file not found!")
        return False
    
    try:
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        print(f"📊 Schema size: {len(schema_sql)} characters")
        
        # Create database and execute schema
        conn = sqlite3.connect('test_schema_debug.db')
        conn.executescript(schema_sql)
        conn.commit()
        
        # Check tables
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"📋 Tables created: {[t[0] for t in tables]}")
        
        # Check users table structure
        cursor.execute("PRAGMA table_info(users);")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        print(f"👤 Users table columns ({len(column_names)}): {column_names}")
        
        # Check for our expected columns
        expected = ['age', 'civil_status', 'hobbies', 'spending_personality']
        found = [col for col in expected if col in column_names]
        missing = [col for col in expected if col not in column_names]
        
        print(f"✅ Expected columns found: {found}")
        if missing:
            print(f"❌ Missing columns: {missing}")
        else:
            print("🎉 All expected columns present!")
        
        conn.close()
        return len(missing) == 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_database_v2_creation():
    """Test using the actual BudgetBuddyDatabase class"""
    print("\n🧪 Testing BudgetBuddyDatabase Class")
    print("-" * 40)
    
    # Remove test database if exists
    if os.path.exists('test_db_v2_debug.db'):
        os.remove('test_db_v2_debug.db')
    
    try:
        from common.database_v2 import BudgetBuddyDatabase
        
        print("📦 Creating BudgetBuddyDatabase instance...")
        db = BudgetBuddyDatabase('test_db_v2_debug.db')
        
        # Check the created database
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"📋 Tables created: {[t[0] for t in tables]}")
            
            cursor.execute("PRAGMA table_info(users);")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            print(f"👤 Users table columns ({len(column_names)}): {column_names}")
            
            # Check for expected columns
            expected = ['age', 'civil_status', 'hobbies', 'spending_personality']
            found = [col for col in expected if col in column_names]
            missing = [col for col in expected if col not in column_names]
            
            print(f"✅ Expected columns found: {found}")
            if missing:
                print(f"❌ Missing columns: {missing}")
                print("🔍 This suggests the basic schema fallback is being used")
                return False
            else:
                print("🎉 All expected columns present!")
                return True
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔍 Database Schema Creation Debug")
    print("=" * 50)
    
    # Test 1: Direct schema loading
    direct_success = test_direct_schema_loading()
    
    # Test 2: Database class
    class_success = test_database_v2_creation()
    
    print("\n" + "=" * 50)
    print("📊 RESULTS:")
    print(f"  Direct schema loading: {'✅ SUCCESS' if direct_success else '❌ FAILED'}")
    print(f"  BudgetBuddyDatabase class: {'✅ SUCCESS' if class_success else '❌ FAILED'}")
    
    if direct_success and not class_success:
        print("\n🔍 DIAGNOSIS: Schema file is valid, but BudgetBuddyDatabase is using fallback schema")
        print("💡 SOLUTION: Check the schema file path resolution in the class")
    elif not direct_success:
        print("\n🔍 DIAGNOSIS: Issue with schema file itself")
    else:
        print("\n🎉 Everything working correctly!")

if __name__ == "__main__":
    main()
