#!/usr/bin/env python3
"""Quick test to check the routes are properly configured"""

from settings import get_dev_settings
from common.app_factory import create_app

# Create app with dev settings
settings = get_dev_settings()
app = create_app(settings)

print(f"Settings: {settings}")
print(f"Route prefix: '{settings.route_prefix}'")
print(f"Require auth: {settings.require_auth}")
print()

print("Available routes:")
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        methods = list(route.methods) if hasattr(route, 'methods') else ['N/A']
        print(f"  {methods} {route.path}")
    elif hasattr(route, 'path'):
        print(f"  [MOUNT] {route.path}")

print()
print("Testing route creation...")
from common.routes import create_main_routes, create_debug_routes

main_router = create_main_routes(
    require_auth=settings.require_auth,
    route_prefix=settings.route_prefix
)
debug_router = create_debug_routes()

print(f"Main router prefix: '{main_router.prefix}'")
print(f"Debug router prefix: '{debug_router.prefix}'")
print("Main router routes:")
for route in main_router.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        methods = list(route.methods) if hasattr(route, 'methods') else ['N/A']
        print(f"  {methods} {route.path}")
