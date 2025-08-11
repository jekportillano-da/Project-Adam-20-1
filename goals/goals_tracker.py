"""
Budget Goals and Progress Tracking System
Allows users to set financial goals and track progress over time
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from decimal import Decimal
import json

@dataclass
class FinancialGoal:
    """Represents a financial goal"""
    id: str
    name: str
    target_amount: float
    current_amount: float
    target_date: datetime
    category: str  # emergency_fund, vacation, house_down_payment, etc.
    priority: str  # high, medium, low
    monthly_contribution: float
    created_date: datetime
    description: Optional[str] = None
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage"""
        if self.target_amount <= 0:
            return 0
        return min(100, (self.current_amount / self.target_amount) * 100)
    
    @property
    def remaining_amount(self) -> float:
        """Calculate remaining amount needed"""
        return max(0, self.target_amount - self.current_amount)
    
    @property
    def months_remaining(self) -> int:
        """Calculate months remaining to target date"""
        today = datetime.now()
        if self.target_date <= today:
            return 0
        return (self.target_date.year - today.year) * 12 + (self.target_date.month - today.month)
    
    @property
    def required_monthly_contribution(self) -> float:
        """Calculate required monthly contribution to meet goal"""
        months = self.months_remaining
        if months <= 0:
            return self.remaining_amount
        return self.remaining_amount / months
    
    @property
    def is_on_track(self) -> bool:
        """Check if goal is on track based on current contribution"""
        required = self.required_monthly_contribution
        return self.monthly_contribution >= required * 0.9  # 10% tolerance

