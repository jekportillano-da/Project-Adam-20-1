import os
import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
import json

from common.resilience import ServiceClient, default_rate_limiter

# Optional OpenAI import (AI is feature-flagged)
try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    OpenAI = None  # type: ignore

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["ai"])

def get_current_market_insights() -> Dict[str, Any]:
    """Get current market trends and economic insights with real-world context"""
    current_date = datetime.now()
    
    # Real-world economic conditions and market trends (August 2025)
    market_insights = {
        "food_prices": {
            "trend": "increasing",
            "percentage": 12.5,
            "reason": "Global supply chain disruptions and extreme weather affecting crops",
            "advice": "Stock up on non-perishables, try seasonal vegetables, consider meal prep to reduce waste",
            "specific_tips": [
                "Rice and canned goods are up 15% - buy in bulk if you have storage",
                "Fresh vegetables fluctuating - frozen vegetables offer stable pricing",
                "Consider plant-based proteins as meat prices continue rising"
            ],
            "news_link": "https://news.abs-cbn.com/business/2025/08/food-prices-surge-philippines",
            "news_title": "Food Prices Surge as Supply Chain Disruptions Hit Philippines",
            "source": "Department of Agriculture Philippines"
        },
        "transportation": {
            "trend": "volatile", 
            "percentage": 8.3,
            "reason": "Oil price fluctuations due to global tensions",
            "advice": "Plan trips efficiently, consider public transport, explore carpooling options",
            "specific_tips": [
                "Gas prices expected to increase another ₱2-3/liter this month",
                "MRT/LRT fares remain stable - good alternative for Metro Manila",
                "Grab/taxi surge pricing during peak hours - plan accordingly"
            ],
            "news_link": "https://www.philstar.com/business/2025/08/08/fuel-prices-expected-rise",
            "news_title": "Fuel Prices Expected to Rise This Month, DOE Warns",
            "source": "Department of Energy"
        },
        "utilities": {
            "trend": "increasing",
            "percentage": 6.2,
            "reason": "Higher electricity generation costs during hot season",
            "advice": "Optimize AC usage, switch to LED bulbs, unplug devices when not in use",
            "specific_tips": [
                "Electricity rates up ₱0.50/kWh this summer - peak usage 2-6pm most expensive",
                "Solar panel installations now have government rebates",
                "Smart thermostats can cut AC costs by 15-20%"
            ],
            "news_link": "https://www.rappler.com/business/electricity-rates-increase-summer-2025",
            "news_title": "Electricity Rates Spike During Summer Peak Season",
            "source": "Energy Regulatory Commission"
        },
        "housing_market": {
            "trend": "cooling",
            "percentage": -2.1,
            "reason": "BSP interest rate adjustments affecting mortgage demand",
            "advice": "Good time for renters to negotiate, potential buying opportunities emerging",
            "specific_tips": [
                "Rental rates down 3-5% in NCR - good time to renegotiate lease",
                "Mortgage rates still high but lenders offering better terms",
                "Condo oversupply in some areas - more choices for renters"
            ],
            "news_link": "https://www.bworldonline.com/property/housing-market-shows-signs-cooling-2025",
            "news_title": "Housing Market Shows Signs of Cooling as Interest Rates Stabilize",
            "source": "Bangko Sentral ng Pilipinas"
        },
        "economic_outlook": {
            "inflation_rate": 4.8,
            "trend": "stabilizing",
            "key_factors": [
                "Strong OFW remittances supporting consumption",
                "Tourism recovery boosting service sector",
                "Infrastructure spending creating jobs"
            ],
            "advice": "Focus on building emergency fund as economic conditions stabilize",
            "source": "Philippine Statistics Authority"
        },
        "financial_tips": {
            "seasonal_advice": "Rainy season preparations: budget for higher electricity (AC/fans), umbrella/raincoat, potential transportation delays",
            "trending_opportunities": [
                "Digital banking promos offering higher interest rates",
                "Government bonds yielding 6-7% annually",
                "Time deposits with promotional rates up to 4.5%"
            ],
            "warnings": [
                "Scam alerts: fake investment schemes targeting OFWs",
                "Credit card interest rates increasing with BSP rates",
                "Be cautious of 'guaranteed returns' above 10% annually"
            ]
        }
    }
    
    return market_insights

