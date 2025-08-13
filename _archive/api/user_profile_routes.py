"""
Enhanced User Profile API Routes
Comprehensive user management with financial data
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from decimal import Decimal

from auth.dependencies import get_current_user
from common.database_v2 import db

user_profile_bp = APIRouter(prefix="/api/profile", tags=["user_profile"])

# ================================
# PYDANTIC MODELS
# ================================

class UserProfileUpdate(BaseModel):
    age: Optional[int] = None
    civil_status: Optional[str] = None
    number_of_dependents: Optional[int] = None
    number_of_kids: Optional[int] = None
    location: Optional[str] = None
    hobbies: Optional[List[str]] = None
    free_time_activities: Optional[List[str]] = None
    spending_personality: Optional[str] = None
    financial_goals_priority: Optional[str] = None

class IncomeSourceCreate(BaseModel):
    source_name: str
    income_type: str  # 'salary', 'freelance', 'business', etc.
    amount: float
    frequency: str  # 'weekly', 'monthly', etc.
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None

class IncomeSourceUpdate(BaseModel):
    source_name: Optional[str] = None
    income_type: Optional[str] = None
    amount: Optional[float] = None
    frequency: Optional[str] = None
    is_active: Optional[bool] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None

class BillCreate(BaseModel):
    bill_name: str
    category: str  # 'housing', 'utilities', etc.
    current_amount: float
    frequency: str  # 'monthly', 'weekly', etc.
    due_date_day: Optional[int] = None
    is_auto_pay: Optional[bool] = False
    payment_method: Optional[str] = None
    priority_level: Optional[str] = 'important'
    is_fixed_amount: Optional[bool] = True
    notes: Optional[str] = None

class BillPaymentRecord(BaseModel):
    amount_paid: float
    payment_date: date
    due_date: Optional[date] = None
    status: Optional[str] = 'paid'
    payment_method: Optional[str] = None
    was_amount_different: Optional[bool] = False
    previous_amount: Optional[float] = None
    late_fee: Optional[float] = 0
    notes: Optional[str] = None

class FinancialGoalCreate(BaseModel):
    goal_name: str
    description: Optional[str] = None
    target_amount: float
    target_date: date
    category: str
    priority: Optional[str] = 'medium'
    monthly_contribution: Optional[float] = 0
    auto_transfer: Optional[bool] = False

class GoalProgressUpdate(BaseModel):
    amount_added: float
    source: Optional[str] = 'manual'
    notes: Optional[str] = None

# ================================
# USER PROFILE ENDPOINTS
# ================================

@user_profile_bp.get("/me")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user's complete profile"""
    try:
        user = db.get_user_by_email(current_user['email'])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Remove sensitive data
        user.pop('hashed_password', None)
        
        return {
            "status": "success",
            "user": user
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_profile_bp.put("/me")
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile information"""
    try:
        # Get current user
        user = db.get_user_by_email(current_user['email'])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update profile
        update_data = profile_data.dict(exclude_unset=True)
        success = db.update_user_profile(user['id'], **update_data)
        
        if success:
            return {
                "status": "success",
                "message": "Profile updated successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="No changes made")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_profile_bp.get("/financial-summary")
async def get_financial_summary(current_user: dict = Depends(get_current_user)):
    """Get comprehensive financial summary"""
    try:
        user = db.get_user_by_email(current_user['email'])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        summary = db.get_user_financial_summary(user['id'])
        
        return {
            "status": "success",
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# INCOME MANAGEMENT ENDPOINTS
# ================================

@user_profile_bp.get("/income")
async def get_income_sources(current_user: dict = Depends(get_current_user)):
    """Get all income sources for current user"""
    try:
        user = db.get_user_by_email(current_user['email'])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        income_sources = db.get_user_income_sources(user['id'])
        
        return {
            "status": "success",
            "income_sources": income_sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_profile_bp.post("/income")
async def add_income_source(
    income_data: IncomeSourceCreate,
    current_user: dict = Depends(get_current_user)
):
    """Add a new income source"""
    try:
        user = db.get_user_by_email(current_user['email'])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        income_id = db.add_income_source(
            user_id=user['id'],
            **income_data.dict()
        )
        
        return {
            "status": "success",
            "message": "Income source added successfully",
            "income_id": income_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_profile_bp.put("/income/{income_id}")
async def update_income_source(
    income_id: int,
    income_data: IncomeSourceUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update an income source"""
    try:
        update_data = income_data.dict(exclude_unset=True)
        success = db.update_income_source(income_id, **update_data)
        
        if success:
            return {
                "status": "success",
                "message": "Income source updated successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Income source not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# BILLS MANAGEMENT ENDPOINTS
# ================================

@user_profile_bp.get("/bills")
async def get_user_bills(current_user: dict = Depends(get_current_user)):
    """Get all bills for current user"""
    try:
        user = db.get_user_by_email(current_user['email'])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        bills = db.get_user_bills(user['id'])
        
        return {
            "status": "success",
            "bills": bills
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_profile_bp.post("/bills")
async def add_bill(
    bill_data: BillCreate,
    current_user: dict = Depends(get_current_user)
):
    """Add a new bill"""
    try:
        user = db.get_user_by_email(current_user['email'])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        bill_id = db.add_bill(
            user_id=user['id'],
            **bill_data.dict()
        )
        
        return {
            "status": "success",
            "message": "Bill added successfully",
            "bill_id": bill_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_profile_bp.post("/bills/{bill_id}/payment")
async def record_bill_payment(
    bill_id: int,
    payment_data: BillPaymentRecord,
    current_user: dict = Depends(get_current_user)
):
    """Record a bill payment"""
    try:
        user = db.get_user_by_email(current_user['email'])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        payment_id = db.record_bill_payment(
            bill_id=bill_id,
            user_id=user['id'],
            **payment_data.dict()
        )
        
        return {
            "status": "success",
            "message": "Payment recorded successfully",
            "payment_id": payment_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_profile_bp.get("/bills/{bill_id}/history")
async def get_bill_payment_history(
    bill_id: int,
    limit: int = 12,
    current_user: dict = Depends(get_current_user)
):
    """Get payment history for a bill"""
    try:
        history = db.get_bill_payment_history(bill_id, limit)
        
        return {
            "status": "success",
            "payment_history": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# FINANCIAL GOALS ENDPOINTS
# ================================

@user_profile_bp.get("/goals")
async def get_financial_goals(current_user: dict = Depends(get_current_user)):
    """Get all financial goals for current user"""
    try:
        user = db.get_user_by_email(current_user['email'])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        goals = db.get_user_goals(user['id'])
        
        return {
            "status": "success",
            "goals": goals
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_profile_bp.post("/goals")
async def create_financial_goal(
    goal_data: FinancialGoalCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new financial goal"""
    try:
        user = db.get_user_by_email(current_user['email'])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        goal_id = db.create_financial_goal(
            user_id=user['id'],
            **goal_data.dict()
        )
        
        return {
            "status": "success",
            "message": "Financial goal created successfully",
            "goal_id": goal_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_profile_bp.post("/goals/{goal_id}/progress")
async def update_goal_progress(
    goal_id: int,
    progress_data: GoalProgressUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update progress on a financial goal"""
    try:
        user = db.get_user_by_email(current_user['email'])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        progress_id = db.update_goal_progress(
            goal_id=goal_id,
            user_id=user['id'],
            **progress_data.dict()
        )
        
        return {
            "status": "success",
            "message": "Goal progress updated successfully",
            "progress_id": progress_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# ANALYTICS ENDPOINTS
# ================================

@user_profile_bp.get("/analytics/spending-by-category")
async def get_spending_by_category(
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get spending breakdown by category"""
    try:
        user = db.get_user_by_email(current_user['email'])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        spending_data = db.calculate_user_spending_by_category(user['id'], days)
        
        return {
            "status": "success",
            "period_days": days,
            "spending_by_category": spending_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_profile_bp.get("/insights")
async def get_ai_insights(
    unread_only: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """Get AI-generated insights for the user"""
    try:
        user = db.get_user_by_email(current_user['email'])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        insights = db.get_user_insights(user['id'], unread_only)
        
        return {
            "status": "success",
            "insights": insights
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
