from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from enum import Enum
from typing import Dict, Optional
from decimal import Decimal, ROUND_HALF_UP

class Duration(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class BudgetRequest(BaseModel):
    amount: Decimal = Field(..., gt=0, le=1000000, description="Budget amount between 0 and 1,000,000")
    duration: Duration = Field(..., description="Budget duration: daily, weekly, or monthly")

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        if v > 1000000:
            raise ValueError("Amount cannot exceed 1,000,000")
        return v.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

class BudgetBreakdown(BaseModel):
    categories: Dict[str, Decimal]
    total_essential: Decimal
    total_savings: Decimal

    class Config:
        json_encoders = {
            Decimal: lambda v: str(v.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        }

app = FastAPI(
    title="Budget Service",
    description="Service for calculating budget breakdowns and allocations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/calculate", response_model=BudgetBreakdown)
async def calculate_budget(request: BudgetRequest):
    try:
        # Normalize values to match the selected time period
        # If user enters a monthly budget but selects "daily", we divide by 30
        # If user enters a monthly budget but selects "weekly", we divide by 4.33
        # If user selects "monthly", we keep as is (we assume entered amount is monthly)
        
        # First, let's handle the input as a monthly budget
        monthly_budget = request.amount
        
        # Then apply the divisor based on the selected time period
        divisor = Decimal(
            "30" if request.duration == Duration.DAILY
            else "4.33" if request.duration == Duration.WEEKLY
            else "1"
        )
        
        # Calculate the adjusted amount for the selected time period
        adjusted_amount = (monthly_budget / divisor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Define category percentages
        percentages = {
            "food": Decimal("0.30"),
            "transportation": Decimal("0.15"),
            "utilities": Decimal("0.20"),
            "emergency_fund": Decimal("0.20"),
            "discretionary": Decimal("0.15")
        }

        # Calculate breakdowns with proper decimal handling
        categories = {}
        for category, percentage in percentages.items():
            amount = (adjusted_amount * percentage).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            categories[category] = amount

        # Calculate totals with safe decimal handling
        total_essential = Decimal("0")
        for cat in ["food", "transportation", "utilities"]:
            total_essential += categories[cat]
        total_essential = total_essential.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        total_savings = (categories["emergency_fund"] + categories["discretionary"]).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        return BudgetBreakdown(
            categories=categories,
            total_essential=total_essential,
            total_savings=total_savings
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "budget"}

@app.get("/")
async def root():
    return {"message": "Budget service is running", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
