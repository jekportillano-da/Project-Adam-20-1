#!/usr/bin/env python3
"""Simple test to verify route configuration"""

from fastapi import FastAPI
from settings import get_dev_settings
from common.app_factory import create_app

# Create test app
settings = get_dev_settings()
app = create_app(settings)

if __name__ == "__main__":
    print(f"Settings: {settings}")
    print(f"Routes available:")
    
    for route in app.routes:
        try:
            if hasattr(route, 'path'):
                path = getattr(route, 'path', 'unknown')
                print(f"  {path}")
        except:
            pass
    
    print(f"\nStarting simple test server...")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