class GoalsTracker:
    """Manages financial goals and tracks progress"""
    
    def __init__(self):
        self.goals: List[FinancialGoal] = []
    
    def add_goal(self, 
                name: str, 
                target_amount: float, 
                target_date: datetime,
                category: str = "general",
                priority: str = "medium",
                monthly_contribution: float = 0,
                description: Optional[str] = None) -> FinancialGoal:
        """Add a new financial goal"""
        
        goal_id = f"goal_{len(self.goals) + 1}_{datetime.now().strftime('%Y%m%d')}"
        
        goal = FinancialGoal(
            id=goal_id,
            name=name,
            target_amount=target_amount,
            current_amount=0,
            target_date=target_date,
            category=category,
            priority=priority,
            monthly_contribution=monthly_contribution,
            created_date=datetime.now(),
            description=description
        )
        
        self.goals.append(goal)
        return goal
    
    def update_goal_progress(self, goal_id: str, new_amount: float) -> bool:
        """Update the current amount for a goal"""
        for goal in self.goals:
            if goal.id == goal_id:
                goal.current_amount = new_amount
                return True
        return False
    
    def get_goal_by_id(self, goal_id: str) -> Optional[FinancialGoal]:
        """Get a specific goal by ID"""
        for goal in self.goals:
            if goal.id == goal_id:
                return goal
        return None
    
    def get_goals_by_category(self, category: str) -> List[FinancialGoal]:
        """Get all goals in a specific category"""
        return [goal for goal in self.goals if goal.category == category]
    
    def get_goals_by_priority(self, priority: str) -> List[FinancialGoal]:
        """Get all goals with specific priority"""
        return [goal for goal in self.goals if goal.priority == priority]
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get a summary for the goals dashboard"""
        if not self.goals:
            return {
                "total_goals": 0,
                "goals_on_track": 0,
                "total_target_amount": 0,
                "total_current_amount": 0,
                "overall_progress": 0,
                "upcoming_deadlines": [],
                "priority_goals": []
            }
        
        total_target = sum(goal.target_amount for goal in self.goals)
        total_current = sum(goal.current_amount for goal in self.goals)
        goals_on_track = sum(1 for goal in self.goals if goal.is_on_track)
        
        # Get goals with deadlines in next 3 months
        three_months_from_now = datetime.now() + timedelta(days=90)
        upcoming_deadlines = [
            goal for goal in self.goals 
            if goal.target_date <= three_months_from_now and goal.progress_percentage < 100
        ]
        
        # Get high priority goals
        priority_goals = self.get_goals_by_priority("high")
        
        return {
            "total_goals": len(self.goals),
            "goals_on_track": goals_on_track,
            "total_target_amount": total_target,
            "total_current_amount": total_current,
            "overall_progress": (total_current / total_target * 100) if total_target > 0 else 0,
            "upcoming_deadlines": upcoming_deadlines[:5],  # Top 5 upcoming
            "priority_goals": priority_goals[:3]  # Top 3 priority goals
        }
    
    def suggest_monthly_allocations(self, available_savings: float) -> Dict[str, Any]:
        """Suggest how to allocate monthly savings across goals"""
        if not self.goals or available_savings <= 0:
            return {"suggestions": [], "total_allocated": 0}
        
        # Sort goals by priority and urgency
        active_goals = [goal for goal in self.goals if goal.progress_percentage < 100]
        
        # Calculate urgency score and allocations
        goal_urgency = []
        for goal in active_goals:
            months_left = max(1, goal.months_remaining)
            urgency_multiplier = {"high": 3, "medium": 2, "low": 1}[goal.priority]
            urgency_score = (100 - goal.progress_percentage) * urgency_multiplier / months_left
            goal_urgency.append((goal, urgency_score))
        
        # Sort by urgency score
        goal_urgency.sort(key=lambda item: item[1], reverse=True)
        
        suggestions = []
        remaining_savings = available_savings
        
        for goal, urgency_score in goal_urgency:
            if remaining_savings <= 0:
                break
                
            # Calculate suggested allocation
            required = goal.required_monthly_contribution
            suggested = min(required, remaining_savings)
            
            if suggested > 0:
                suggestions.append({
                    "goal_id": goal.id,
                    "goal_name": goal.name,
                    "suggested_amount": suggested,
                    "required_amount": required,
                    "is_sufficient": suggested >= required,
                    "progress_after": goal.current_amount + suggested,
                    "target_amount": goal.target_amount
                })
                
                remaining_savings -= suggested
        
        return {
            "suggestions": suggestions,
            "total_allocated": available_savings - remaining_savings,
            "remaining_unallocated": remaining_savings
        }
    
    def get_goal_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get pre-defined goal templates"""
        return {
            "emergency_fund": {
                "name": "Emergency Fund (6 months expenses)",
                "category": "emergency_fund",
                "priority": "high",
                "description": "Build a safety net for unexpected expenses",
                "target_multiplier": 6,  # 6x monthly expenses
                "typical_timeframe_months": 12
            },
            "vacation_fund": {
                "name": "Dream Vacation",
                "category": "vacation",
                "priority": "medium",
                "description": "Save for a well-deserved vacation",
                "typical_amounts": [50000, 100000, 200000],
                "typical_timeframe_months": 8
            },
            "house_down_payment": {
                "name": "House Down Payment",
                "category": "real_estate",
                "priority": "high",
                "description": "Save for your first home down payment",
                "typical_amounts": [500000, 1000000, 2000000],
                "typical_timeframe_months": 24
            },
            "education_fund": {
                "name": "Education/Skills Development",
                "category": "education",
                "priority": "medium",
                "description": "Invest in learning and professional development",
                "typical_amounts": [25000, 50000, 100000],
                "typical_timeframe_months": 6
            },
            "business_capital": {
                "name": "Business Starting Capital",
                "category": "business",
                "priority": "high",
                "description": "Capital for starting your own business",
                "typical_amounts": [100000, 300000, 500000],
                "typical_timeframe_months": 18
            },
            "retirement_fund": {
                "name": "Retirement Savings",
                "category": "retirement",
                "priority": "high",
                "description": "Long-term retirement planning",
                "target_multiplier": 300,  # 25x annual expenses (4% rule)
                "typical_timeframe_months": 360  # 30 years
            }
        }
    
    def create_goal_from_template(self, 
                                template_id: str, 
                                target_amount: float, 
                                target_date: datetime,
                                monthly_contribution: float = 0) -> Optional[FinancialGoal]:
        """Create a goal from a predefined template"""
        templates = self.get_goal_templates()
        template = templates.get(template_id)
        
        if not template:
            return None
        
        return self.add_goal(
            name=template["name"],
            target_amount=target_amount,
            target_date=target_date,
            category=template["category"],
            priority=template["priority"],
            monthly_contribution=monthly_contribution,
            description=template["description"]
        )
