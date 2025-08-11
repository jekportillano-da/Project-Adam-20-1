# Database Models and Implementation
from sqlalchemy import (
    Boolean, Column, Integer, String, DateTime, Text, 
    ForeignKey, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.types import Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
from decimal import Decimal as PyDecimal
from typing import Optional
import os

Base = declarative_base()

class User(Base):
    """User model with enhanced security"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    budget_entries = relationship("BudgetEntry", back_populates="user")
    savings_goals = relationship("SavingsGoal", back_populates="user")
    sessions = relationship("UserSession", back_populates="user")
    
    __table_args__ = (
        Index('ix_users_email', 'email'),
        Index('ix_users_created_at', 'created_at'),
    )

class UserSession(Base):
    """User session tracking for security"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    __table_args__ = (
        Index('ix_sessions_token', 'session_token'),
        Index('ix_sessions_user_id', 'user_id'),
        Index('ix_sessions_expires_at', 'expires_at'),
    )

class BudgetEntry(Base):
    """Budget calculation history"""
    __tablename__ = "budget_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(precision=12, scale=2), nullable=False)
    duration = Column(String(20), nullable=False)  # daily, weekly, monthly
    daily_equivalent = Column(Numeric(precision=12, scale=2), nullable=False)
    
    # Category allocations (stored as JSON or separate table)
    food_allocation = Column(Numeric(precision=12, scale=2))
    transportation_allocation = Column(Numeric(precision=12, scale=2))
    utilities_allocation = Column(Numeric(precision=12, scale=2))
    emergency_fund_allocation = Column(Numeric(precision=12, scale=2))
    discretionary_allocation = Column(Numeric(precision=12, scale=2))
    
    total_essential = Column(Numeric(precision=12, scale=2))
    total_savings = Column(Numeric(precision=12, scale=2))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="budget_entries")
    ai_tips = relationship("AITip", back_populates="budget_entry")
    
    __table_args__ = (
        CheckConstraint('amount > 0', name='check_positive_amount'),
        CheckConstraint(
            "duration IN ('daily', 'weekly', 'monthly')", 
            name='check_valid_duration'
        ),
        Index('ix_budget_entries_user_id', 'user_id'),
        Index('ix_budget_entries_created_at', 'created_at'),
    )

class SavingsGoal(Base):
    """User savings goals and tracking"""
    __tablename__ = "savings_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal_name = Column(String(255), nullable=False)
    target_amount = Column(Numeric(precision=12, scale=2), nullable=False)
    current_amount = Column(Numeric(precision=12, scale=2), default=0.0)
    monthly_contribution = Column(Numeric(precision=12, scale=2))
    target_date = Column(DateTime)
    
    is_emergency_fund = Column(Boolean, default=False)
    is_completed = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="savings_goals")
    contributions = relationship("SavingsContribution", back_populates="goal")
    
    __table_args__ = (
        CheckConstraint('target_amount > 0', name='check_positive_target'),
        CheckConstraint('current_amount >= 0', name='check_non_negative_current'),
        Index('ix_savings_goals_user_id', 'user_id'),
        Index('ix_savings_goals_target_date', 'target_date'),
    )

class SavingsContribution(Base):
    """Individual savings contributions"""
    __tablename__ = "savings_contributions"
    
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("savings_goals.id"), nullable=False)
    amount = Column(Numeric(precision=12, scale=2), nullable=False)
    contribution_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    
    # Relationships
    goal = relationship("SavingsGoal", back_populates="contributions")
    
    __table_args__ = (
        CheckConstraint('amount > 0', name='check_positive_contribution'),
        Index('ix_contributions_goal_id', 'goal_id'),
        Index('ix_contributions_date', 'contribution_date'),
    )

class AITip(Base):
    """AI-generated tips and recommendations"""
    __tablename__ = "ai_tips"
    
    id = Column(Integer, primary_key=True, index=True)
    budget_entry_id = Column(Integer, ForeignKey("budget_entries.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    tip_text = Column(Text, nullable=False)
    tip_category = Column(String(50))  # budgeting, savings, spending, etc.
    confidence_score = Column(Numeric(precision=4, scale=3))  # 0.000 to 1.000
    
    # AI model information
    model_used = Column(String(100))  # groq, openai, etc.
    model_version = Column(String(50))
    response_time_ms = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # User feedback
    user_rating = Column(Integer)  # 1-5 stars
    user_feedback = Column(Text)
    feedback_date = Column(DateTime)
    
    # Relationships
    budget_entry = relationship("BudgetEntry", back_populates="ai_tips")
    
    __table_args__ = (
        CheckConstraint(
            'user_rating IS NULL OR (user_rating >= 1 AND user_rating <= 5)',
            name='check_valid_rating'
        ),
        Index('ix_ai_tips_user_id', 'user_id'),
        Index('ix_ai_tips_created_at', 'created_at'),
        Index('ix_ai_tips_category', 'tip_category'),
    )

class SecurityLog(Base):
    """Security events logging"""
    __tablename__ = "security_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_type = Column(String(50), nullable=False)  # login, logout, failed_login, etc.
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    success = Column(Boolean, nullable=False)
    details = Column(Text)  # JSON string with additional details
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_security_logs_user_id', 'user_id'),
        Index('ix_security_logs_event_type', 'event_type'),
        Index('ix_security_logs_created_at', 'created_at'),
        Index('ix_security_logs_ip_address', 'ip_address'),
    )

class SystemMetrics(Base):
    """System performance and usage metrics"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Numeric(precision=15, scale=6), nullable=False)
    metric_unit = Column(String(20))  # ms, count, percentage, etc.
    
    # Context
    service_name = Column(String(50))  # gateway, budget, savings, insights
    endpoint = Column(String(255))
    
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_metrics_name_service', 'metric_name', 'service_name'),
        Index('ix_metrics_recorded_at', 'recorded_at'),
    )

# Database configuration and connection
class DatabaseManager:
    """Database connection and session management"""
    
    def __init__(self, database_url: Optional[str] = None):
        if database_url is None:
            database_url = os.getenv("DATABASE_URL", "sqlite:///./budget_assistant.db")
        
        self.engine = create_engine(
            database_url,
            # SQLite specific settings
            connect_args={"check_same_thread": False} if "sqlite" in database_url else {},
            # Connection pooling for production databases (not SQLite)
            pool_size=10 if "sqlite" not in database_url else 5,
            max_overflow=20 if "sqlite" not in database_url else 0,
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=self.engine
        )
    
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get database session"""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

# Global database instance
db_manager = DatabaseManager()

# Dependency for FastAPI
def get_db():
    """Database dependency for FastAPI"""
    return next(db_manager.get_session())

# Initialize database on import
try:
    db_manager.create_tables()
except Exception as e:
    print(f"Warning: Could not initialize database: {e}")
