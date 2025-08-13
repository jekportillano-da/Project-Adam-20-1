#!/usr/bin/env python3
"""
Quick SQLite3 availability test
"""

def test_sqlite3_availability():
    try:
        import sqlite3
        print("✅ SQLite3 module is available!")
        print(f"SQLite3 version: {sqlite3.sqlite_version}")
        print(f"Python sqlite3 module available: {sqlite3.__file__}")
        
        # Test creating a simple database
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE test (id INTEGER, name TEXT)')
        cursor.execute('INSERT INTO test (id, name) VALUES (1, "Hello SQLite")')
        cursor.execute('SELECT * FROM test')
        result = cursor.fetchone()
        conn.close()
        
        print(f"✅ SQLite3 functionality test passed: {result}")
        return True
        
    except ImportError:
        print("❌ SQLite3 module not available")
        return False
    except Exception as e:
        print(f"❌ SQLite3 test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing SQLite3 availability...")
    if test_sqlite3_availability():
        print("\n🎉 SQLite3 is ready to use!")
        print("Your database implementation should work correctly.")
    else:
        print("\n⚠️  SQLite3 needs to be installed or configured.")
