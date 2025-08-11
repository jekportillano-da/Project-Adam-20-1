# Refactored Gateway with Enhanced Security and Resilience
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, Response, RedirectResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time
import uuid
from pathlib import Path
import logging
import os

# Try to import our enhanced modules, fall back gracefully
try:
    from config import Settings
    settings = Settings()
except ImportError as e:
    print(f"Warning: Could not import config: {e}")
    # Fallback settings
    class Settings:
        def __init__(self):
            self.allowed_origins = ["http://localhost:3000", "http://localhost:8000"]
            self.environment = "development"
            self.host = "0.0.0.0"
            self.port = 8000
            self.log_level = "INFO"
            self.log_format = "json"
            self.services = {
                "budget": "http://localhost:8081",
                "savings": "http://localhost:8082",
                "insights": "http://localhost:8083"
            }
    settings = Settings()

try:
    from logging_config import setup_logging, request_logger, security_logger, timer
    setup_logging(settings.log_level, settings.log_format)
except ImportError as e:
    print(f"Warning: Could not import logging_config: {e}")
    # Fallback timer
    class timer:
        def __init__(self, operation):
            self.operation = operation
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
    
    # Use basic logging
    logging.basicConfig(level=getattr(logging, settings.log_level))

try:
    from resilience import ServiceClient, default_rate_limiter, CircuitBreaker
except ImportError as e:
    print(f"Warning: Could not import resilience: {e}")
    # Fallback rate limiter
    class DefaultRateLimiter:
        def is_allowed(self, client_id: str) -> bool:
            return True
    default_rate_limiter = DefaultRateLimiter()

# Import authentication modules
try:
    from auth import auth_router, get_current_user, optional_auth, db
    from auth.models import User
except ImportError as e:
    print(f"Warning: Could not import auth modules: {e}")
    # Create dummy dependencies
    from fastapi import APIRouter
    auth_router = APIRouter()
    
    def optional_auth():
        return None
    
    class User:
        pass

logger = logging.getLogger(__name__)

# Get the absolute paths
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

logger.info(f"Base directory: {BASE_DIR}")
logger.info(f"Static directory: {STATIC_DIR}")
logger.info(f"Templates directory: {TEMPLATES_DIR}")

# Initialize FastAPI with enhanced security
app = FastAPI(
    title="Budget Assistant Gateway",
    description="Secure Gateway API for the Smart Budget Assistant",
    version="1.0.0",
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url="/redoc" if settings.environment != "production" else None
)

# Security middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    max_age=3600,
)

# Add trusted host middleware for production
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_origins
    )

# Configure templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Helper function to patch Jinja2Templates
def patch_templates():
    orig_get_env = templates.env.get_template
    
    def patched_url_for(name, **path_params):
        if name == 'static' and 'filename' in path_params:
            return f"/static/{path_params['filename']}"
        return "/"
    
    def patched_get_env(*args, **kwargs):
        template = orig_get_env(*args, **kwargs)
        template.globals['url_for'] = patched_url_for
        return template
    
    templates.env.get_template = patched_get_env

