from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, Response, RedirectResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import logging
import os
import time
from pathlib import Path

# Import authentication modules
from auth import auth_router, get_current_user, optional_auth, db
from auth.models import User

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

# Debug: Print route registration
@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI startup - registering routes...")
    for route in app.routes:
        if hasattr(route, 'path'):
            logger.info(f"Registered route: {route.path} [{getattr(route, 'methods', 'N/A')}]")  # type: ignore

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

# Include authentication router
app.include_router(auth_router)

# Test route for debugging
@app.get("/test")
async def test_route():
    """Simple test route"""
    return {"message": "Server is working!", "status": "ok"}

@app.get("/debug-auth")
async def debug_auth(request: Request):
    """Debug authentication status"""
    token = None
    
    # Try to get token from Authorization header
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    
    # If no header token, try to get from cookies
    if not token:
        token = request.cookies.get("access_token")
    
    return {
        "has_auth_header": "authorization" in request.headers,
        "auth_header": request.headers.get("authorization", "None"),
        "has_cookie": "access_token" in request.cookies,
        "cookie_value": "PRESENT" if token else "NONE",
        "all_cookies": list(request.cookies.keys())
    }

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main index.html page - redirect to login if not authenticated"""
    try:
        # TEMPORARY: Skip authentication for debugging
        logger.debug("Home route called - authentication temporarily disabled for debugging")
        
        # Just serve the page without authentication for now
        logger.debug("Serving home page without authentication check")
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
            '{{ url_for(\'static\', filename=\'js/script.js\') }}', 
            '/static/js/script.js?v=' + str(int(time.time()))
        )
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Error in home route: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
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
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'js/input-alignment.js\') }}', 
            '/static/js/input-alignment.js?v=' + str(int(time.time()))
        )
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'js/zoom-alignment-fix.js\') }}', 
            '/static/js/zoom-alignment-fix.js?v=' + str(int(time.time()))
        )
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'js/bills.js\') }}', 
            '/static/js/bills.js?v=' + str(int(time.time()))
        )

        # Add user information to the template if authenticated
        if current_user:
            user_info = f'<script>window.currentUser = {{"id": {current_user.id}, "name": "{current_user.name}", "email": "{current_user.email}"}};</script>'
            html_content = html_content.replace('</head>', f'{user_info}</head>')
        else:
            html_content = html_content.replace('</head>', '<script>window.currentUser = null;</script></head>')

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
async def bills(request: Request, current_user: User = Depends(optional_auth)):
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

# Authentication page routes
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Serve the login page"""
    try:
        login_file = TEMPLATES_DIR / "login.html"
        if not login_file.exists():
            raise HTTPException(status_code=404, detail="Login page not found")
        
        with open(login_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        return HTMLResponse(content=content)
    except Exception as e:
        logger.error(f"Error serving login page: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Serve the registration page"""
    try:
        register_file = TEMPLATES_DIR / "register.html"
        if not register_file.exists():
            raise HTTPException(status_code=404, detail="Registration page not found")
        
        with open(register_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        return HTMLResponse(content=content)
    except Exception as e:
        logger.error(f"Error serving registration page: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Clean up - removed debug routes for production

# Demo billing page for users trying without registering
@app.get("/demo/bills", response_class=HTMLResponse)
async def demo_bills(request: Request):
    """Serve the bills.html page in demo mode (no authentication required)"""
    try:
        logger.debug("Demo bills route called!")
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

        # Add demo mode indicator
        demo_info = '<script>window.currentUser = null; window.demoMode = true;</script>'
        html_content = html_content.replace('</head>', f'{demo_info}</head>')

        # Create a plain HTML response
        response = HTMLResponse(content=html_content)
        
        # Add cache control headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except Exception as e:
        logger.error(f"Error serving demo bills mode: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error")

# Guest/demo route for users who want to try without registering
@app.get("/demo", response_class=HTMLResponse)
async def demo_mode(request: Request):
    """Serve the main index.html page in demo mode (no authentication required)"""
    try:
        logger.debug("Demo route called!")
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
            '{{ url_for(\'static\', filename=\'css/bills.css\') }}', 
            '/static/css/bills.css'
        )
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'css/budget-form-fix.css\') }}', 
            '/static/css/budget-form-fix.css'
        )
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'css/input-fix.css\') }}', 
            '/static/css/input-fix.css'
        )
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'css/ultimate-input-fix.css\') }}', 
            '/static/css/ultimate-input-fix.css'
        )
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'css/left-align-fix.css\') }}', 
            '/static/css/left-align-fix.css'
        )
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'css/browser-compatibility.css\') }}', 
            '/static/css/browser-compatibility.css'
        )
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'css/budget-inputs-fix.css\') }}', 
            '/static/css/budget-inputs-fix.css'
        )
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'css/zoom-responsive-fix.css\') }}', 
            '/static/css/zoom-responsive-fix.css'
        )
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'css/wrapper-fix.css\') }}', 
            '/static/css/wrapper-fix.css'
        )
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'css/responsive-layout-fix.css\') }}', 
            '/static/css/responsive-layout-fix.css'
        )
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'css/budget-panel-responsive.css\') }}', 
            '/static/css/budget-panel-responsive.css'
        )
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'css/button-alignment-fix.css\') }}', 
            '/static/css/button-alignment-fix.css'
        )
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'css/budget-bills-integration.css\') }}', 
            '/static/css/budget-bills-integration.css'
        )
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'js/dropdown.js\') }}', 
            '/static/js/dropdown.js?v=' + str(int(time.time()))  # Add timestamp to bust cache
        )
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'js/script.js\') }}', 
            '/static/js/script.js?v=' + str(int(time.time()))  # Add timestamp to bust cache
        )
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'js/input-alignment.js\') }}', 
            '/static/js/input-alignment.js?v=' + str(int(time.time()))
        )
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'js/zoom-alignment-fix.js\') }}', 
            '/static/js/zoom-alignment-fix.js?v=' + str(int(time.time()))
        )
        html_content = html_content.replace(
            '{{ url_for(\'static\', filename=\'js/bills.js\') }}', 
            '/static/js/bills.js?v=' + str(int(time.time()))
        )

        # Add demo mode indicator
        demo_info = '<script>window.currentUser = null; window.demoMode = true;</script>'
        html_content = html_content.replace('</head>', f'{demo_info}</head>')

        # Create a plain HTML response
        response = HTMLResponse(content=html_content)
        
        # Add cache control headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except Exception as e:
        logger.error(f"Error serving demo mode: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error")

