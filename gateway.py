from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx
import logging
import os
import time
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get the absolute paths
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

logger.debug(f"Base directory: {BASE_DIR}")
logger.debug(f"Static directory: {STATIC_DIR}")
logger.debug(f"Templates directory: {TEMPLATES_DIR}")

# Initialize FastAPI
app = FastAPI(
    title="Budget Assistant Gateway",
    description="Gateway API for the Smart Budget Assistant"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Helper function to patch Jinja2Templates to handle Flask-style url_for
def patch_templates():
    orig_get_env = templates.env.get_template
    
    def patched_url_for(name, **path_params):
        if name == 'static' and 'filename' in path_params:
            return f"/static/{path_params['filename']}"
        return "/"  # Default fallback
    
    def patched_get_env(*args, **kwargs):
        template = orig_get_env(*args, **kwargs)
        template.globals['url_for'] = patched_url_for
        return template
    
    templates.env.get_template = patched_get_env

# Apply the patch
patch_templates()

# Add middleware to prevent directory listing
@app.middleware("http")
async def prevent_directory_listing(request: Request, call_next):
    # Check if the path is for a directory
    if request.url.path.endswith('/') and not request.url.path == '/':
        logger.warning(f"Directory access attempt: {request.url.path}")
        raise HTTPException(status_code=404, detail="Page not found")
    
    # For all other cases, proceed normally
    response = await call_next(request)
    return response

# Microservice URLs
SERVICES = {
    "budget": "http://localhost:8081",
    "savings": "http://localhost:8082",
    "insights": "http://localhost:8083"
}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main index.html page"""
    try:
        logger.debug(f"Templates directory: {TEMPLATES_DIR}")
        index_file = TEMPLATES_DIR / "index.html"
        logger.debug(f"Checking if index.html exists: {index_file.exists()}")
        
        if not index_file.exists():
            logger.error(f"index.html not found at {index_file}")
            raise HTTPException(status_code=500, detail=f"Template file not found")
        
        # Read the file content directly
        with open(index_file, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Process the template manually to replace url_for tags
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'css/style.css\') }}', 
            '/static/css/style.css'
        )
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'css/components.css\') }}', 
            '/static/css/components.css'
        )
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'css/insights.css\') }}', 
            '/static/css/insights.css'
        )
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'css/breakdown.css\') }}', 
            '/static/css/breakdown.css'
        )
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'css/tips.css\') }}', 
            '/static/css/tips.css'
        )
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'js/dropdown.js\') }}', 
            '/static/js/dropdown.js?v=' + str(int(time.time()))  # Add timestamp to bust cache
        )
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'js/script.js\') }}', 
            '/static/js/script.js?v=' + str(int(time.time()))  # Add timestamp to bust cache
        )

        # Create a plain HTML response
        response = HTMLResponse(content=html_content)
        
        # Add cache control headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except Exception as e:
        logger.error(f"Error serving index.html: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error")

@app.get("/bills", response_class=HTMLResponse)
async def bills(request: Request):
    """Serve the bills.html page"""
    try:
        logger.debug(f"Templates directory: {TEMPLATES_DIR}")
        bills_file = TEMPLATES_DIR / "bills.html"
        logger.debug(f"Checking if bills.html exists: {bills_file.exists()}")
        
        if not bills_file.exists():
            logger.error(f"bills.html not found at {bills_file}")
            raise HTTPException(status_code=500, detail=f"Template file not found")
            
        # Read the file content directly
        with open(bills_file, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Process the template manually to replace url_for tags
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'css/style.css\') }}', 
            '/static/css/style.css'
        )
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'css/components.css\') }}', 
            '/static/css/components.css'
        )
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'css/bills.css\') }}', 
            '/static/css/bills.css'
        )
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'js/dropdown.js\') }}', 
            '/static/js/dropdown.js?v=' + str(int(time.time()))
        )
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'js/bills.js\') }}', 
            '/static/js/bills.js?v=' + str(int(time.time()))
        )

        # Create a plain HTML response
        response = HTMLResponse(content=html_content)
        
        # Add cache control headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except Exception as e:
        logger.error(f"Error rendering bills template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Specific API routes MUST come before the generic proxy route
@app.post("/api/tip")
async def get_budget_tip(request: Request):
    """Generate budget tip using Groq AI"""
    try:
        # Import here to avoid dependency issues
        import os
        from openai import OpenAI
        import json
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv()
        
        # Get request data
        data = await request.json()
        budget = float(str(data.get('budget', '')).replace(',', ''))
        duration = data.get('duration', 'daily')
        
        # Validate budget
        if budget <= 0:
            return {"tip": "Please enter a positive amount"}
        if budget > 1000000:
            return {"tip": "Amount cannot exceed PHP 1,000,000"}
            
        # Convert to daily budget
        if duration == 'weekly':
            daily_budget = round(budget / 7, 2)
        elif duration == 'monthly':
            daily_budget = round(budget / 30, 2)
        else:  # daily
            daily_budget = budget
            
        # Initialize Groq client
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            logger.error("Groq API key not found")
            return {"tip": "AI service not configured. Please add your Groq API key."}
            
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        
        # Determine budget level
        budget_level = 'low' if daily_budget < 500 else 'medium' if daily_budget < 1000 else 'high'
        
        # Get AI budget allocations
        allocation_prompt = f"""As a financial advisor, analyze this budget and return ONLY a JSON object containing recommended percentage allocations.
        Daily budget: PHP {daily_budget:.2f}
        Budget level: {budget_level}
        
        Rules:
        - Total must equal 100
        - Categories must include: Food, Transportation, Utilities, Emergency Fund, Discretionary
        - For {budget_level} budgets, follow these guidelines:
          low: Essentials 70-80%, Emergency 10-15%, Rest discretionary
          medium: Essentials 60-70%, Emergency 15-20%, Rest discretionary
          high: Essentials 50-60%, Emergency 20-25%, Rest discretionary/investments
        
        Return ONLY a JSON object like:
        {{"Food": 30, "Transportation": 20, "Utilities": 20, "Emergency Fund": 20, "Discretionary": 10}}"""

        try:
            # Get allocations from AI
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial allocation expert. Respond only with a valid JSON object containing percentage allocations that sum to 100."
                    },
                    {
                        "role": "user",
                        "content": allocation_prompt
                    }
                ],
                temperature=0.2,
                max_tokens=200
            )
            
            if response.choices and response.choices[0].message.content:
                allocations = json.loads(response.choices[0].message.content)
                if not isinstance(allocations, dict) or sum(allocations.values()) != 100:
                    raise ValueError("Invalid allocation response")
            else:
                raise ValueError("No response from AI")
                
        except Exception as e:
            logger.warning(f"AI allocation failed, using fallback: {str(e)}")
            # Fallback allocations
            if budget_level == 'low':
                allocations = {"Food": 40, "Transportation": 20, "Utilities": 15, "Emergency Fund": 15, "Discretionary": 10}
            elif budget_level == 'medium':
                allocations = {"Food": 35, "Transportation": 15, "Utilities": 15, "Emergency Fund": 20, "Discretionary": 15}
            else:
                allocations = {"Food": 30, "Transportation": 15, "Utilities": 15, "Emergency Fund": 25, "Discretionary": 15}
        
        # Calculate breakdown
        breakdown = {category: (percentage / 100.0) * daily_budget for category, percentage in allocations.items()}
        
        # Get comprehensive AI insights with market analysis
        insights_prompt = f"""You are a sophisticated AI financial advisor for Filipinos. Analyze this budget and provide comprehensive insights:

Budget Context:
- Daily Budget: PHP {daily_budget:.2f}
- Budget Level: {budget_level}
- Duration: {duration}
- Spending Breakdown: {json.dumps(breakdown, indent=2)}

Provide a detailed JSON response with these sections:

{{
  "financial_health_score": 85,
  "key_insights": [
    "Your emergency fund allocation of 20% is excellent",
    "Food budget could be optimized by 15-20%"
  ],
  "smart_recommendations": [
    {{
      "priority": "high",
      "category": "Food",
      "action": "Specific actionable step",
      "impact": "Expected savings/benefit",
      "timeframe": "immediate/weekly/monthly"
    }}
  ],
  "market_alerts": [
    {{
      "type": "food_prices",
      "message": "Rice prices increased 8% this month",
      "advice": "Stock up on 25kg rice bags"
    }}
  ],
  "investment_opportunities": [
    "Consider UITF if savings exceed PHP 5,000 monthly"
  ],
  "budget_optimization": {{
    "overspending_risk": ["Transportation", "Discretionary"],
    "underutilized_areas": ["Emergency Fund building"],
    "suggested_adjustments": {{
      "Food": -5,
      "Emergency Fund": +3,
      "Transportation": -2
    }}
  }},
  "next_steps": [
    "Build emergency fund to PHP 15,000",
    "Reduce food expenses by meal planning"
  ]
}}

Make insights specific to Philippine context, current economic conditions, and this exact budget level."""

        try:
            # Get comprehensive insights from AI
            insights_response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Filipino financial advisor with deep knowledge of local markets, economic conditions, and practical money management. Always respond with valid JSON containing comprehensive financial insights."
                    },
                    {
                        "role": "user",
                        "content": insights_prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            if insights_response.choices and insights_response.choices[0].message.content:
                insights = json.loads(insights_response.choices[0].message.content)
                
                # Format as comprehensive tip response
                formatted_tip = f"""🎯 **Financial Health Score: {insights.get('financial_health_score', 75)}/100**

📊 **Key Insights:**
{chr(10).join([f"• {insight}" for insight in insights.get('key_insights', [])])}

💡 **Smart Recommendations:**
{chr(10).join([f"🔥 **{rec.get('priority', '').upper()}**: {rec.get('action', '')} → {rec.get('impact', '')} ({rec.get('timeframe', 'ongoing')})" for rec in insights.get('smart_recommendations', [])])}

📰 **Market Alerts:**
{chr(10).join([f"⚠️ **{alert.get('type', '').replace('_', ' ').title()}**: {alert.get('message', '')} - {alert.get('advice', '')} [Market News](https://www.bsp.gov.ph/SitePages/MediaAndResearch/MediaAndResearch.aspx)" for alert in insights.get('market_alerts', [])])}

💰 **Investment Opportunities:**
{chr(10).join([f"💎 {opp}" for opp in insights.get('investment_opportunities', [])])}

⚖️ **Budget Optimization:**
Risk Areas: {', '.join(insights.get('budget_optimization', {}).get('overspending_risk', []))}
Adjustments: {', '.join([f"{k}{v:+d}%" for k, v in insights.get('budget_optimization', {}).get('suggested_adjustments', {}).items()])}

🎯 **Next Steps:**
{chr(10).join([f"✅ {step}" for step in insights.get('next_steps', [])])}"""
                
                return {"tip": formatted_tip}
                
            else:
                raise ValueError("No insights response from AI")
                
        except Exception as e:
            logger.warning(f"AI insights failed, using enhanced fallback: {str(e)}")
            # Enhanced fallback with sophisticated analysis
            health_score = 85 if budget_level == 'high' else 70 if budget_level == 'medium' else 60
            
            # Calculate key insights based on budget analysis
            food_pct = (breakdown.get('Food', 0) / daily_budget) * 100
            emergency_pct = (breakdown.get('Emergency Fund', 0) / daily_budget) * 100
            
            insights = []
            if emergency_pct >= 20:
                insights.append("🛡️ Excellent emergency fund allocation - you're financially secure!")
            elif emergency_pct >= 15:
                insights.append("✅ Good emergency fund allocation, consider increasing to 20%")
            else:
                insights.append("⚠️ Emergency fund needs attention - aim for 15-20% minimum")
                
            if food_pct > 40:
                insights.append(f"🍽️ Food budget at {food_pct:.0f}% is high - meal planning can save 15-20%")
            elif food_pct < 25:
                insights.append("🎯 Excellent food budget control!")
            else:
                insights.append("✅ Food budget is well-balanced")
            
            # Smart recommendations based on budget level
            recommendations = []
            if budget_level == 'low':
                recommendations.extend([
                    "🔥 **HIGH**: Build emergency fund to PHP 5,000 first → Financial security (immediate)",
                    "💡 **MEDIUM**: Use 50/30/20 rule for rice purchases → Save PHP 200-300 monthly (weekly)",
                    "⚡ **LOW**: Walk/bike for errands under 2km → Save PHP 100-150 monthly (daily)"
                ])
            elif budget_level == 'medium':
                recommendations.extend([
                    "🔥 **HIGH**: Automate 20% savings transfer → Build wealth consistently (immediate)",
                    "💡 **MEDIUM**: Buy in bulk for non-perishables → Save PHP 300-500 monthly (monthly)",
                    "⚡ **LOW**: Use banking apps for bill payments → Save time and fees (weekly)"
                ])
            else:
                recommendations.extend([
                    "🔥 **HIGH**: Open high-yield savings account → Earn PHP 500+ monthly (immediate)",
                    "💡 **MEDIUM**: Consider UITF/mutual funds → Build long-term wealth (monthly)",
                    "⚡ **LOW**: Maximize credit card rewards → Earn cashback on expenses (ongoing)"
                ])
            
            # Market alerts based on current conditions
            market_alerts = [
                "⚠️ **Food Prices**: Rice prices up 8% this month - Stock up on 25kg bags [BSP Food Inflation Report](https://www.bsp.gov.ph/SitePages/MediaAndResearch/SubSitePages/InflationReport.aspx)",
                "⚠️ **Transportation**: Gas prices volatile - Consider carpooling or public transport [DOE Fuel Prices](https://www.doe.gov.ph/fuel-prices)",
                "⚠️ **Utilities**: MERALCO rates increasing - Use energy-efficient appliances [MERALCO Rate Updates](https://company.meralco.com.ph/sustainability/our-rates)"
            ]
            
            # Investment opportunities by budget level
            investments = []
            if budget_level == 'high':
                investments = [
                    "💎 Consider digital banks offering 6% p.a. interest",
                    "💎 FMETF (Philippine stock index) for long-term growth",
                    "💎 MP2 PAGIBIG for retirement planning"
                ]
            elif budget_level == 'medium':
                investments = [
                    "💎 Start with digital banks for higher interest rates",
                    "💎 Build emergency fund first, then consider UITF"
                ]
            else:
                investments = [
                    "💎 Focus on emergency fund before investing",
                    "💎 Use GSave or Maya for higher interest vs traditional banks"
                ]
            
            # Next steps based on analysis
            next_steps = []
            if emergency_pct < 15:
                next_steps.append("✅ Build emergency fund to 3-6 months expenses")
            if food_pct > 35:
                next_steps.append("✅ Create weekly meal plan to reduce food costs")
            next_steps.extend([
                "✅ Track expenses for 30 days to identify spending patterns",
                "✅ Set up automatic savings transfers",
                "✅ Review and optimize monthly subscriptions"
            ])
            
            formatted_tip = f"""🎯 **Financial Health Score: {health_score}/100**

📊 **Key Insights:**
{chr(10).join(insights)}

💡 **Smart Recommendations:**
{chr(10).join(recommendations)}

📰 **Market Alerts:**
{chr(10).join(market_alerts)}

💰 **Investment Opportunities:**
{chr(10).join(investments)}

⚖️ **Budget Optimization:**
Risk Areas: {"Food" if food_pct > 35 else "Transportation"}, Discretionary spending
Adjustments: Focus on emergency fund building and expense tracking

🎯 **Next Steps:**
{chr(10).join(next_steps)}"""
            
            return {"tip": formatted_tip}
        
        logger.info("Successfully generated AI budget tip")
        return {"tip": "Error generating insights"}
        
    except Exception as e:
        logger.error(f"Error in budget tip endpoint: {str(e)}")
        return {"tip": f"AI service error: {str(e)}"}

@app.api_route("/api/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_to_service(service: str, path: str, request: Request):
    """Proxy all API requests to the appropriate microservice with AI enhancement"""
    if service not in SERVICES:
        logger.error(f"Service '{service}' not found in configured services")
        raise HTTPException(status_code=404, detail=f"Service '{service}' not found")
    
    # Get the target service URL
    service_url = SERVICES[service]
    logger.debug(f"Proxying request to {service} service at {service_url}/{path}")
    
    # Special handling for insights service - enhance with AI
    if service == "insights" and path == "analyze":
        try:
            # Get request body
            body = await request.body()
            request_data = json.loads(body) if body else {}
            
            # First get standard insights from the insights service
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{service_url}/{path}",
                    json=request_data,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    insights_data = response.json()
                    
                    # Enhance with AI analysis
                    groq_api_key = os.getenv('GROQ_API_KEY')
                    if groq_api_key and request_data.get('budget_breakdown'):
                        try:
                            # Import and initialize Groq client
                            from openai import OpenAI
                            
                            groq_client = OpenAI(
                                api_key=groq_api_key,
                                base_url="https://api.groq.com/openai/v1"
                            )
                            budget_breakdown = request_data['budget_breakdown']
                            savings_data = request_data.get('savings_data', {})
                            
                            # Calculate budget level
                            total_budget = sum(float(v) for v in budget_breakdown.get('categories', {}).values())
                            budget_level = 'high' if total_budget > 50000 else 'medium' if total_budget > 20000 else 'low'
                            
                            # AI enhancement prompt
                            ai_prompt = f"""Analyze this budget and provide enhanced insights:

Budget Categories: {budget_breakdown.get('categories', {})}
Total Budget: {total_budget}
Savings Rate: {(budget_breakdown.get('total_savings', 0) / total_budget * 100):.1f}%
Emergency Fund Progress: {savings_data.get('emergency_fund_progress', 0)}%
Current Health Score: {insights_data.get('health_score', 0)}

Please provide:
1. 2-3 specific actionable insights based on the data
2. Assessment of financial behaviors and trends
3. Personalized recommendations for improvement
4. Potential risks and opportunities

Respond with a JSON object with:
- enhanced_insights: [array of insight objects with type and message]
- ai_recommendations: [array of specific actionable recommendations]
- risk_assessment: string describing potential risks
- opportunities: [array of opportunities specific to this budget level]
"""

                            ai_response = groq_client.chat.completions.create(
                                model="llama3-70b-8192",
                                messages=[
                                    {
                                        "role": "system",
                                        "content": "You are an expert Filipino financial advisor. Provide detailed, actionable financial insights in JSON format."
                                    },
                                    {
                                        "role": "user",
                                        "content": ai_prompt
                                    }
                                ],
                                temperature=0.7,
                                max_tokens=1000
                            )
                            
                            if ai_response.choices and ai_response.choices[0].message.content:
                                ai_data = json.loads(ai_response.choices[0].message.content)
                                
                                # Merge AI insights with standard insights
                                enhanced_insights = insights_data.copy()
                                
                                # Add AI-enhanced insights
                                if 'enhanced_insights' in ai_data:
                                    enhanced_insights['insights'].extend(ai_data['enhanced_insights'])
                                
                                # Add AI recommendations
                                if 'ai_recommendations' in ai_data:
                                    enhanced_insights['recommendations'].extend(ai_data['ai_recommendations'])
                                
                                # Add new AI fields
                                enhanced_insights['risk_assessment'] = ai_data.get('risk_assessment', '')
                                enhanced_insights['opportunities'] = ai_data.get('opportunities', [])
                                enhanced_insights['ai_enhanced'] = True
                                
                                return enhanced_insights
                                
                        except Exception as e:
                            logger.warning(f"AI enhancement failed for insights: {str(e)}")
                    
                    return insights_data
                else:
                    raise HTTPException(status_code=response.status_code, detail=f"Insights service error: {response.text}")
                    
        except Exception as e:
            logger.error(f"Error in enhanced insights proxy: {str(e)}")
            # Fall back to standard proxy
    
    # Standard proxy logic for all other services
    
    # Forward the request to the appropriate service
    try:
        # Get the request body if it exists
        body = None
        if request.method in ["POST", "PUT"]:
            body = await request.body()
            logger.debug(f"Request body: {body}")

        # Forward the request
        async with httpx.AsyncClient() as client:
            logger.debug(f"Sending {request.method} request to {service_url}/{path}")
            try:
                response = await client.request(
                    method=request.method,
                    url=f"{service_url}/{path}",
                    headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
                    content=body,
                    params=request.query_params,
                    timeout=10.0  # Add a reasonable timeout
                )
                logger.debug(f"Response status: {response.status_code}")
                
                # Log response content for debugging
                response_json = response.json()
                logger.debug(f"Response from {service} service: {response_json}")
                
                return response_json
            except httpx.TimeoutException:
                logger.error(f"Timeout connecting to {service} service at {service_url}/{path}")
                raise HTTPException(status_code=504, detail=f"Timeout connecting to {service} service")
            except httpx.ConnectError:
                logger.error(f"Connection error to {service} service at {service_url}/{path}")
                raise HTTPException(status_code=503, detail=f"Cannot connect to {service} service")
    except httpx.RequestError as e:
        logger.error(f"Error connecting to {service} service: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Error connecting to {service} service: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in proxy: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/test-services")
async def test_services():
    """Test connection to all microservices"""
    results = {}
    for service_name, service_url in SERVICES.items():
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{service_url}/health", timeout=5.0)
                results[service_name] = {
                    "status": "success" if response.status_code == 200 else "error",
                    "status_code": response.status_code,
                    "response": response.json() if response.status_code == 200 else None
                }
        except Exception as e:
            results[service_name] = {
                "status": "error",
                "error": str(e)
            }
    return results

# This catch-all route must be AFTER all other routes to avoid conflicts
# Only handle non-API routes to avoid interfering with API routing
@app.api_route("/{path:path}", methods=["GET", "OPTIONS", "HEAD"])
async def catch_all(request: Request, path: str):
    """Catch-all route to prevent directory listing"""
    # Exclude API routes from catch-all
    if path.startswith("api/"):
        raise HTTPException(status_code=404, detail=f"API endpoint not found: {path}")
    
    logger.debug(f"Caught unhandled path: {path}")
    
    # Special case for the root path with trailing slash
    if path == "":
        return await home(request)
        
    # Try to serve static files
    static_path = STATIC_DIR / path
    if static_path.exists() and static_path.is_file():
        logger.debug(f"Serving static file: {static_path}")
        with open(static_path, "rb") as f:
            content = f.read()
        
        # Determine content type
        content_type = "application/octet-stream"
        if path.endswith(".css"):
            content_type = "text/css"
        elif path.endswith(".js"):
            content_type = "application/javascript"
        elif path.endswith(".html"):
            content_type = "text/html"
        elif path.endswith(".jpg") or path.endswith(".jpeg"):
            content_type = "image/jpeg"
        elif path.endswith(".png"):
            content_type = "image/png"
        
        return Response(content=content, media_type=content_type)
    
    # Otherwise return 404
    raise HTTPException(status_code=404, detail=f"Page not found: {path}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
