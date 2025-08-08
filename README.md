# 💰 Smart Budget Assistant

A modern, AI-powered budget planning application built with FastAPI, featuring separate development and production environments with comprehensive financial insights.

## 🏗️ Architecture Overview

```
PROJECT-ADAM-20-1-1/
├── 🎭 Demo Environment (Port 8000)    │ 🔐 Production Environment (Port 8080)
│   ├── No authentication required     │   ├── JWT-based authentication  
│   ├── Routes: /demo/*                │   ├── Routes: /*
│   └── Public access demo             │   └── Secure user accounts
│                                      │
├── 📁 Core Structure                  │
│   ├── auth/                          │ # Authentication module (prod only)
│   │   ├── routes.py                  │ # Login/register endpoints
│   │   ├── models.py                  │ # User/token models
│   │   └── database.py                │ # User database operations
│   │                                  │
│   ├── common/                        │ # Shared application logic
│   │   ├── app_factory.py             │ # FastAPI app creation
│   │   └── routes.py                  │ # Shared route handlers
│   │                                  │
│   ├── services/                      │ # Microservices architecture
│   │   ├── budget-service/            │ # Budget calculation logic
│   │   ├── savings-service/           │ # Savings forecast algorithms
│   │   └── insights-service/          │ # Financial insights & AI integration
│   │                                  │
│   ├── static/                        │ # Frontend assets (CSS/JS/images)
│   ├── templates/                     │ # Jinja2 HTML templates
│   └── tests/                         │ # Comprehensive test suite
│                                      │
├── 🚀 Entry Points                    │
│   ├── main_dev.py                    │ # Demo application (8000)
│   ├── main_prod.py                   │ # Production application (8080)
│   └── gateway_enhanced.py            │ # Enhanced gateway with resilience
│                                      │
└── ⚙️ Configuration & Deployment      │
    ├── settings.py                    │ # Environment-aware configuration
    ├── docker-compose.yml             │ # Development containers
    ├── docker-compose.production.yml  │ # Production deployment
    └── .env.{dev,prod}                │ # Environment variables
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip or Poetry
- Docker (optional)

### Installation

#### Option 1: Using pip
```bash
# Clone the repository
git clone <repository-url>
cd Project-Adam-20-1-1

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Option 2: Using Poetry
```bash
# Install dependencies with Poetry
poetry install
poetry shell
```

### Environment Configuration

Copy environment files and configure as needed:
```bash
cp .env.example .env.dev
cp .env.example .env.prod

# Edit .env.dev and .env.prod with your configuration
# Add API keys for AI features (GROQ_API_KEY, etc.)
```

## 🎭 Running the Application

### Development/Demo Environment (Port 8000)
```bash
# Method 1: Direct Python execution
python main_dev.py

# Method 2: Using uvicorn
uvicorn main_dev:app --reload --port 8000

# Method 3: Using batch scripts
./run_dev.bat     # Windows
./run_dev.ps1     # PowerShell

# Method 4: Using Docker
docker-compose up gateway-dev
```
**Access at:** http://localhost:8000/demo

**Features:**
- ✅ No authentication required
- ✅ Public demo access
- ✅ Full budget planning features
- ✅ AI-powered insights
- ✅ Bill tracking and integration
- ✅ Savings forecasting

### Production Environment (Port 8080)
```bash
# Method 1: Direct Python execution  
python main_prod.py

# Method 2: Using uvicorn
uvicorn main_prod:app --reload --port 8080

# Method 3: Using batch scripts
./run_prod.bat    # Windows
./run_prod.ps1    # PowerShell

# Method 4: Using Docker
docker-compose up gateway-prod
```
**Access at:** http://localhost:8080/

**Features:**
- 🔐 JWT-based authentication required
- 👤 User registration and login
- 🛡️ Secure user sessions
- 💾 Personal data persistence
- 📊 Individual user analytics

### Both Environments Simultaneously
```bash
# Run both demo and production together
docker-compose up gateway-dev gateway-prod

# Or in separate terminals
python main_dev.py &
python main_prod.py &
```

