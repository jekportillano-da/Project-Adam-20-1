#!/usr/bin/env python3
"""
Check existing databases in the project
"""

import sqlite3
import os
from pathlib import Path

def check_database(db_name):
    """Check a database file and show its contents"""
    if not os.path.exists(db_name):
        print(f"❌ {db_name} - File not found")
        return
    
    try:
        print(f"\n📁 === {db_name} ===")
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("  🔍 No tables found (empty database)")
            conn.close()
            return
            
        print(f"  📋 Tables: {[t[0] for t in tables]}")
        
        # For each table, count rows and show structure
        for table in tables:
            table_name = table[0]
            
            # Count rows
            cursor.execute(f"SELECT COUNT(*) FROM [{table_name}]")
            count = cursor.fetchone()[0]
            
            # Get column info
            cursor.execute(f"PRAGMA table_info([{table_name}])")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            print(f"    📊 {table_name}: {count} rows")
            print(f"       Columns: {column_names}")
            
            # Show sample data if any
            if count > 0:
                cursor.execute(f"SELECT * FROM [{table_name}] LIMIT 2")
                samples = cursor.fetchall()
                print(f"       Sample: {samples[0] if samples else 'No data'}")
                
        conn.close()
        
    except Exception as e:
        print(f"  ❌ Error reading {db_name}: {e}")

def main():
    print("🔍 Checking existing databases in Budget Buddy project")
    print("=" * 60)
    
    # Check all .db files in the project
    db_files = list(Path('.').glob('*.db'))
    
    if not db_files:
        print("📭 No database files found")
        return
    
    # Focus on the main application databases
    main_databases = [
        'budget_app.db',
        'budget_assistant.db', 
        'budget_buddy_v2.db'
    ]
    
    print("🎯 Main Application Databases:")
    for db in main_databases:
        check_database(db)
    
    print(f"\n📋 All database files found:")
    for db_file in sorted(db_files):
        size_kb = db_file.stat().st_size / 1024
        print(f"  📁 {db_file.name}: {size_kb:.1f} KB")

if __name__ == "__main__":
    main()