@app.get("/favicon.ico")
async def favicon():
    """Serve favicon to prevent 404 errors"""
    return FileResponse(os.path.join(BASE_DIR, "static", "favicon.ico"))

# Specific API routes MUST come before the generic proxy route
@app.post("/api/tip")
async def get_budget_tip(request: Request, current_user: User = Depends(optional_auth)):
    """Generate budget tip using Groq AI - optionally authenticated"""
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
        
        # Get AI tips
        tips_prompt = f"""Give 3 practical money-saving tips for someone in the Philippines with:
Daily budget: PHP {daily_budget:.2f}
Spending breakdown:
{json.dumps(breakdown, indent=2)}

Return ONLY a JSON array of 3 objects, each with:
- title: The tip title
- action: One specific, actionable step
- savings: Expected savings range in PHP (X.XX-Y.YY format)

Example:
[
  {{
    "title": "Smart Grocery Shopping",
    "action": "Buy fresh produce from wet markets early morning",
    "savings": "50.00-100.00"
  }}
]"""

        try:
            # Get tips from AI
            tips_response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a local financial advisor in the Philippines. Return only valid JSON arrays of money-saving tips."
                    },
                    {
                        "role": "user",
                        "content": tips_prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            if tips_response.choices and tips_response.choices[0].message.content:
                tips = json.loads(tips_response.choices[0].message.content)
                if not isinstance(tips, list) or len(tips) != 3:
                    raise ValueError("Invalid tips format")
            else:
                raise ValueError("No tips response from AI")
                
        except Exception as e:
            logger.warning(f"AI tips failed, using fallback: {str(e)}")
            # Fallback tips
            tips = [
                {
                    "title": "Smart Grocery Shopping",
                    "action": "Buy fresh produce from local markets early morning",
                    "savings": "50.00-100.00"
                },
                {
                    "title": "Transportation Planning",
                    "action": "Use public transport during off-peak hours",
                    "savings": "20.00-50.00"
                },
                {
                    "title": "Utility Savings",
                    "action": "Use natural lighting and ventilation when possible",
                    "savings": "100.00-200.00"
                }
            ]
        
        # Format response
        essential_categories = ['Food', 'Transportation', 'Utilities']
        essentials_total = sum(breakdown[cat] for cat in essential_categories if cat in breakdown)
        
        response_lines = [
            "📊 Budget Analysis",
            f"Daily Budget: PHP {daily_budget:.2f}",
            "",
            "💰 Smart Budget Breakdown:",
            *[f"{cat}: PHP {amount:.2f}" for cat, amount in breakdown.items() if cat in essential_categories],
            f"Total Essential Expenses: PHP {essentials_total:.2f}",
            "",
            "🎯 Savings and Goals:",
            f"Emergency Fund: PHP {breakdown.get('Emergency Fund', 0):.2f}",
            f"Discretionary: PHP {breakdown.get('Discretionary', 0):.2f}",
            "",
            "💡 AI-Generated Money-Saving Tips:"
        ]
        
        for i, tip in enumerate(tips, 1):
            response_lines.extend([
                f"{i}. {tip['title']}",
                f"• {tip['action']}",
                f"• Expected savings: PHP {tip['savings']}",
                ""
            ])
        
        # Remove last empty line
        if response_lines[-1] == "":
            response_lines.pop()
            
        tip_text = "\n".join(response_lines)
        
        logger.info("Successfully generated AI budget tip")
        return {"tip": tip_text}
        
    except Exception as e:
        logger.error(f"Error in budget tip endpoint: {str(e)}")
        return {"tip": f"AI service error: {str(e)}"}

@app.api_route("/api/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_to_service(service: str, path: str, request: Request):
    """Proxy all API requests to the appropriate microservice"""
    if service not in SERVICES:
        logger.error(f"Service '{service}' not found in configured services")
        raise HTTPException(status_code=404, detail=f"Service '{service}' not found")
    
    # Get the target service URL
    service_url = SERVICES[service]
    logger.debug(f"Proxying request to {service} service at {service_url}/{path}")
    
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
# TEMPORARILY DISABLED TO TEST DEMO ROUTE
# @app.api_route("/{path:path}", methods=["GET", "OPTIONS", "HEAD"])
# async def catch_all(request: Request, path: str):
#     """Catch-all route to prevent directory listing"""
#     # Exclude API routes from catch-all
#     if path.startswith("api/"):
#         raise HTTPException(status_code=404, detail=f"API endpoint not found: {path}")
#     
#     # Exclude specific routes that are handled by explicit handlers
#     excluded_paths = ["demo", "login", "register", "bills", "test-services"]
#     if path in excluded_paths:
#         raise HTTPException(status_code=404, detail=f"Route should be handled by explicit handler: {path}")
#     
#     logger.debug(f"Caught unhandled path: {path}")
#     
#     # Special case for the root path with trailing slash
#     if path == "":
#         return await home(request)
#         
#     # Try to serve static files
#     static_path = STATIC_DIR / path
#     if static_path.exists() and static_path.is_file():
#         logger.debug(f"Serving static file: {static_path}")
#         with open(static_path, "rb") as f:
#             content = f.read()
#         
#         # Determine content type
#         content_type = "application/octet-stream"
#         if path.endswith(".css"):
#             content_type = "text/css"
#         elif path.endswith(".js"):
#             content_type = "application/javascript"
#         elif path.endswith(".html"):
#             content_type = "text/html"
#         elif path.endswith(".jpg") or path.endswith(".jpeg"):
#             content_type = "image/jpeg"
#         elif path.endswith(".png"):
#             content_type = "image/png"
#         
#         return Response(content=content, media_type=content_type)
#     
#     # Otherwise return 404
#     raise HTTPException(status_code=404, detail=f"Page not found: {path}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("gateway:app", host="0.0.0.0", port=8000, reload=True)
