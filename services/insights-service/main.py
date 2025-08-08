from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum

class InsightType(str, Enum):
    SUCCESS = "success"
    WARNING = "warning"
    INFO = "info"

class HealthStatus(str, Enum):
    EXCELLENT = "excellent"
    ON_TRACK = "on_track"
    NEEDS_IMPROVEMENT = "needs_improvement"

class Insight(BaseModel):
    type: InsightType
    message: str

class BudgetBreakdown(BaseModel):
    categories: Dict[str, Decimal]
    total_essential: Decimal
    total_savings: Decimal

class SavingsForecast(BaseModel):
    monthly_projections: List[Decimal]
    emergency_fund_progress: Decimal
    what_if_scenarios: Dict[str, Decimal]

class InsightsRequest(BaseModel):
    budget_breakdown: BudgetBreakdown
    savings_data: SavingsForecast

class BudgetInsights(BaseModel):
    health_score: Decimal
    status: HealthStatus
    insights: List[Insight]
    recommendations: List[str]

app = FastAPI(title="Insights Service")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze", response_model=BudgetInsights)
async def analyze_budget(request: InsightsRequest):
    try:
        # Calculate health score based on multiple factors
        total_budget = sum(Decimal(str(val)) for val in request.budget_breakdown.categories.values())
        if total_budget == Decimal("0"):
            savings_rate = Decimal("0")
        else:
            savings_rate = (request.budget_breakdown.total_savings / total_budget * Decimal("100")).quantize(
                Decimal("0.1"), rounding=ROUND_HALF_UP
            )
        
        emergency_progress = request.savings_data.emergency_fund_progress
        
        # Base health score on savings rate and emergency fund progress
        health_score = (
            savings_rate * Decimal("0.6") + emergency_progress * Decimal("0.4")
        ).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
        
        # Determine status
        status = (
            HealthStatus.EXCELLENT if health_score >= Decimal("80")
            else HealthStatus.ON_TRACK if health_score >= Decimal("60")
            else HealthStatus.NEEDS_IMPROVEMENT
        )

        # Generate insights
        insights = []
        recommendations = []

        # Emergency fund insights
        if emergency_progress >= 75:
            insights.append(Insight(
                type=InsightType.SUCCESS,
                message=f"Strong emergency fund at {emergency_progress:.1f}% of goal"
            ))
            recommendations.append("Consider investing additional savings for long-term growth")
        elif emergency_progress >= 25:
            insights.append(Insight(
                type=InsightType.INFO,
                message=f"Building emergency fund: {emergency_progress:.1f}% of goal"
            ))
            recommendations.append("Stay consistent with emergency fund contributions")
        else:
            insights.append(Insight(
                type=InsightType.WARNING,
                message=f"Low emergency fund: {emergency_progress:.1f}% of goal"
            ))
            recommendations.append("Prioritize building your emergency fund")

        # Savings rate insights
        if savings_rate >= 20:
            insights.append(Insight(
                type=InsightType.SUCCESS,
                message=f"Healthy savings rate: {savings_rate:.1f}% of income"
            ))
        else:
            insights.append(Insight(
                type=InsightType.WARNING,
                message=f"Low savings rate: {savings_rate:.1f}% of income"
            ))
            recommendations.append("Look for ways to increase your savings rate to 20% or more")

        return BudgetInsights(
            health_score=health_score,
            status=status,
            insights=insights,
            recommendations=recommendations
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "insights"}

@app.get("/")
async def root():
    return {"message": "Insights service is running", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8083, reload=True)
