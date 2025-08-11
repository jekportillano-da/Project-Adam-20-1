#!/usr/bin/env python3
"""
Quick test to check if routes are working
"""
try:
    from common.routes import create_main_routes
    router = create_main_routes(require_auth=True, route_prefix="")
    
    print(f"Router created successfully!")
    print(f"Number of routes: {len(router.routes)}")
    
    for route in router.routes:
        if hasattr(route, 'path'):
            print(f"Route: {route.path}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
