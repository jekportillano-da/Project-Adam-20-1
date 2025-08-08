# Smart Budget Assistant - Dev/Prod Split

## Overview

This FastAPI application has been restructured with a clean separation between demo and production environments:

- **Demo Environment** (Port 8000): Public access, no authentication required, routes under `/demo`
- **Production Environment** (Port 8080): Authentication required, routes at root `/`

## Quick Start

### Development/Demo Environment
```bash
# Direct Python execution
python main_dev.py

# Using uvicorn directly  
uvicorn main_dev:app --reload --port 8000

# Using Docker
docker-compose up gateway-dev
```

**Access at:** http://localhost:8000/demo

### Production Environment
```bash
# Direct Python execution
python main_prod.py

# Using uvicorn directly
uvicorn main_prod:app --reload --port 8080

# Using Docker
docker-compose up gateway-prod
```

**Access at:** http://localhost:8080/ (requires login)

### Both Environments Simultaneously
```bash
# Run both demo and production
docker-compose up gateway-dev gateway-prod

# Or run separately in different terminals
python main_dev.py &
python main_prod.py &
```

## File Structure

```
PROJECT-ADAM-20-1-1/
├── auth/                     # Authentication module (shared, used by prod only)
│   ├── __init__.py
│   ├── auth_utils.py
│   ├── database.py
│   ├── dependencies.py
│   ├── models.py
│   └── routes.py
├── common/                   # Shared utilities and routes
│   ├── __init__.py
│   ├── app_factory.py       # FastAPI app creation
│   └── routes.py            # Shared route handlers
├── services/                 # Microservices (shared)
│   ├── budget-service/
│   ├── savings-service/
│   └── insights-service/
├── static/                   # Shared CSS/JS/images
├── templates/                # Shared Jinja templates
│
├── main_dev.py              # Demo entry point (port 8000, /demo prefix)
├── main_prod.py             # Production entry point (port 8080, auth required)
│
├── settings.py              # Environment-aware configuration
├── .env.dev                 # Development environment variables
├── .env.prod                # Production environment variables
│
├── docker-compose.yml       # Both services: gateway-dev & gateway-prod
├── Dockerfile.gateway       # Container definition
└── requirements.txt         # Python dependencies
```

## Environment Configuration

### Development (.env.dev)
```bash
ENV=dev
PORT=8000
ROUTE_PREFIX=/demo
SECRET_KEY=dev-secret-key
DEBUG=true
```

### Production (.env.prod)
```bash
ENV=prod
PORT=8080
ROUTE_PREFIX=/
SECRET_KEY=production-ready-secret-key
DEBUG=false
COOKIE_SECURE=true
```

## Route Documentation

### Demo Environment (:8000) - No Authentication
| Route | Description |
|-------|-------------|
| `GET /demo` | Main application (demo mode) |
| `GET /demo/bills` | Bills management page |
| `GET /static/*` | Static files (CSS, JS, images) |
| `GET /docs` | Swagger UI documentation |
| `GET /debug/status` | Server status check |
| `GET /debug/auth` | Authentication debug info |

### Production Environment (:8080) - Authentication Required

**Public Routes:**
| Route | Description |
|-------|-------------|
| `GET /login` | Login page |
| `GET /register` | Registration page |
| `POST /auth/login` | Login API endpoint |
| `POST /auth/register` | Registration API endpoint |
| `POST /auth/logout` | Logout API endpoint |
| `GET /static/*` | Static files |
| `GET /docs` | Swagger UI documentation |
| `GET /debug/*` | Debug endpoints |

**Protected Routes (Auth Required):**
| Route | Description |
|-------|-------------|
| `GET /` | Main application |
| `GET /bills` | Bills management page |
| `GET /auth/me` | Current user information |

## Development Workflow

1. **Make changes and test on demo first:**
   ```bash
   python main_dev.py
   # Test at http://localhost:8000/demo
   ```

2. **Validate on production environment:**
   ```bash
   python main_prod.py
   # Test at http://localhost:8080/ (requires login)
   ```

3. **For Docker workflow:**
   ```bash
   # Test both environments
   docker-compose up gateway-dev gateway-prod
   ```

## Features

### Shared Components
- ✅ Same templates and static files
- ✅ Same business logic (bills, insights, budget)
- ✅ Same database schema
- ✅ Same microservices integration

### Environment-Specific Features
- ✅ Demo: Public access, no registration needed
- ✅ Production: JWT authentication, secure cookies
- ✅ Different route prefixes (`/demo` vs `/`)
- ✅ Environment-aware settings
- ✅ Separate databases (dev vs prod)

### Authentication (Production Only)
- ✅ JWT-based authentication with httpOnly cookies
- ✅ User registration and login
- ✅ Password hashing with bcrypt
- ✅ Secure session management

## API Documentation

Swagger UI is available on both environments:
- Demo: http://localhost:8000/docs
- Production: http://localhost:8080/docs

## Security Notes

- **Demo Environment**: All routes are public for testing
- **Production Environment**: Main application routes require authentication
- **Cookie Security**: Production uses secure, SameSite cookies
- **CORS**: Environment-specific allowed origins
- **Database Separation**: Different SQLite files for dev/prod

## Migration from Legacy

This structure replaces the previous `gateway.py`, `dev_server.py`, and `prod_server.py` files with:
- Clean separation of concerns
- Environment-aware configuration  
- Shared code without duplication
- Clear routing structure

All existing functionality has been preserved and enhanced.