## 🐳 Docker Deployment

### Development Deployment
```bash
# Build and run all services
docker-compose up --build

# Run specific services
docker-compose up gateway-dev budget-service savings-service
```

### Production Deployment
```bash
# Full production stack with monitoring
docker-compose -f docker-compose.production.yml up --build

# Includes: PostgreSQL, Redis, Nginx, monitoring
```

## 🧪 Testing

### Run Test Suite
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_comprehensive.py::TestBudgetService -v
python -m pytest tests/test_comprehensive.py::TestSecurity -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

### Manual Testing
```bash
# Test development environment
curl http://localhost:8000/demo/health

# Test production environment (after login)
curl http://localhost:8080/health
```

## 🔌 API Endpoints

### Demo Environment (`/demo/*`)
- `GET /demo` - Main budget planning interface
- `GET /demo/bills` - Bill tracking interface  
- `POST /demo/api/budget/calculate` - Budget calculation
- `POST /demo/api/savings/forecast` - Savings projections
- `POST /demo/api/insights/analyze` - Financial insights
- `POST /demo/api/tip` - AI-powered tips

### Production Environment (`/*`)
- `GET /` - Main application (requires auth)
- `GET /login` - User login page
- `GET /register` - User registration
- `POST /auth/login` - Authentication endpoint
- `POST /auth/register` - User registration endpoint
- All budget APIs (requires authentication)

## 🤖 AI Integration

The application integrates with multiple AI providers:

### Supported AI Services
- **GROQ** - Primary AI provider for budget insights
- **OpenAI** - Alternative AI provider
- **DeepSeek** - Cost-effective AI option

### Configuration
```bash
# Add to .env.dev and .env.prod
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### AI Features
- 💡 Personalized budget recommendations
- 📈 Spending pattern analysis
- 🎯 Smart savings strategies
- 🔍 Financial health insights
- 💰 Expense optimization suggestions

## 🛠️ Development

### Code Quality
```bash
# Format code
black .
isort .

# Lint code
flake8 .
mypy .

# Type checking with pyright
pyright
```

### Adding New Features
1. Add routes in `common/routes.py` for shared functionality
2. Add auth-specific routes in `auth/routes.py`
3. Update templates in `templates/`
4. Add tests in `tests/`
5. Update documentation

### Environment Variables

#### Development (.env.dev)
```bash
ENV=dev
PORT=8000
ROUTE_PREFIX=/demo
DEBUG=true
LOG_LEVEL=DEBUG
SECRET_KEY=dev-secret-key
```

#### Production (.env.prod)
```bash
ENV=prod
PORT=8080
ROUTE_PREFIX=
DEBUG=false
LOG_LEVEL=INFO
SECRET_KEY=production-ready-secret-key
DATABASE_URL=postgresql://user:pass@localhost/budget_db
```

## 🔐 Security Features

- 🛡️ JWT-based authentication
- 🔒 Password hashing with bcrypt
- 🌐 CORS protection
- 🚫 SQL injection prevention
- 🔍 Input validation and sanitization
- 📊 Rate limiting
- 🛠️ Security headers

## 📊 Monitoring & Logging

### Health Checks
- `GET /health` - Application health status
- `GET /metrics` - Prometheus metrics (production)
- Database connectivity checks
- Service dependency validation

### Logging
- Structured JSON logging
- Request/response logging
- Error tracking and reporting
- Performance monitoring

## 🔧 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Kill process using the port
lsof -ti:8000 | xargs kill -9  # Linux/Mac
netstat -ano | findstr :8000   # Windows
```

**Database issues:**
```bash
# Reset database
rm budget_app.db budget_assistant.db
python -c "from auth.database import init_db; init_db()"
```

**Dependencies issues:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

For support and questions:
- Create an issue in this repository
- Check the troubleshooting section above
- Review the comprehensive test suite for examples

---

**Built with ❤️ using FastAPI, modern Python, and AI integration**

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
