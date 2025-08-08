import logging
import time
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
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

# Create FastAPI app
app = FastAPI(
    title="Smart Budget Assistant",
    description="AI-powered budget planning with microservices architecture",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Include authentication router
app.include_router(auth_router)

# Debug endpoint for cookie testing
@app.get("/debug/auth")
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
async def home(request: Request, current_user: User = Depends(optional_auth)):
    """Serve the main index.html page - redirect to login if not authenticated"""
    try:
        logger.debug("Home route called")
        logger.debug(f"Current user: {current_user}")
        logger.debug(f"Request cookies: {request.cookies}")
        
        # Check authentication
        if current_user is None:
            logger.debug("User is not authenticated, redirecting to login")
            return RedirectResponse(url="/login", status_code=302)
        
        logger.debug("User is authenticated, serving home page")
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
        
        # Also handle patterns with ?v= cache busting
        pattern_with_cache = r"{{\s*url_for\(\s*['\"]static['\"],\s*filename\s*=\s*['\"]([^'\"]+)['\"]\s*\)\s*}}\?v={{\s*[^}]+\s*}}"
        html_content = re.sub(pattern_with_cache, replace_url_for, html_content)
        
        # Handle any remaining random filter patterns
        pattern_random = r"{{\s*range\([^}]+\)\s*\|\s*random\s*}}"
        html_content = re.sub(pattern_random, str(int(time.time())), html_content)
        
        # Inject user authentication state for authenticated users
        user_script = f"""
        <script>
            // Set authentication state for authenticated user
            window.isAuthenticated = true;
            window.currentUser = {{
                id: {current_user.id},
                name: "{current_user.name}",
                email: "{current_user.email}"
            }};
            
            // Override localStorage check since we're using cookie auth
            function getAuthToken() {{
                return window.isAuthenticated ? 'cookie-auth' : null;
            }}
            
            function isAuthenticated() {{
                return window.isAuthenticated;
            }}
        </script>
        """
        
        # Insert the script before the closing </head> tag
        html_content = html_content.replace('</head>', user_script + '</head>')
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Error in home route: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

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

@app.get("/demo", response_class=HTMLResponse)
async def demo_page(request: Request):
    """Serve demo mode (main page without authentication)"""
    try:
        logger.debug("Demo route called - serving without authentication")
        
        # Read the template file
        index_file = TEMPLATES_DIR / "index.html"
        if not index_file.exists():
            logger.error(f"index.html not found at {index_file}")
            raise HTTPException(status_code=500, detail=f"Template file not found")
        
        with open(index_file, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Process template variables (same as authenticated version)
        import re
        
        def replace_url_for(match):
            filename = match.group(1)
            if filename.endswith('.js'):
                return f'/static/{filename}?v={int(time.time())}'
            else:
                return f'/static/{filename}'
        
        pattern = r"{{\s*url_for\(\s*['\"]static['\"],\s*filename\s*=\s*['\"]([^'\"]+)['\"]\s*\)\s*}}"
        html_content = re.sub(pattern, replace_url_for, html_content)
        
        pattern_with_cache = r"{{\s*url_for\(\s*['\"]static['\"],\s*filename\s*=\s*['\"]([^'\"]+)['\"]\s*\)\s*}}\?v={{\s*[^}]+\s*}}"
        html_content = re.sub(pattern_with_cache, replace_url_for, html_content)
        
        pattern_random = r"{{\s*range\([^}]+\)\s*\|\s*random\s*}}"
        html_content = re.sub(pattern_random, str(int(time.time())), html_content)
        
        # Inject demo mode state (no authentication required)
        demo_script = f"""
        <script>
            // Set demo mode state
            window.isAuthenticated = false;
            window.demoMode = true;
            window.currentUser = null;
            
            // Override authentication functions for demo
            function getAuthToken() {{
                return null;
            }}
            
            function isAuthenticated() {{
                return false;
            }}
            
            // Demo mode indicator
            console.log('🎭 Running in Demo Mode - No account required!');
        </script>
        """
        
        html_content = html_content.replace('</head>', demo_script + '</head>')
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Error in demo route: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