patch_templates()

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Generate correlation ID
    correlation_id = str(uuid.uuid4())
    
    # Get client IP for rate limiting
    client_ip = request.client.host if request.client else "unknown"
    if "x-forwarded-for" in request.headers:
        client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
    
    # Rate limiting
    if not default_rate_limiter.is_allowed(client_ip):
        if 'security_logger' in globals():
            security_logger.log_suspicious_activity(
                "rate_limit_exceeded",
                {"path": request.url.path, "method": request.method},
                client_ip,
                "high"
            )
        logger.warning(f"Rate limit exceeded for {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    # Time the request
    start_time = time.time()
    
    try:
        response = await call_next(request)
        response_time = time.time() - start_time
        
        # Log successful request
        if 'request_logger' in globals():
            request_logger.log_request(
                request, response.status_code, response_time, correlation_id
            )
        
        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response
    except Exception as e:
        response_time = time.time() - start_time
        logger.error(f"Request failed: {e}", extra={"correlation_id": correlation_id})
        raise

# Initialize service clients with resilience (if available)
service_clients = {}
try:
    if 'ServiceClient' in globals() and 'CircuitBreaker' in globals():
        service_clients = {
            service_name: ServiceClient(
                base_url=service_url,
                circuit_breaker=CircuitBreaker(failure_threshold=3, recovery_timeout=30)
            )
            for service_name, service_url in settings.services.items()
        }
    else:
        # Fallback: just store URLs
        service_clients = {name: url for name, url in settings.services.items()}
except Exception as e:
    logger.error(f"Failed to initialize service clients: {e}")
    service_clients = {name: url for name, url in settings.services.items()}

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

# Enhanced health check
@app.get("/health")
async def health_check():
    """Enhanced health check with service status"""
    with timer("health_check"):
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "version": "1.0.0",
            "services": {}
        }
        
        # Check service health
        for service_name, client_or_url in service_clients.items():
            try:
                if hasattr(client_or_url, 'health_check'):
                    # It's a ServiceClient
                    is_healthy = await client_or_url.health_check()
                    health_status["services"][service_name] = {
                        "status": "healthy" if is_healthy else "unhealthy"
                    }
                else:
                    # It's just a URL, do basic HTTP check
                    import httpx
                    async with httpx.AsyncClient() as http_client:
                        response = await http_client.get(f"{client_or_url}/health", timeout=5.0)
                        health_status["services"][service_name] = {
                            "status": "healthy" if response.status_code == 200 else "unhealthy"
                        }
            except Exception as e:
                health_status["services"][service_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # Determine overall health
        unhealthy_services = [
            name for name, status in health_status["services"].items()
            if status["status"] != "healthy"
        ]
        
        if unhealthy_services:
            health_status["status"] = "degraded"
            health_status["unhealthy_services"] = unhealthy_services
        
        return health_status

# Root route with authentication
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, current_user: User = Depends(optional_auth)):
    """Home page with authentication check"""
    with timer("home_page_render"):
        try:
            logger.debug(f"Home route called, current_user: {current_user}")
            logger.debug(f"Request cookies: {request.cookies}")
            logger.debug(f"Authorization header: {request.headers.get('authorization', 'None')}")
            
            if current_user is None:
                logger.debug("User is not authenticated, redirecting to login")
                return RedirectResponse(url="/login", status_code=302)
            
            logger.debug(f"User authenticated: {current_user.email if hasattr(current_user, 'email') else 'user_object'}")
            return templates.TemplateResponse("index.html", {
                "request": request,
                "user": current_user
            })
        except Exception as e:
            logger.error(f"Error in home route: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

# Enhanced proxy endpoint with resilience
@app.api_route("/api/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_to_service(service: str, path: str, request: Request):
    """Enhanced proxy with circuit breaker and retry logic"""
    if service not in service_clients:
        logger.error(f"Service '{service}' not found in configured services")
        raise HTTPException(status_code=404, detail=f"Service '{service}' not found")
    
    client_or_url = service_clients[service]
    
    with timer(f"proxy_to_{service}"):
        try:
            # Get the request body if it exists
            body = None
            if request.method in ["POST", "PUT"]:
                body = await request.body()
            
            if hasattr(client_or_url, '_make_request'):
                # It's a ServiceClient
                response = await client_or_url._make_request(
                    method=request.method,
                    path=path,
                    content=body,
                    params=request.query_params,
                    headers={k: v for k, v in request.headers.items() if k.lower() != "host"}
                )
                return response.json()
            else:
                # It's just a URL, make direct HTTP request
                import httpx
                async with httpx.AsyncClient() as http_client:
                    response = await http_client.request(
                        method=request.method,
                        url=f"{client_or_url}/{path}",
                        headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
                        content=body,
                        params=request.query_params,
                        timeout=10.0
                    )
                    return response.json()
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in proxy: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "gateway_enhanced:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
        reload=True
    )
