from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Dict
from decimal import Decimal, ROUND_HALF_UP

class SavingsRequest(BaseModel):
    monthly_savings: Decimal = Field(..., gt=0, description="Monthly savings amount")
    emergency_fund: Decimal = Field(..., ge=0, description="Current emergency fund amount")
    current_goal: Decimal = Field(Decimal("50000"), gt=0, description="Emergency fund goal")

class SavingsForecast(BaseModel):
    monthly_projections: List[Decimal] = Field(..., description="Projected savings for 1, 2, 3, 6, and 12 months")
    emergency_fund_progress: Decimal = Field(..., description="Progress towards emergency fund goal as a percentage")
    what_if_scenarios: Dict[str, Decimal] = Field(..., description="Various what-if scenarios for savings analysis")
    
    class Config:
        schema_extra = {
            "example": {
                "monthly_projections": ["1000.00", "2000.00", "3000.00", "6000.00", "12000.00"],
                "emergency_fund_progress": "20.0",
                "what_if_scenarios": {
                    "monthly_10pct_more": "100.00",
                    "yearly_10pct_more": "1200.00",
                    "monthly_interest_gain": "3.33",
                    "months_to_goal": "48",
                    "months_with_increase": "44",
                    "months_saved": "4"
                }
            }
        }

app = FastAPI(title="Savings Service")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/forecast", response_model=SavingsForecast)
async def calculate_savings_forecast(request: SavingsRequest):
    try:
        # Calculate monthly projections (1, 2, 3, 6, 12 months)
        projections = []
        for months in [1, 2, 3, 6, 12]:
            amount = (request.monthly_savings * Decimal(str(months))).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            projections.append(amount)

        # Calculate emergency fund progress
        if request.current_goal == Decimal("0"):
            progress = Decimal("0")
        else:
            progress = (request.emergency_fund / request.current_goal * Decimal("100")).quantize(
                Decimal("0.1"), rounding=ROUND_HALF_UP
            )
            progress = min(progress, Decimal("100"))  # Cap at 100%

        # Calculate what-if scenarios
        
        # Monthly impact of 10% more savings
        monthly_savings_increase = (request.monthly_savings * Decimal("0.1")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        
        # Yearly impact of 10% more savings 
        yearly_savings_increase = (monthly_savings_increase * Decimal("12")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        
        # Calculate compound growth with a 4% annual interest rate (common for savings accounts)
        annual_interest_rate = Decimal("0.04")
        monthly_interest_rate = annual_interest_rate / Decimal("12")
        
        # Calculate monthly compound growth
        monthly_with_interest = (request.monthly_savings * (Decimal("1") + monthly_interest_rate)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        monthly_interest_gain = monthly_with_interest - request.monthly_savings
        
        # Calculate time to reach emergency fund goal (in months)
        remaining_to_goal = max(Decimal("0"), request.current_goal - request.emergency_fund)
        if request.monthly_savings > Decimal("0"):
            months_to_goal = (remaining_to_goal / request.monthly_savings).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )
        else:
            months_to_goal = Decimal("999")  # If monthly savings is zero
            
        # Time to reach goal with 10% more savings
        increased_monthly_savings = request.monthly_savings * Decimal("1.1")
        if increased_monthly_savings > Decimal("0"):
            months_to_goal_increased = (remaining_to_goal / increased_monthly_savings).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )
            time_saved = max(Decimal("0"), months_to_goal - months_to_goal_increased)
        else:
            months_to_goal_increased = Decimal("999")
            time_saved = Decimal("0")

        scenarios = {
            "monthly_10pct_more": monthly_savings_increase,
            "yearly_10pct_more": yearly_savings_increase,
            "monthly_interest_gain": monthly_interest_gain,
            "months_to_goal": months_to_goal,
            "months_with_increase": months_to_goal_increased,
            "months_saved": time_saved
        }

        return SavingsForecast(
            monthly_projections=projections,
            emergency_fund_progress=progress.quantize(Decimal("0.1")),
            what_if_scenarios=scenarios
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "savings"}

@app.get("/")
async def root():
    return {
        "message": "Savings service is running", 
        "version": "1.0.0",
        "endpoints": [
            {
                "path": "/forecast",
                "method": "POST",
                "description": "Calculate savings forecast based on monthly savings amount"
            },
            {
                "path": "/health",
                "method": "GET",
                "description": "Health check endpoint"
            }
        ]
    }

@app.get("/what-if-help")
async def what_if_explanation():
    """Explains the what-if scenarios provided by the forecast endpoint"""
    return {
        "scenarios": {
            "monthly_10pct_more": "Additional amount saved per month by increasing your savings rate by 10%",
            "yearly_10pct_more": "Additional amount saved per year by increasing your savings rate by 10%",
            "monthly_interest_gain": "Extra money earned in the first month from a 4% annual interest rate",
            "months_to_goal": "Estimated months to reach your emergency fund goal at current savings rate",
            "months_with_increase": "Estimated months to reach your goal with 10% increased savings rate",
            "months_saved": "Number of months saved by increasing your savings rate by 10%"
        },
        "formula_explanations": {
            "monthly_10pct_more": "monthly_savings * 0.1",
            "yearly_10pct_more": "monthly_10pct_more * 12",
            "monthly_interest_gain": "monthly_savings * (annual_interest_rate / 12)",
            "months_to_goal": "(goal_amount - current_amount) / monthly_savings",
            "months_with_increase": "(goal_amount - current_amount) / (monthly_savings * 1.1)"
        }
    }
