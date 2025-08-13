import os
import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
import json

from common.resilience import ServiceClient, default_rate_limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["ai"])

# Response models
class TipResponse(BaseModel):
    tip: str
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    category: str = "general"

class InsightsResponse(BaseModel):
    analysis: str
    recommendations: List[str]
    optimization_tips: str
    emergency_advice: str
    market_insights: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    priority_ranking: List[str]

# Request models
class TipRequest(BaseModel):
    budget: Decimal = Field(gt=0, le=10000000)
    duration: str = Field(regex="^(daily|weekly|monthly)$")

class InsightsRequest(BaseModel):
    budget: Decimal = Field(gt=0, le=10000000)
    duration: str = Field(regex="^(daily|weekly|monthly)$")
    categories: Dict[str, Decimal] = Field(default_factory=dict)
    goals: Optional[List[str]] = Field(default_factory=list)

@router.post("/tip", response_model=TipResponse)
async def generate_tip(request: Request, body: TipRequest):
    """Get budget tip (deprecated - use gateway for AI insights)"""
    
    # Simple IP-based rate limiting
    client_id = request.client.host if request.client else "anonymous"
    if not default_rate_limiter.is_allowed(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # AI functionality moved to gateway.py with GROQ integration
    return TipResponse(
        tip="🤖 AI insights are now available through the main budget interface! Use the 'Calculate Budget' feature for intelligent recommendations powered by GROQ AI.",
        confidence=0.9,
        category="info"
    )

@router.post("/ai/insights", response_model=InsightsResponse)
async def get_ai_insights(request: Request, body: InsightsRequest):
    """Get AI insights (deprecated - use gateway for AI insights)"""
    
    # Simple IP-based rate limiting  
    client_id = request.client.host if request.client else "anonymous"
    if not default_rate_limiter.is_allowed(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # AI functionality moved to gateway.py with GROQ integration
    return InsightsResponse(
        analysis="AI insights are now powered by GROQ and available through the main budget interface.",
        recommendations=["Use the main budget calculator for intelligent recommendations", "All AI features are integrated in the gateway service"],
        optimization_tips="Access AI features through the main application interface",
        emergency_advice="Use the comprehensive budget calculator for personalized advice",
        market_insights="Real-time market insights available in main application",
        confidence_score=0.9,
        priority_ranking=["use_main_interface", "groq_powered_insights"]
    )

def get_current_market_insights() -> Dict[str, Any]:
    """Get current market trends (placeholder - deprecated)"""
    return {
        "status": "deprecated",
        "message": "Market insights available through GROQ integration in gateway"
    }
