"""
Enhanced Database Manager for Budget Buddy v2
Comprehensive SQLite3 implementation with user financial management
"""

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime, date
from typing import Optional, Dict, Any, List, Union
from decimal import Decimal

logger = logging.getLogger(__name__)

class BudgetBuddyDatabase:
    """Enhanced database manager for comprehensive financial management"""
    
    def __init__(self, db_path: str = "budget_buddy_v2.db"):
        self.db_path = Path(db_path)
        self.init_database()
    
    def init_database(self):
        """Initialize database with schema if it doesn't exist"""
        print(f"🔍 Database path: {self.db_path}")
        print(f"🔍 Database exists: {self.db_path.exists()}")
        
        if not self.db_path.exists():
            print("📝 Database doesn't exist, creating with full schema...")
            self._create_database_schema()
        else:
            print("📁 Database exists, checking if empty...")
            is_empty = self._is_database_empty()
            print(f"🔍 Database is empty: {is_empty}")
            if is_empty:
                print("📝 Database is empty, creating full schema...")
                self._create_database_schema()
            else:
                print("✅ Database has tables, skipping schema creation")
    
    def _is_database_empty(self) -> bool:
        """Check if database exists but is empty"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                return len(tables) == 0
        except Exception:
            return True
    
    def _create_database_schema(self):
        """Create database schema from SQL file"""
        schema_file = Path(__file__).parent.parent / "database_schema_v2.sql"
        
        if not schema_file.exists():
            # If schema file doesn't exist, create basic tables
            self._create_basic_schema()
            return
        
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        with self.get_connection() as conn:
            # Use executescript for better SQL parsing
            conn.executescript(schema_sql)
            conn.commit()
            print(f"✅ Database schema created: {self.db_path}")
    
    def _create_basic_schema(self):
        """Create basic schema if SQL file is not available"""
        basic_schema = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            hashed_password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            age INTEGER,
            civil_status TEXT,
            number_of_dependents INTEGER DEFAULT 0,
            number_of_kids INTEGER DEFAULT 0,
            location TEXT,
            hobbies TEXT,
            free_time_activities TEXT,
            spending_personality TEXT,
            financial_goals_priority TEXT
        );
        
        CREATE TABLE IF NOT EXISTS user_income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            source_name TEXT NOT NULL,
            income_type TEXT NOT NULL,
            amount DECIMAL(12,2) NOT NULL,
            frequency TEXT NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS user_bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            bill_name TEXT NOT NULL,
            category TEXT NOT NULL,
            current_amount DECIMAL(10,2) NOT NULL,
            frequency TEXT NOT NULL DEFAULT 'monthly',
            due_date_day INTEGER,
            priority_level TEXT DEFAULT 'important',
            is_fixed_amount BOOLEAN DEFAULT 1,
            is_auto_pay BOOLEAN DEFAULT 0,
            notes TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        """
        
        with self.get_connection() as conn:
            conn.executescript(basic_schema)
            conn.commit()
    
    def get_connection(self):
        """Get a database connection with proper settings"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        return conn
    
    # ================================
    # USER MANAGEMENT
    # ================================
    
    def create_user(self, email: str, name: str, hashed_password: str, **kwargs) -> int:
        """Create a new user with optional profile data"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO users (email, name, hashed_password, age, civil_status, 
                                 number_of_dependents, number_of_kids, location, hobbies, 
                                 free_time_activities, spending_personality, financial_goals_priority)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                email, name, hashed_password,
                kwargs.get('age'),
                kwargs.get('civil_status'),
                kwargs.get('number_of_dependents', 0),
                kwargs.get('number_of_kids', 0),
                kwargs.get('location'),
                json.dumps(kwargs.get('hobbies', [])),
                json.dumps(kwargs.get('free_time_activities', [])),
                kwargs.get('spending_personality'),
                kwargs.get('financial_goals_priority')
            ))
            return cursor.lastrowid or 0
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email with all profile data"""
        with self.get_connection() as conn:
            row = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
            if row:
                user_dict = dict(row)
                # Parse JSON fields
                if user_dict.get('hobbies'):
                    user_dict['hobbies'] = json.loads(user_dict['hobbies'])
                if user_dict.get('free_time_activities'):
                    user_dict['free_time_activities'] = json.loads(user_dict['free_time_activities'])
                return user_dict
            return None
    
    def update_user_profile(self, user_id: int, **kwargs) -> bool:
        """Update user profile information"""
        # Prepare update fields
        fields = []
        values = []
        
        for field, value in kwargs.items():
            if field in ['age', 'civil_status', 'number_of_dependents', 'number_of_kids', 
                        'location', 'spending_personality', 'financial_goals_priority']:
                fields.append(f"{field} = ?")
                values.append(value)
            elif field in ['hobbies', 'free_time_activities']:
                fields.append(f"{field} = ?")
                values.append(json.dumps(value) if isinstance(value, list) else value)
        
        if not fields:
            return False
        
        fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(user_id)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE users SET {', '.join(fields)} WHERE id = ?
            ''', values)
            conn.commit()
            return cursor.rowcount > 0
    
    # ================================
    # INCOME MANAGEMENT
    # ================================
    
    def add_income_source(self, user_id: int, source_name: str, income_type: str, 
                         amount: float, frequency: str, **kwargs) -> int:
        """Add a new income source for user"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO user_income (user_id, source_name, income_type, amount, frequency,
                                       start_date, end_date, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, source_name, income_type, amount, frequency,
                kwargs.get('start_date'),
                kwargs.get('end_date'),
                kwargs.get('description')
            ))
            return cursor.lastrowid or 0
    
    def get_user_income_sources(self, user_id: int, active_only: bool = True) -> List[Dict]:
        """Get all income sources for a user"""
        query = 'SELECT * FROM user_income WHERE user_id = ?'
        params = [user_id]
        
        if active_only:
            query += ' AND is_active = 1'
        
        with self.get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]
    
    def update_income_source(self, income_id: int, **kwargs) -> bool:
        """Update an income source"""
        fields = []
        values = []
        
        allowed_fields = ['source_name', 'income_type', 'amount', 'frequency', 
                         'is_active', 'start_date', 'end_date', 'description']
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                fields.append(f"{field} = ?")
                values.append(value)
        
        if not fields:
            return False
        
        fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(income_id)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE user_income SET {', '.join(fields)} WHERE id = ?
            ''', values)
            conn.commit()
            return cursor.rowcount > 0
    
    # ================================
    # BILLS MANAGEMENT
    # ================================
    
    def add_bill(self, user_id: int, bill_name: str, category: str, current_amount: float,
                frequency: str, **kwargs) -> int:
        """Add a new bill for user"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO user_bills (user_id, bill_name, category, current_amount, frequency,
                                      due_date_day, is_auto_pay, payment_method, priority_level,
                                      is_fixed_amount, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, bill_name, category, current_amount, frequency,
                kwargs.get('due_date_day'),
                kwargs.get('is_auto_pay', False),
                kwargs.get('payment_method'),
                kwargs.get('priority_level', 'important'),
                kwargs.get('is_fixed_amount', True),
                kwargs.get('notes')
            ))
            return cursor.lastrowid or 0
    
    def get_user_bills(self, user_id: int, active_only: bool = True) -> List[Dict]:
        """Get all bills for a user"""
        query = 'SELECT * FROM user_bills WHERE user_id = ?'
        params = [user_id]
        
        if active_only:
            query += ' AND is_active = 1'
        
        query += ' ORDER BY category, bill_name'
        
        with self.get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]
    
    def record_bill_payment(self, bill_id: int, user_id: int, amount_paid: float,
                           payment_date: date, **kwargs) -> int:
        """Record a bill payment"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO bill_payment_history (bill_id, user_id, amount_paid, payment_date,
                                                 due_date, status, payment_method, previous_amount,
                                                 was_amount_different, late_fee, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                bill_id, user_id, amount_paid, payment_date,
                kwargs.get('due_date'),
                kwargs.get('status', 'paid'),
                kwargs.get('payment_method'),
                kwargs.get('previous_amount'),
                kwargs.get('was_amount_different', False),
                kwargs.get('late_fee', 0),
                kwargs.get('notes')
            ))
            return cursor.lastrowid or 0
    
    def get_bill_payment_history(self, bill_id: int, limit: int = 12) -> List[Dict]:
        """Get payment history for a bill"""
        with self.get_connection() as conn:
            rows = conn.execute('''
                SELECT * FROM bill_payment_history 
                WHERE bill_id = ? 
                ORDER BY payment_date DESC 
                LIMIT ?
            ''', (bill_id, limit)).fetchall()
            return [dict(row) for row in rows]
    
    # ================================
    # FINANCIAL GOALS
    # ================================
    
    def create_financial_goal(self, user_id: int, goal_name: str, target_amount: float,
                             target_date: date, category: str, **kwargs) -> int:
        """Create a new financial goal"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO financial_goals (user_id, goal_name, description, target_amount,
                                           current_amount, target_date, category, priority,
                                           monthly_contribution, auto_transfer)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, goal_name, kwargs.get('description'), target_amount,
                kwargs.get('current_amount', 0), target_date, category,
                kwargs.get('priority', 'medium'),
                kwargs.get('monthly_contribution', 0),
                kwargs.get('auto_transfer', False)
            ))
            return cursor.lastrowid or 0
    
    def get_user_goals(self, user_id: int, status: str = 'active') -> List[Dict]:
        """Get user's financial goals"""
        with self.get_connection() as conn:
            rows = conn.execute('''
                SELECT * FROM financial_goals 
                WHERE user_id = ? AND status = ?
                ORDER BY priority DESC, target_date ASC
            ''', (user_id, status)).fetchall()
            return [dict(row) for row in rows]
    
    def update_goal_progress(self, goal_id: int, user_id: int, amount_added: float,
                            source: str = 'manual', notes: str | None = None) -> int:
        """Add progress to a financial goal"""
        with self.get_connection() as conn:
            # Get current amount
            current_row = conn.execute(
                'SELECT current_amount FROM financial_goals WHERE id = ?', 
                (goal_id,)
            ).fetchone()
            
            if not current_row:
                raise ValueError("Goal not found")
            
            new_total = float(current_row['current_amount']) + amount_added
            
            # Update goal
            conn.execute('''
                UPDATE financial_goals 
                SET current_amount = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_total, goal_id))
            
            # Record progress entry
            cursor = conn.execute('''
                INSERT INTO goal_progress (goal_id, user_id, amount_added, new_total, 
                                         entry_date, source, notes)
                VALUES (?, ?, ?, ?, DATE('now'), ?, ?)
            ''', (goal_id, user_id, amount_added, new_total, source, notes))
            
            return cursor.lastrowid or 0
    
    # ================================
    # ANALYTICS & INSIGHTS
    # ================================
    
    def get_user_financial_summary(self, user_id: int) -> Dict:
        """Get comprehensive financial summary for user"""
        with self.get_connection() as conn:
            # Use the view we created
            row = conn.execute('''
                SELECT * FROM user_financial_summary WHERE user_id = ?
            ''', (user_id,)).fetchone()
            
            if row:
                return dict(row)
            return {}
    
    def calculate_user_spending_by_category(self, user_id: int, days: int = 30) -> Dict:
        """Calculate spending by category for analysis"""
        with self.get_connection() as conn:
            rows = conn.execute('''
                SELECT category, SUM(amount) as total_amount, COUNT(*) as transaction_count
                FROM user_transactions 
                WHERE user_id = ? 
                  AND transaction_type = 'expense'
                  AND transaction_date >= DATE('now', '-{} days')
                GROUP BY category
                ORDER BY total_amount DESC
            '''.format(days), (user_id,)).fetchall()
            
            return {row['category']: {
                'amount': float(row['total_amount']),
                'count': row['transaction_count']
            } for row in rows}
    
    def store_ai_insight(self, user_id: int, insight_type: str, title: str, 
                        content: str, **kwargs) -> int:
        """Store an AI-generated insight"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO ai_insights (user_id, insight_type, insight_title, insight_content,
                                       confidence_score, data_period_start, data_period_end,
                                       expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, insight_type, title, content,
                kwargs.get('confidence_score'),
                kwargs.get('data_period_start'),
                kwargs.get('data_period_end'),
                kwargs.get('expires_at')
            ))
            return cursor.lastrowid or 0
    
    def get_user_insights(self, user_id: int, unread_only: bool = False) -> List[Dict]:
        """Get AI insights for user"""
        query = '''
            SELECT * FROM ai_insights 
            WHERE user_id = ? AND is_dismissed = 0
        '''
        params = [user_id]
        
        if unread_only:
            query += ' AND is_read = 0'
        
        query += ' ORDER BY created_at DESC'
        
        with self.get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]
    
    # ================================
    # UTILITY METHODS
    # ================================
    
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        with self.get_connection() as conn:
            stats = {}
            
            tables = ['users', 'user_income', 'user_bills', 'financial_goals', 
                     'user_transactions', 'ai_insights']
            
            for table in tables:
                count = conn.execute(f'SELECT COUNT(*) as count FROM {table}').fetchone()
                stats[table] = count['count']
            
            # Database size
            stats['db_size_mb'] = self.db_path.stat().st_size / (1024 * 1024)
            
            return stats


# Global database instance
db = BudgetBuddyDatabase()

# Migration utility
def migrate_from_old_database(old_db_path: str, new_db: BudgetBuddyDatabase):
    """Migrate data from old database structure"""
    try:
        old_conn = sqlite3.connect(old_db_path)
        old_conn.row_factory = sqlite3.Row
        
        # Migrate users
        users = old_conn.execute('SELECT * FROM users').fetchall()
        for user in users:
            try:
                new_db.create_user(
                    email=user['email'],
                    name=user['name'],
                    hashed_password=user['hashed_password']
                )
                logger.info(f"Migrated user: {user['email']}")
            except Exception as e:
                logger.error(f"Failed to migrate user {user['email']}: {e}")
        
        # Migrate bills if they exist
        try:
            bills = old_conn.execute('SELECT * FROM bills').fetchall()
            for bill in bills:
                # You'd need to map old bill structure to new structure
                pass
        except sqlite3.OperationalError:
            logger.info("No bills table found in old database")
        
        old_conn.close()
        logger.info("Migration completed successfully")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


if __name__ == "__main__":
    # Test the database
    db = BudgetBuddyDatabase("test_budget_buddy.db")
    print("Database initialized successfully!")
    print("Stats:", db.get_database_stats())
