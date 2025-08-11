"""
Financial Goals API Routes
Provides endpoints for managing financial goals and tracking progress
"""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import json
from goals.goals_tracker import GoalsTracker, FinancialGoal

goals_bp = APIRouter(prefix="/api/goals", tags=["goals"])

# In-memory storage for demo (in production, use proper database)
user_goals_tracker = {}

# Pydantic models for request/response validation
class GoalCreate(BaseModel):
    name: str
    target_amount: float
    target_date: str
    category: Optional[str] = "general"
    priority: Optional[str] = "medium"
    monthly_contribution: Optional[float] = 0
    description: Optional[str] = None

class GoalUpdate(BaseModel):
    current_amount: Optional[float] = None
    monthly_contribution: Optional[float] = None

class SavingsAllocation(BaseModel):
    available_savings: float

class TemplateGoal(BaseModel):
    target_amount: float
    target_date: str
    monthly_contribution: Optional[float] = 0

def get_user_tracker(user_id: Optional[str] = None) -> GoalsTracker:
    """Get or create goals tracker for user"""
    if not user_id:
        user_id = 'demo_user'  # Default user for demo
    
    if user_id not in user_goals_tracker:
        user_goals_tracker[user_id] = GoalsTracker()
    
    return user_goals_tracker[user_id]

@goals_bp.get("")
async def get_goals():
    """Get all goals for the current user"""
    try:
        tracker = get_user_tracker()
        goals_data = []
        
        for goal in tracker.goals:
            goals_data.append({
                'id': goal.id,
                'name': goal.name,
                'target_amount': goal.target_amount,
                'current_amount': goal.current_amount,
                'target_date': goal.target_date.isoformat(),
                'category': goal.category,
                'priority': goal.priority,
                'monthly_contribution': goal.monthly_contribution,
                'progress_percentage': goal.progress_percentage,
                'remaining_amount': goal.remaining_amount,
                'months_remaining': goal.months_remaining,
                'required_monthly_contribution': goal.required_monthly_contribution,
                'is_on_track': goal.is_on_track,
                'description': goal.description
            })
        
        return {
            'status': 'success',
            'goals': goals_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@goals_bp.post("")
async def create_goal(goal_data: GoalCreate):
    """Create a new financial goal"""
    try:
        tracker = get_user_tracker()
        
        # Parse target date
        target_date = datetime.fromisoformat(goal_data.target_date.replace('Z', '+00:00'))
        
        goal = tracker.add_goal(
            name=goal_data.name,
            target_amount=goal_data.target_amount,
            target_date=target_date,
            category=goal_data.category or "general",
            priority=goal_data.priority or "medium",
            monthly_contribution=goal_data.monthly_contribution or 0,
            description=goal_data.description
        )
        
        return {
            'status': 'success',
            'message': 'Goal created successfully',
            'goal': {
                'id': goal.id,
                'name': goal.name,
                'target_amount': goal.target_amount,
                'current_amount': goal.current_amount,
                'target_date': goal.target_date.isoformat(),
                'category': goal.category,
                'priority': goal.priority,
                'monthly_contribution': goal.monthly_contribution,
                'progress_percentage': goal.progress_percentage
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@goals_bp.put("/{goal_id}")
async def update_goal_progress(goal_id: str, update_data: GoalUpdate):
    """Update progress for a specific goal"""
    try:
        tracker = get_user_tracker()
        
        if update_data.current_amount is not None:
            success = tracker.update_goal_progress(goal_id, update_data.current_amount)
            if not success:
                raise HTTPException(status_code=404, detail="Goal not found")
        
        goal = tracker.get_goal_by_id(goal_id)
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        if update_data.monthly_contribution is not None:
            goal.monthly_contribution = update_data.monthly_contribution
        
        return {
            'status': 'success',
            'message': 'Goal progress updated successfully',
            'goal': {
                'id': goal.id,
                'name': goal.name,
                'current_amount': goal.current_amount,
                'progress_percentage': goal.progress_percentage,
                'remaining_amount': goal.remaining_amount,
                'is_on_track': goal.is_on_track
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@goals_bp.get("/dashboard")
async def get_goals_dashboard():
    """Get goals dashboard summary"""
    try:
        tracker = get_user_tracker()
        summary = tracker.get_dashboard_summary()
        
        # Convert datetime objects to ISO format for JSON serialization
        dashboard_data = {
            'total_goals': summary.get('total_goals', 0),
            'total_target_amount': summary.get('total_target_amount', 0),
            'total_current_amount': summary.get('total_current_amount', 0),
            'overall_progress': summary.get('overall_progress', 0),
            'goals_on_track': summary.get('goals_on_track', 0),
            'upcoming_deadlines_data': [],
            'priority_goals_data': []
        }
        
        # Process upcoming deadlines
        for goal in summary.get('upcoming_deadlines', []):
            dashboard_data['upcoming_deadlines_data'].append({
                'id': goal.id,
                'name': goal.name,
                'target_date': goal.target_date.isoformat(),
                'progress_percentage': goal.progress_percentage,
                'remaining_amount': goal.remaining_amount
            })
        
        # Process priority goals
        for goal in summary.get('priority_goals', []):
            dashboard_data['priority_goals_data'].append({
                'id': goal.id,
                'name': goal.name,
                'priority': goal.priority,
                'progress_percentage': goal.progress_percentage,
                'is_on_track': goal.is_on_track
            })
        
        return {
            'status': 'success',
            'dashboard': dashboard_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@goals_bp.post("/suggestions")
async def get_savings_suggestions(allocation_data: SavingsAllocation):
    """Get suggestions for allocating savings across goals"""
    try:
        tracker = get_user_tracker()
        suggestions = tracker.suggest_monthly_allocations(allocation_data.available_savings)
        
        return {
            'status': 'success',
            'suggestions': suggestions
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@goals_bp.get("/templates")
async def get_goal_templates():
    """Get predefined goal templates"""
    try:
        tracker = get_user_tracker()
        templates = tracker.get_goal_templates()
        
        return {
            'status': 'success',
            'templates': templates
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@goals_bp.post("/template/{template_id}")
async def create_goal_from_template(template_id: str, template_data: TemplateGoal):
    """Create a goal from a predefined template"""
    try:
        tracker = get_user_tracker()
        target_date = datetime.fromisoformat(template_data.target_date.replace('Z', '+00:00'))
        
        goal = tracker.create_goal_from_template(
            template_id=template_id,
            target_amount=template_data.target_amount,
            target_date=target_date,
            monthly_contribution=template_data.monthly_contribution or 0
        )
        
        if not goal:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {
            'status': 'success',
            'message': 'Goal created from template successfully',
            'goal': {
                'id': goal.id,
                'name': goal.name,
                'target_amount': goal.target_amount,
                'target_date': goal.target_date.isoformat(),
                'category': goal.category,
                'priority': goal.priority,
                'description': goal.description
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
