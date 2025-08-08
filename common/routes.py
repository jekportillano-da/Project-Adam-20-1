import logging
import time
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pathlib import Path
from typing import Optional

# Import authentication modules
from auth import get_current_user, optional_auth
from auth.models import User

logger = logging.getLogger(__name__)

# Get the absolute paths
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

def create_main_routes(require_auth: bool = True, route_prefix: str = "") -> APIRouter:
    """
    Create main application routes
    
    Args:
        require_auth: Whether authentication is required for these routes
        route_prefix: Prefix for routes (e.g., "/demo" for dev environment)
    """
    router = APIRouter(prefix=route_prefix)
    
    @router.get("/", response_class=HTMLResponse)
    async def home(request: Request, current_user: Optional[User] = Depends(optional_auth if not require_auth else get_current_user)):
        """Serve the main index.html page"""
        try:
            logger.debug(f"Home route called - require_auth: {require_auth}, current_user: {current_user}")
            
            # For production (require_auth=True), redirect to login if not authenticated
            if require_auth and current_user is None:
                logger.debug("User is not authenticated, redirecting to login")
                return RedirectResponse(url="/login", status_code=302)
            
            logger.debug("Serving home page")
            
            # Read the template file
            index_file = TEMPLATES_DIR / "index.html"
            if not index_file.exists():
                logger.error(f"index.html not found at {index_file}")
                raise HTTPException(status_code=500, detail="Template file not found")
            
            with open(index_file, "r", encoding="utf-8") as f:
                html_content = f.read()
            
            # Process the template manually to replace url_for tags
            html_content = process_template_variables(html_content)
            
            # Set up navigation URLs based on environment
            if require_auth:
                # Production environment - set up production URLs
                budget_insights_url = "/"
                monthly_bills_url = "/bills"
                demo_mode_value = "false"
            else:
                # Demo environment - set up demo URLs
                budget_insights_url = "/demo"
                monthly_bills_url = "/demo/bills"
                demo_mode_value = "true"
            
            # Replace navigation URLs in the HTML
            html_content = html_content.replace(
                'id="budget-insights-link">Budget Insights</a>',
                f'id="budget-insights-link" href="{budget_insights_url}">Budget Insights</a>'
            )
            html_content = html_content.replace(
                'id="monthly-bills-link">Monthly Bills</a>',
                f'id="monthly-bills-link" href="{monthly_bills_url}">Monthly Bills</a>'
            )
            
            # Inject authentication state
            if require_auth and current_user:
                # Authenticated user in production
                user_script = f"""
                <script>
                    window.isAuthenticated = true;
                    window.demoMode = {demo_mode_value};
                    window.currentUser = {{
                        id: {current_user.id},
                        name: "{current_user.name}",
                        email: "{current_user.email}"
                    }};
                    
                    function getAuthToken() {{
                        return 'cookie-auth';
                    }}
                    
                    function isAuthenticated() {{
                        return true;
                    }}
                </script>
                """
            else:
                # Demo mode (dev environment)
                user_script = f"""
                <script>
                    window.isAuthenticated = false;
                    window.demoMode = {demo_mode_value};
                    window.currentUser = null;
                    
                    function getAuthToken() {{
                        return null;
                    }}
                    
                    function isAuthenticated() {{
                        return false;
                    }}
                    
                    console.log('🎭 Running in Demo Mode - No account required!');
                </script>
                """
            
            # Insert the script before the closing </head> tag
            html_content = html_content.replace('</head>', user_script + '</head>')
            
            return HTMLResponse(content=html_content)
            
        except Exception as e:
            logger.error(f"Error in home route: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    @router.get("/bills", response_class=HTMLResponse)
    async def bills_page(request: Request, current_user: Optional[User] = Depends(optional_auth if not require_auth else get_current_user)):
        """Serve the bills page"""
        try:
            # For production, check authentication
            if require_auth and current_user is None:
                return RedirectResponse(url="/login", status_code=302)
                
            bills_file = TEMPLATES_DIR / "bills.html"
            if not bills_file.exists():
                raise HTTPException(status_code=404, detail="Bills page not found")
            
            with open(bills_file, "r", encoding="utf-8") as f:
                html_content = f.read()
            
            # Process template variables
            html_content = process_template_variables(html_content)
            
            # Set up navigation URLs based on environment
            if require_auth:
                # Production environment
                budget_insights_url = "/"
                monthly_bills_url = "/bills"
                demo_mode_value = "false"
            else:
                # Demo environment
                budget_insights_url = "/demo"
                monthly_bills_url = "/demo/bills"
                demo_mode_value = "true"
            
            # Replace navigation URLs in the HTML
            html_content = html_content.replace(
                'budgetInsightsLink.href = \'/demo\';',
                f'budgetInsightsLink.href = \'{budget_insights_url}\';'
            )
            html_content = html_content.replace(
                'monthlyBillsLink.href = \'/demo/bills\';',
                f'monthlyBillsLink.href = \'{monthly_bills_url}\';'
            )
            html_content = html_content.replace(
                'budgetInsightsLink.href = \'/\';',
                f'budgetInsightsLink.href = \'{budget_insights_url}\';'
            )
            html_content = html_content.replace(
                'monthlyBillsLink.href = \'/bills\';',
                f'monthlyBillsLink.href = \'{monthly_bills_url}\';'
            )
            
            # Inject demo mode variable
            demo_script = f"""
            <script>
                window.demoMode = {demo_mode_value};
                console.log('🎭 Bills page - Demo mode: {demo_mode_value}');
            </script>
            """
            html_content = html_content.replace('</head>', demo_script + '</head>')
            
            return HTMLResponse(content=html_content)
            
        except Exception as e:
            logger.error(f"Error serving bills page: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    return router

def process_template_variables(html_content: str) -> str:
    """Process template variables in HTML content"""
    import re
    
    # Replace all url_for static file references
    def replace_url_for(match):
        filename = match.group(1)
        if filename.endswith('.js'):
            # Add cache busting for JS files
            return f'/static/{filename}?v={int(time.time())}'
        else:
            return f'/static/{filename}'
    
    # Pattern to match {{ url_for('static', filename='...') }}
    pattern = r"{{\s*url_for\(\s*['\"]static['\"],\s*filename\s*=\s*['\"]([^'\"]+)['\"]\s*\)\s*}}"
    html_content = re.sub(pattern, replace_url_for, html_content)
    
    # Handle patterns with cache busting
    pattern_with_cache = r"{{\s*url_for\(\s*['\"]static['\"],\s*filename\s*=\s*['\"]([^'\"]+)['\"]\s*\)\s*}}\?v={{\s*[^}]+\s*}}"
    html_content = re.sub(pattern_with_cache, replace_url_for, html_content)
    
    # Handle random filter patterns
    pattern_random = r"{{\s*range\([^}]+\)\s*\|\s*random\s*}}"
    html_content = re.sub(pattern_random, str(int(time.time())), html_content)
    
    return html_content

def create_debug_routes() -> APIRouter:
    """Create debug routes available in both environments"""
    router = APIRouter(prefix="/debug")
    
    @router.get("/status")
    async def debug_status():
        """Simple status check"""
        return {"message": "Server is working!", "status": "ok"}
    
    @router.get("/auth")
    async def debug_auth_status(request: Request):
        """Debug endpoint to check authentication status"""
        try:
            # Get token from cookie
            token = request.cookies.get("access_token")
            auth_header = request.headers.get("authorization")
            
            debug_info = {
                "cookies": dict(request.cookies),
                "has_access_token_cookie": "access_token" in request.cookies,
                "access_token_length": len(token) if token else 0,
                "has_auth_header": "authorization" in request.headers,
                "auth_header": auth_header[:20] + "..." if auth_header else None,
            }
            
            # Try to decode the token
            if token:
                try:
                    from auth.auth_utils import auth_manager
                    payload = auth_manager.verify_token(token)
                    debug_info["token_valid"] = payload is not None
                    debug_info["token_payload"] = payload
                except Exception as e:
                    debug_info["token_error"] = str(e)
            
            return debug_info
        except Exception as e:
            return {"error": str(e)}
    
    return router