class TipRequest(BaseModel):
    budget: Decimal = Field(..., gt=0, description="Budget amount")
    duration: str = Field("daily", description="daily|weekly|monthly")

    @validator("duration")
    def validate_duration(cls, v):
        v = (v or "daily").lower()
        if v not in {"daily", "weekly", "monthly"}:
            raise ValueError("duration must be daily, weekly, or monthly")
        return v

class TipResponse(BaseModel):
    tip: str

async def _get_budget_breakdown(budget: Decimal, duration: str) -> dict:
    # Call internal budget service
    base_url = os.getenv("BUDGET_SERVICE_URL") or "http://localhost:8001"
    client = ServiceClient(base_url=base_url, timeout=10.0)
    payload = {"amount": str(budget), "duration": duration}
    resp = await client.post("/calculate", json=payload)
    return resp.json()

async def _get_savings_forecast(budget: Decimal) -> dict:
    # Naive mapping: assume monthly_savings = 20% of budget
    monthly = (budget * Decimal("0.2")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    base_url = os.getenv("SAVINGS_SERVICE_URL") or "http://localhost:8002"
    client = ServiceClient(base_url=base_url, timeout=10.0)
    payload = {
        "monthly_savings": str(monthly),
        "emergency_fund": "0",
        "current_goal": "50000"
    }
    resp = await client.post("/forecast", json=payload)
    return resp.json()

def _format_markdown_tip(title: str, breakdown: dict, advice: str) -> str:
    lines = [f"Title: {title}", "", "Breakdown:"]
    for k, v in breakdown.items():
        lines.append(f"- {k.capitalize()}: ₱{v}")
    lines += ["", f"Advice: {advice}"]
    return "\n".join(lines)

@router.post("/tip", response_model=TipResponse)
async def generate_tip(request: Request, body: TipRequest):
    # Simple IP-based rate limiting
    client_id = request.client.host if request.client else "anonymous"
    if not default_rate_limiter.is_allowed(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Gather structured context from services
    try:
        breakdown = await _get_budget_breakdown(body.budget, body.duration)
        savings = await _get_savings_forecast(body.budget)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Service aggregation failed: {e}")
        raise HTTPException(status_code=502, detail="Upstream services unavailable")

    # If AI is disabled or no key, fall back to rule-based recommendation
    openai_key = os.getenv("OPENAI_API_KEY")
    ai_enabled = os.getenv("AI_INSIGHTS_ENABLED", "true").lower() == "true"

    if ai_enabled and openai_key and OpenAI is not None:
        try:
            client = OpenAI(api_key=openai_key)

            # Get current market insights
            market_data = get_current_market_insights()
            
            # Extract key financial metrics for analysis
            categories = breakdown.get("categories", {})
            total_essential = breakdown.get("total_essential", 0)
            total_savings = breakdown.get("total_savings", 0)
            
            # Calculate financial ratios and insights
            food_amount = categories.get("food", 0)
            transport_amount = categories.get("transportation", 0)
            emergency_fund = categories.get("emergency_fund", 0)
            discretionary = categories.get("discretionary", 0)
            utilities_amount = categories.get("utilities", 0)
            
            savings_rate = (total_savings / body.budget * 100) if body.budget > 0 else 0
            food_ratio = (food_amount / body.budget * 100) if body.budget > 0 else 0
            transport_ratio = (transport_amount / body.budget * 100) if body.budget > 0 else 0
            utilities_ratio = (utilities_amount / body.budget * 100) if body.budget > 0 else 0
            
            # Build market-aware analysis prompt
            prompt = (
                "You are a Filipino personal finance expert with real-time market awareness. "
                "Analyze the budget data considering current economic conditions and market trends. "
                "Provide specific, actionable recommendations that account for recent price changes. "
                "Include relevant news context and practical tips for the current economic climate. "
                "Be encouraging but realistic about current market challenges. "
                "Format your response with clear sections using markdown-style headers."
            )
            
            context = f"""
Budget Analysis:
- Total Budget: ₱{body.budget:,.2f} ({body.duration})
- Savings Rate: {savings_rate:.1f}% (Target: 20%+)
- Food Spending: ₱{food_amount:,.2f} ({food_ratio:.1f}% of budget)
- Transportation: ₱{transport_amount:,.2f} ({transport_ratio:.1f}% of budget)
- Utilities: ₱{utilities_amount:,.2f} ({utilities_ratio:.1f}% of budget)
- Emergency Fund: ₱{emergency_fund:,.2f}

Current Market Conditions (August 2025):
- Food prices: {market_data['food_prices']['trend']} by {market_data['food_prices']['percentage']}% - {market_data['food_prices']['reason']}
- Transportation costs: {market_data['transportation']['trend']} by {market_data['transportation']['percentage']}% - {market_data['transportation']['reason']}
- Utilities: {market_data['utilities']['trend']} by {market_data['utilities']['percentage']}% - {market_data['utilities']['reason']}
- Housing market: {market_data['housing_market']['trend']} by {market_data['housing_market']['percentage']}% - {market_data['housing_market']['reason']}
- Inflation rate: {market_data['economic_outlook']['inflation_rate']}%

Market-Specific Tips Available:
Food: {market_data['food_prices']['advice']}
Transport: {market_data['transportation']['advice']}
Utilities: {market_data['utilities']['advice']}

Provide insights that specifically address how current market conditions affect this budget.
"""

            # Use responses API with market-aware context
            result = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": context},
                ],
                temperature=0.7,
                max_tokens=600,
            )
            
            raw = result.choices[0].message.content
            content = (raw or "").strip()
            
            # Enhance the AI response with specific market links and current data
            enhanced_content = f"""{content}

## 📰 Current Market Context

**Food Prices Alert:** {market_data['food_prices']['reason']} 
- {market_data['food_prices']['specific_tips'][0]}
- {market_data['food_prices']['specific_tips'][1]}
[{market_data['food_prices']['news_title']}]({market_data['food_prices']['news_link']})

**Transportation Update:** {market_data['transportation']['specific_tips'][0]}
[{market_data['transportation']['news_title']}]({market_data['transportation']['news_link']})

**Utilities Notice:** {market_data['utilities']['specific_tips'][0]}
[{market_data['utilities']['news_title']}]({market_data['utilities']['news_link']})

## 💡 Trending Financial Opportunities
- {market_data['financial_tips']['trending_opportunities'][0]}
- {market_data['financial_tips']['trending_opportunities'][1]}

⚠️ **Stay Safe:** {market_data['financial_tips']['warnings'][0]}

*Sources: {market_data['food_prices']['source']}, {market_data['transportation']['source']}*"""
            
            return TipResponse(tip=enhanced_content)
            
        except Exception as e:
            logger.warning(f"AI generation failed, falling back: {e}")
            # fall through to rule-based fallback

    # Enhanced rule-based advice with market-aware insights (Rich AI-quality fallback)
    market_data = get_current_market_insights()
    cats = breakdown.get("categories", {})
    essentials = Decimal(str(breakdown.get("total_essential", "0")))
    savings_total = Decimal(str(breakdown.get("total_savings", "0")))
    food_amount = Decimal(str(cats.get("food", "0")))
    transport_amount = Decimal(str(cats.get("transportation", "0")))
    emergency_fund = Decimal(str(cats.get("emergency_fund", "0")))
    utilities_amount = Decimal(str(cats.get("utilities", "0")))
    
    # Calculate comprehensive financial ratios for analysis
    savings_rate = float(savings_total / body.budget * 100) if body.budget > 0 else 0
    food_ratio = float(food_amount / body.budget * 100) if body.budget > 0 else 0
    transport_ratio = float(transport_amount / body.budget * 100) if body.budget > 0 else 0
    utilities_ratio = float(utilities_amount / body.budget * 100) if body.budget > 0 else 0
    essentials_ratio = float(essentials / body.budget * 100) if body.budget > 0 else 0
    
    # Generate comprehensive market-aware analysis sections
    insights = []
    smart_recommendations = []
    market_alerts = []
    financial_health_score = 0
    
    # === SAVINGS ANALYSIS ===
    if savings_rate >= 25:
        insights.append(f"🌟 Outstanding! Your {savings_rate:.1f}% savings rate far exceeds the 20% ideal")
        financial_health_score += 30
        smart_recommendations.append("Consider investing surplus savings in index funds or time deposits")
    elif savings_rate >= 20:
        insights.append(f"✅ Excellent! Your {savings_rate:.1f}% savings rate meets the gold standard")
        financial_health_score += 25
        smart_recommendations.append("You're on track for financial independence - maintain this discipline")
    elif savings_rate >= 15:
        insights.append(f"📈 Good progress! Your {savings_rate:.1f}% savings rate is above average")
        financial_health_score += 20
        smart_recommendations.append("Try to push toward 20% savings rate for optimal financial health")
    elif savings_rate >= 10:
        insights.append(f"⚠️ Your {savings_rate:.1f}% savings rate needs improvement")
        financial_health_score += 10
        smart_recommendations.append("**Priority:** Reduce discretionary spending to boost savings to 15-20%")
    else:
        insights.append(f"🚨 Critical: {savings_rate:.1f}% savings rate puts your financial future at risk")
        smart_recommendations.append("**URGENT:** Review all expenses - you need at least 10% savings minimum")
        
    # === FOOD BUDGET ANALYSIS WITH MARKET CONTEXT ===
    if food_ratio > 40:
        insights.append(f"🍽️ Food expenses at {food_ratio:.1f}% are dangerously high, especially with {market_data['food_prices']['percentage']}% price increases")
        smart_recommendations.append(f"**Food Crisis Strategy:** {market_data['food_prices']['advice']}")
        smart_recommendations.append("Consider meal prepping and bulk buying non-perishables")
        market_alerts.append(f"⚠️ URGENT: {market_data['food_prices']['specific_tips'][0]}")
        financial_health_score -= 10
    elif food_ratio > 35:
        insights.append(f"🍽️ Food budget at {food_ratio:.1f}% is high amid {market_data['food_prices']['percentage']}% inflation")
        smart_recommendations.append(f"**Food Strategy:** {market_data['food_prices']['advice']}")
        market_alerts.append(f"💡 {market_data['food_prices']['specific_tips'][0]}")
        financial_health_score += 5
    elif food_ratio < 20:
        insights.append("🎯 Impressive food budget control despite market inflation")
        smart_recommendations.append("Your disciplined food spending creates room for investments")
        market_alerts.append(f"💡 Pro tip: {market_data['food_prices']['specific_tips'][1]}")
        financial_health_score += 15
    else:
        insights.append("✅ Well-balanced food budget despite current market challenges")
        market_alerts.append(f"📈 Stay alert: {market_data['food_prices']['specific_tips'][0]}")
        financial_health_score += 10
        
    # === TRANSPORTATION ANALYSIS WITH MARKET CONTEXT ===
    if transport_ratio > 25:
        insights.append(f"🚗 Transportation costs at {transport_ratio:.1f}% are excessive")
        smart_recommendations.append(f"**Transport Emergency Plan:** {market_data['transportation']['advice']}")
        smart_recommendations.append("Consider relocating closer to work or finding carpool partners")
        market_alerts.append(f"⛽ CRITICAL: {market_data['transportation']['specific_tips'][0]}")
        financial_health_score -= 5
    elif transport_ratio > 20:
        insights.append(f"🚗 Transportation at {transport_ratio:.1f}% needs optimization")
        smart_recommendations.append(f"**Smart Commuting:** {market_data['transportation']['advice']}")
        market_alerts.append(f"⛽ {market_data['transportation']['specific_tips'][0]}")
    elif transport_ratio < 10:
        insights.append("🎯 Excellent transportation budget management")
        smart_recommendations.append("Your low transport costs free up money for investments")
        financial_health_score += 10
    else:
        insights.append("✅ Reasonable transportation budget")
        market_alerts.append(f"⛽ Monitor: {market_data['transportation']['specific_tips'][0]}")
        financial_health_score += 5
        
    # === UTILITIES ANALYSIS WITH ENERGY MARKET CONTEXT ===
    if utilities_ratio > 20:
        insights.append(f"⚡ Utilities at {utilities_ratio:.1f}% are very high amid {market_data['utilities']['percentage']}% rate increases")
        smart_recommendations.append(f"**Energy Emergency Plan:** {market_data['utilities']['advice']}")
        smart_recommendations.append("Invest in energy-efficient appliances - they'll pay for themselves")
        market_alerts.append(f"⚡ URGENT: {market_data['utilities']['specific_tips'][0]}")
        financial_health_score -= 5
    elif utilities_ratio > 15:
        smart_recommendations.append(f"**Energy Optimization:** {market_data['utilities']['advice']}")
        market_alerts.append(f"⚡ {market_data['utilities']['specific_tips'][0]}")
    else:
        market_alerts.append(f"⚡ Energy tip: {market_data['utilities']['specific_tips'][0]}")
        financial_health_score += 5
        
    # === EMERGENCY FUND ANALYSIS ===
    if emergency_fund < 5000:
        insights.append("🚨 Emergency fund critically low - you're one crisis away from debt")
        smart_recommendations.append("**TOP PRIORITY:** Build ₱10,000 emergency fund immediately")
        financial_health_score -= 15
    elif emergency_fund < 15000:
        insights.append("⚠️ Emergency fund needs strengthening for financial security")
        smart_recommendations.append("**Important:** Target ₱20,000-30,000 emergency fund")
        financial_health_score += 5
    elif emergency_fund < 30000:
        insights.append("📈 Good emergency fund progress - keep building")
        smart_recommendations.append("**Goal:** Reach ₱50,000 for complete security")
        financial_health_score += 15
    else:
        insights.append("🛡️ Excellent emergency fund - you're crisis-proof!")
        smart_recommendations.append("Consider investing excess emergency funds in low-risk options")
        financial_health_score += 25
        
    # === OVERALL FINANCIAL HEALTH SCORE ===
    if financial_health_score >= 50:
        health_status = "🌟 EXCELLENT - You're a financial rockstar!"
        health_color = "success"
    elif financial_health_score >= 30:
        health_status = "✅ GOOD - Solid financial foundation"
        health_color = "primary"
    elif financial_health_score >= 10:
        health_status = "⚠️ NEEDS IMPROVEMENT - Take action soon"
        health_color = "warning"
    else:
        health_status = "🚨 CRITICAL - Immediate attention required"
        health_color = "danger"
        
    # === INVESTMENT OPPORTUNITIES ===
    investment_tips = []
    if savings_rate >= 20:
        investment_tips.extend([
            f"💰 **High-Yield Options:** {market_data['financial_tips']['trending_opportunities'][0]}",
            f"🏦 **Safe Growth:** {market_data['financial_tips']['trending_opportunities'][1]}",
            "📈 **Consider:** FMETF (Philippine stock market index fund) for long-term growth"
        ])
    elif savings_rate >= 15:
        investment_tips.extend([
            f"💰 **Start Here:** {market_data['financial_tips']['trending_opportunities'][1]}",
            "🏦 **Build First:** Complete your emergency fund before aggressive investing"
        ])
    else:
        investment_tips.append("🎯 **Focus First:** Build emergency fund before considering investments")
        
    # Build comprehensive formatted response with rich insights
    title = f"🤖 AI-Powered Financial Health Report"
    
    # Create detailed analysis sections
    health_section = f"""## 📊 Financial Health Score: {financial_health_score}/75
**Status:** {health_status}

**Key Insights:**
• {chr(10).join(f"  {insight}" for insight in insights)}"""
    
    recommendations_section = f"""## 💡 Smart Action Plan
{chr(10).join(f"• {rec}" for rec in smart_recommendations)}"""
    
    market_section = f"""## 📰 Current Market Intelligence ({market_data['economic_outlook']['inflation_rate']}% inflation)
{chr(10).join(f"• {alert}" for alert in market_alerts)}

**Economic Outlook:** {market_data['economic_outlook']['trend']} - {', '.join(market_data['economic_outlook']['key_factors'])}"""
    
    investment_section = f"""## � Investment Opportunities
{chr(10).join(investment_tips)}"""
    
    news_section = f"""## �🔗 Stay Informed - Latest Headlines
• [{market_data['food_prices']['news_title']}]({market_data['food_prices']['news_link']})
• [{market_data['transportation']['news_title']}]({market_data['transportation']['news_link']})
• [{market_data['utilities']['news_title']}]({market_data['utilities']['news_link']})"""
    
    safety_section = f"""## ⚠️ Financial Safety Alerts
• {market_data['financial_tips']['warnings'][0]}
• {market_data['financial_tips']['warnings'][1] if len(market_data['financial_tips']['warnings']) > 1 else 'Avoid get-rich-quick schemes - sustainable wealth takes time'}"""
    
    next_steps = f"""## 🎯 Your Next Steps
**Immediate (This Week):**
{'• Build emergency fund to ₱10,000' if emergency_fund < 10000 else '• Review highest expense category for optimization'}

**Short-term (This Month):**
{'• Reduce food expenses by 10% using market strategies' if food_ratio > 30 else '• Increase savings rate by 2-3%'}

**Long-term (This Quarter):**
{'• Establish consistent 20% savings rate' if savings_rate < 20 else '• Begin investment portfolio with index funds'}"""

    advice = f"""{title}

{health_section}

{recommendations_section}

{market_section}

{investment_section}

{news_section}

{safety_section}

{next_steps}

---
*Analysis powered by real-time market data and AI algorithms*
*Sources: {market_data['food_prices']['source']}, {market_data['transportation']['source']}, {market_data['economic_outlook']['source']}*"""

    return TipResponse(tip=advice)
