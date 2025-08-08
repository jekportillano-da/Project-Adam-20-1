#!/usr/bin/env python3
"""
Demo Application Entry Point
- Port: 8000
- Route Prefix: /demo  
- Authentication: Not required (demo mode)
- Environment: Development

Access the application at: http://localhost:8000/demo
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

# Create the FastAPI app
settings = get_dev_settings()
app = create_app(settings)

def main():
    """Main entry point for demo application"""
    logger.info("🎭 Starting Demo Application")
    logger.info(f"Environment: {settings.env}")
    logger.info(f"Port: {settings.port}")
    logger.info(f"Authentication: {'Required' if settings.require_auth else 'Not Required (Demo Mode)'}")
    logger.info(f"Route prefix: '{settings.route_prefix}'")
    logger.info(f"Access at: http://localhost:{settings.port}{settings.route_prefix}")
    logger.info(f"Swagger docs: http://localhost:{settings.port}/docs")
    
    # Run the server
    uvicorn.run(
        "main_dev:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

if __name__ == "__main__":
    main()
