import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from settings import AppSettings

logger = logging.getLogger(__name__)

def create_app(settings: AppSettings) -> FastAPI:
    """
    Create and configure FastAPI application
    
    Args:
        settings: Application settings for the environment
    """
    # Create FastAPI app
    app = FastAPI(
        title=settings.app_title,
        description="AI-powered budget planning with microservices architecture",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Get the absolute paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    STATIC_DIR = BASE_DIR / "static"
    TEMPLATES_DIR = BASE_DIR / "templates"
    
    logger.debug(f"Base directory: {BASE_DIR}")
    logger.debug(f"Static directory: {STATIC_DIR}")
    logger.debug(f"Templates directory: {TEMPLATES_DIR}")
    
    # Mount static files
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    
    # Include authentication router only for production
    if settings.require_auth:
        from auth import auth_router
        app.include_router(auth_router)
        
        # Add login/register pages for production
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
    
    # Include main routes with appropriate configuration
    from common.routes import create_main_routes, create_debug_routes
    
    main_router = create_main_routes(
        require_auth=settings.require_auth,
        route_prefix=settings.route_prefix
    )
    debug_router = create_debug_routes()
    
    app.include_router(main_router)
    app.include_router(debug_router)
    
    return app
