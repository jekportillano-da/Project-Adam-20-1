from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx
import logging
import os
import time
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
    "budget": "http://localhost:8001",
    "savings": "http://localhost:8002",
    "insights": "http://localhost:8003"
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
        logger.error(f"Error rendering template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
async def catch_all(request: Request, path: str):
    """Catch-all route to prevent directory listing"""
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
