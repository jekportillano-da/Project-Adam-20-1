#!/usr/bin/env python3
"""
Database Migration Script for Budget Buddy v2
Migrates from existing SQLite setup to comprehensive schema
"""

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime

from common.database_v2 import BudgetBuddyDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    """Handles migration from v1 to v2 database schema"""
    
    def __init__(self, old_db_path: str = "budget_app.db", new_db_path: str = "budget_buddy_v2.db"):
        self.old_db_path = Path(old_db_path)
        self.new_db_path = Path(new_db_path)
        self.new_db = BudgetBuddyDatabase(str(self.new_db_path))
        
    def migrate(self):
        """Execute complete migration"""
        logger.info("🚀 Starting Budget Buddy Database Migration")
        
        if not self.old_db_path.exists():
            logger.warning(f"Old database not found at {self.old_db_path}")
            logger.info("Creating fresh v2 database...")
            return True
        
        try:
            # Connect to old database
            old_conn = sqlite3.connect(self.old_db_path)
            old_conn.row_factory = sqlite3.Row
            
            # Migration steps
            self._migrate_users(old_conn)
            self._migrate_bills(old_conn)
            self._migrate_user_budgets(old_conn)
            
            old_conn.close()
            
            logger.info("✅ Migration completed successfully!")
            self._print_migration_summary()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            raise
    
    def _migrate_users(self, old_conn):
        """Migrate users table"""
        logger.info("📋 Migrating users...")
        
        try:
            users = old_conn.execute('SELECT * FROM users').fetchall()
            migrated_count = 0
            
            for user in users:
                try:
                    # Check if user already exists in new database
                    existing_user = self.new_db.get_user_by_email(user['email'])
                    if existing_user:
                        logger.info(f"   ↳ User {user['email']} already exists, skipping")
                        continue
                    
                    # Create user in new database
                    user_id = self.new_db.create_user(
                        email=user['email'],
                        name=user['name'],
                        hashed_password=user['hashed_password']
                    )
                    
                    logger.info(f"   ✓ Migrated user: {user['email']} (ID: {user_id})")
                    migrated_count += 1
                    
                except Exception as e:
                    logger.error(f"   ✗ Failed to migrate user {user['email']}: {e}")
            
            logger.info(f"   📊 Users migrated: {migrated_count}/{len(users)}")
            
        except sqlite3.OperationalError as e:
            if "no such table: users" in str(e):
                logger.warning("   ⚠️  No users table found in old database")
            else:
                raise
    
    def _migrate_bills(self, old_conn):
        """Migrate bills table"""
        logger.info("📋 Migrating bills...")
        
        try:
            bills = old_conn.execute('''
                SELECT b.*, u.email as user_email 
                FROM bills b 
                JOIN users u ON b.user_id = u.id
            ''').fetchall()
            
            migrated_count = 0
            
            for bill in bills:
                try:
                    # Get new user ID
                    user = self.new_db.get_user_by_email(bill['user_email'])
                    if not user:
                        logger.warning(f"   ⚠️  User {bill['user_email']} not found for bill {bill['name']}")
                        continue
                    
                    # Map old bill structure to new structure
                    bill_id = self.new_db.add_bill(
                        user_id=user['id'],
                        bill_name=bill['name'],
                        category=bill.get('category', 'other'),
                        current_amount=float(bill['amount']),
                        frequency='monthly',  # Default frequency
                        due_date_day=self._parse_due_date(bill.get('due_date')),
                        notes=f"Migrated from v1 database"
                    )
                    
                    logger.info(f"   ✓ Migrated bill: {bill['name']} for {bill['user_email']}")
                    migrated_count += 1
                    
                except Exception as e:
                    logger.error(f"   ✗ Failed to migrate bill {bill['name']}: {e}")
            
            logger.info(f"   📊 Bills migrated: {migrated_count}/{len(bills)}")
            
        except sqlite3.OperationalError as e:
            if "no such table: bills" in str(e):
                logger.warning("   ⚠️  No bills table found in old database")
            else:
                raise
    
    def _migrate_user_budgets(self, old_conn):
        """Migrate user_budgets table"""
        logger.info("📋 Migrating user budgets...")
        
        try:
            budgets = old_conn.execute('''
                SELECT ub.*, u.email as user_email 
                FROM user_budgets ub 
                JOIN users u ON ub.user_id = u.id
            ''').fetchall()
            
            migrated_count = 0
            
            for budget in budgets:
                try:
                    # Get new user ID
                    user = self.new_db.get_user_by_email(budget['user_email'])
                    if not user:
                        logger.warning(f"   ⚠️  User {budget['user_email']} not found for budget")
                        continue
                    
                    # Parse budget data if it's JSON
                    budget_data = budget.get('budget_data', '{}')
                    if isinstance(budget_data, str):
                        try:
                            budget_allocations = json.loads(budget_data)
                        except:
                            budget_allocations = {}
                    else:
                        budget_allocations = budget_data or {}
                    
                    # Create budget entry (you might need to adjust this based on your current budget structure)
                    current_date = datetime.now()
                    
                    with self.new_db.get_connection() as conn:
                        conn.execute('''
                            INSERT INTO user_budgets (user_id, budget_name, budget_month, budget_year,
                                                    total_income, budget_allocations, is_template)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            user['id'],
                            "Migrated Budget",
                            current_date.month,
                            current_date.year,
                            float(budget.get('income', 0)),
                            json.dumps(budget_allocations),
                            False
                        ))
                    
                    logger.info(f"   ✓ Migrated budget for {budget['user_email']}")
                    migrated_count += 1
                    
                except Exception as e:
                    logger.error(f"   ✗ Failed to migrate budget for {budget['user_email']}: {e}")
            
            logger.info(f"   📊 Budgets migrated: {migrated_count}/{len(budgets)}")
            
        except sqlite3.OperationalError as e:
            if "no such table: user_budgets" in str(e):
                logger.warning("   ⚠️  No user_budgets table found in old database")
            else:
                raise
    
    def _parse_due_date(self, due_date_str):
        """Parse due date from old format to day of month"""
        if not due_date_str:
            return None
        
        try:
            # Try to extract day from various date formats
            if isinstance(due_date_str, str):
                # Handle formats like "2024-01-15" or "15"
                if '-' in due_date_str:
                    return int(due_date_str.split('-')[-1])
                else:
                    day = int(due_date_str)
                    return day if 1 <= day <= 31 else None
            return None
        except:
            return None
    
    def _print_migration_summary(self):
        """Print migration summary"""
        stats = self.new_db.get_database_stats()
        
        logger.info("\n" + "="*50)
        logger.info("📊 MIGRATION SUMMARY")
        logger.info("="*50)
        
        for table, count in stats.items():
            if table != 'db_size_mb':
                logger.info(f"   {table}: {count} records")
        
        logger.info(f"   Database size: {stats['db_size_mb']:.2f} MB")
        logger.info("="*50)
        logger.info("✅ Migration completed successfully!")
        logger.info(f"New database created at: {self.new_db_path}")
        logger.info("You can now use the enhanced Budget Buddy v2 features!")

def main():
    """Main migration function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate Budget Buddy database to v2")
    parser.add_argument("--old-db", default="budget_app.db", help="Path to old database")
    parser.add_argument("--new-db", default="budget_buddy_v2.db", help="Path for new database")
    parser.add_argument("--backup", action="store_true", help="Backup old database before migration")
    
    args = parser.parse_args()
    
    # Backup old database if requested
    if args.backup and Path(args.old_db).exists():
        backup_path = f"{args.old_db}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        import shutil
        shutil.copy2(args.old_db, backup_path)
        logger.info(f"📁 Backup created: {backup_path}")
    
    # Run migration
    migrator = DatabaseMigrator(args.old_db, args.new_db)
    success = migrator.migrate()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print(f"Your new database is ready at: {args.new_db}")
        print("\nNext steps:")
        print("1. Update your application to use the new database")
        print("2. Test all functionality with the migrated data")
        print("3. Update your backup procedures for the new database")
    else:
        print("\n❌ Migration failed. Check the logs for details.")

if __name__ == "__main__":
    main()
