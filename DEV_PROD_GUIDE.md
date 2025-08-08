# Dev/Prod Split Commands and Route Documentation

## Quick Start

### Development Environment (Port 8000)
```bash
# Plain Python
python dev_server.py

# Or with Docker
docker-compose up gateway-dev

# Access at:
# http://localhost:8000/demo (main app, no auth required)
# http://localhost:8000/demo/bills (bills page, no auth)
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/debug/status (debug endpoint)
```

### Production Environment (Port 8080)
```bash
# Plain Python
python prod_server.py

# Or with Docker
docker-compose up gateway-prod

# Access at:
# http://localhost:8080/ (main app, auth required)
# http://localhost:8080/login (login page)
# http://localhost:8080/auth/login (login API)
# http://localhost:8080/docs (Swagger UI)
# http://localhost:8080/debug/status (debug endpoint)
```

### Both Environments Simultaneously
```bash
# Run both dev and prod servers
docker-compose up gateway-dev gateway-prod

# Or run services individually
python dev_server.py &
python prod_server.py &
```

## Route Documentation

### Development Environment (:8000)
**Public Routes (No Authentication Required):**
- `GET /demo` - Main application (demo mode)
- `GET /demo/bills` - Bills management page (demo mode)
- `GET /static/*` - Static files (CSS, JS, images)
- `GET /docs` - Swagger UI documentation
- `GET /openapi.json` - OpenAPI specification
- `GET /debug/status` - Server status check
- `GET /debug/auth` - Authentication debug information

### Production Environment (:8080)
**Public Routes (No Authentication Required):**
- `GET /login` - Login page
- `GET /register` - Registration page
- `POST /auth/login` - Login API endpoint
- `POST /auth/register` - Registration API endpoint
- `POST /auth/logout` - Logout API endpoint
- `GET /static/*` - Static files (CSS, JS, images)
- `GET /docs` - Swagger UI documentation
- `GET /openapi.json` - OpenAPI specification
- `GET /debug/status` - Server status check
- `GET /debug/auth` - Authentication debug information

**Protected Routes (Authentication Required):**
- `GET /` - Main application (authenticated users only)
- `GET /bills` - Bills management page (authenticated users only)
- `GET /auth/me` - Current user information

## Environment Configuration

### Using Environment Variables
```bash
# Set environment for development
export APP_ENV=dev

# Set environment for production
export APP_ENV=prod

# Override other settings
export SECRET_KEY=your-production-secret-key
export ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Using .env File
```bash
# Copy example file
cp .env.example .env

# Edit .env file
# Set APP_ENV=dev for development
# Set APP_ENV=prod for production
```

## Development Workflow

1. **Make changes and test on development server first:**
   ```bash
   python dev_server.py
   # Test at http://localhost:8000/demo
   ```

2. **Once validated, test on production server:**
   ```bash
   python prod_server.py
   # Test at http://localhost:8080/ (requires login)
   ```

3. **For Docker workflow:**
   ```bash
   # Test on dev
   docker-compose up gateway-dev
   
   # Test on prod
   docker-compose up gateway-prod
   ```

## Security Notes

- **Development Environment:** No authentication required, all routes public
- **Production Environment:** Authentication required for main app routes
- **Shared Static Files:** Both environments serve the same static files
- **Separate Databases:** Each environment can use separate database files
- **Cookie Security:** Production uses secure cookies, development uses relaxed settings

## Port Summary

- **8000**: Development server (demo mode, no auth)
- **8080**: Production server (auth required)
- **8081-8083**: Microservices (budget, savings, insights)
- **8004**: API Gateway service (if using microservices)
