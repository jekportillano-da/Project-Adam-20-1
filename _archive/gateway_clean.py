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
    """Serve demo mode (redirect to main page without authentication)"""
    return RedirectResponse(url="/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)
