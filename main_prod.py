#!/usr/bin/env python3
"""
Production Application Entry Point
- Port: 8080
- Route Prefix: / (root)
- Authentication: Required (JWT/cookie-based)
- Environment: Production

Access the application at: http://localhost:8080/
Login at: http://localhost:8080/login
"""

import logging
import uvicorn
from settings import get_prod_settings
from common.app_factory import create_app

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create the FastAPI app
settings = get_prod_settings()
app = create_app(settings)

def main():
    """Main entry point for production application"""
    logger.info("🔒 Starting Production Application")
    logger.info(f"Environment: {settings.env}")
    logger.info(f"Port: {settings.port}")
    logger.info(f"Authentication: {'Required' if settings.require_auth else 'Not Required'}")
    logger.info(f"Route prefix: '{settings.route_prefix}'")
    logger.info(f"Access at: http://localhost:{settings.port}{settings.route_prefix}")
    logger.info(f"Login at: http://localhost:{settings.port}/login")
    logger.info(f"Swagger docs: http://localhost:{settings.port}/docs")
    
    # Run the server
    uvicorn.run(
        "main_prod:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

if __name__ == "__main__":
    main()
