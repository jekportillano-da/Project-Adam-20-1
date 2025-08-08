import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = "budget_app.db"):
        self.db_path = Path(db_path)
        self.init_database()
    
    def get_connection(self):
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # This allows accessing columns by name
        return conn
    
    def init_database(self):
        """Initialize the database with required tables"""
        try:
            with self.get_connection() as conn:
                # Create users table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        hashed_password TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1
                    )
                ''')
                
                # Create bills table for user-specific bill data
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS bills (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        amount REAL NOT NULL,
                        due_date TEXT,
                        category TEXT,
                        is_recurring BOOLEAN DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                ''')
                
                # Create user_budgets table for storing budget data per user
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS user_budgets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        income REAL NOT NULL,
                        expenses REAL NOT NULL,
                        savings_goal REAL,
                        budget_data TEXT,  -- JSON string for complex data
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def create_user(self, name: str, email: str, hashed_password: str) -> Optional[int]:
        """Create a new user and return the user ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    'INSERT INTO users (name, email, hashed_password) VALUES (?, ?, ?)',
                    (name, email, hashed_password)
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                logger.warning(f"User with email {email} already exists")
                return None
            raise
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    'SELECT * FROM users WHERE email = ? AND is_active = 1',
                    (email,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    'SELECT * FROM users WHERE id = ? AND is_active = 1',
                    (user_id,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    def save_user_budget(self, user_id: int, income: float, expenses: float, 
                        savings_goal: float = None, budget_data: str = None) -> bool:
        """Save or update user budget data"""
        try:
            with self.get_connection() as conn:
                # Check if user already has budget data
                cursor = conn.execute(
                    'SELECT id FROM user_budgets WHERE user_id = ?',
                    (user_id,)
                )
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing budget
                    conn.execute('''
                        UPDATE user_budgets 
                        SET income = ?, expenses = ?, savings_goal = ?, 
                            budget_data = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    ''', (income, expenses, savings_goal, budget_data, user_id))
                else:
                    # Create new budget entry
                    conn.execute('''
                        INSERT INTO user_budgets (user_id, income, expenses, savings_goal, budget_data)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (user_id, income, expenses, savings_goal, budget_data))
                
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving user budget: {e}")
            return False
    
    def get_user_budget(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user budget data"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    'SELECT * FROM user_budgets WHERE user_id = ? ORDER BY updated_at DESC LIMIT 1',
                    (user_id,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting user budget: {e}")
            return None

# Global database instance
db = Database()
