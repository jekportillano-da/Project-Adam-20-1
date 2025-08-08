#!/usr/bin/env python3
"""Test script to validate the development server setup"""

import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    logger.info("Testing imports...")
    
    from settings import get_dev_settings
    logger.info("✓ Settings imported")
    
    from common.app_factory import create_app
    logger.info("✓ App factory imported")
    
    from auth import auth_router
    logger.info("✓ Auth router imported")
    
    logger.info("Creating development settings...")
    settings = get_dev_settings()
    logger.info(f"✓ Dev settings created: port={settings.port}, auth={settings.require_auth}, prefix='{settings.route_prefix}'")
    
    logger.info("Creating FastAPI app...")
    app = create_app(settings)
    logger.info("✓ FastAPI app created successfully")
    
    # Test routes
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append(f"{getattr(route, 'methods', 'N/A')} {getattr(route, 'path', 'N/A')}")
        elif hasattr(route, 'path'):
            routes.append(f"ALL {getattr(route, 'path', 'N/A')}")
    
    logger.info(f"✓ App has {len(routes)} routes:")
    for route in routes[:10]:  # Show first 10 routes
        logger.info(f"  {route}")
    
    logger.info("All tests passed! Starting server...")
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", reload=False)
    
except Exception as e:
    logger.error(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
