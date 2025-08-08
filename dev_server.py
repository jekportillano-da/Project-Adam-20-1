#!/usr/bin/env python3
"""
Development Server - Port 8000
Public demo mode with no authentication required
Routes available at: /demo, /demo/bills, etc.
"""

import logging
import uvicorn
from settings import get_dev_settings
from common.app_factory import create_app

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for development server"""
    # Get development settings
    settings = get_dev_settings()
    
    logger.info(f"🎭 Starting Development Server")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Port: {settings.port}")
    logger.info(f"Authentication: {'Required' if settings.require_auth else 'Not Required (Demo Mode)'}")
    logger.info(f"Route prefix: '{settings.route_prefix}' (access at /demo)")
    
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
