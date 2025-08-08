#!/usr/bin/env python3
"""
Production Server - Port 8080
Requires authentication for all main routes
Routes available at: /, /bills, etc. (behind auth)
Auth routes: /auth/login, /auth/register, /login, /register
"""

import logging
import uvicorn
from settings import get_prod_settings
from common.app_factory import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for production server"""
    # Get production settings
    settings = get_prod_settings()
    
    logger.info(f"🔒 Starting Production Server")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Port: {settings.port}")
    logger.info(f"Authentication: {'Required' if settings.require_auth else 'Not Required'}")
    logger.info(f"Route prefix: '{settings.route_prefix}' (access at /)")
    
    # Create the FastAPI app
    app = create_app(settings)
    
    # Run the server
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )

if __name__ == "__main__":
    main()
