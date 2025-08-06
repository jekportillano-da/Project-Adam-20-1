# Project Architecture

## Overview
Project Adam is a Flask-based web application that provides personalized budget advice for Filipino users. The application uses the DeepSeek API to generate culturally relevant financial recommendations based on user-provided budget constraints.

## Directory Structure
```
Project-Adam/
├── app/                    # Main application package
│   ├── __init__.py        # App factory and configuration
│   ├── routes.py          # Route handlers
│   ├── services/          # Business logic
│   │   ├── __init__.py
│   │   └── generator.py   # DeepSeek integration
│   ├── static/            # Static assets
│   │   ├── css/
│   │   └── js/
│   └── templates/         # Jinja2 templates
├── docs/                  # Documentation
├── tests/                 # Test suite (future)
├── .env.example          # Environment variable template
├── run.py                # Application entry point
└── schema.sql            # Database schema
```

## Components

### App Factory (`app/__init__.py`)
- Creates and configures the Flask application
- Registers blueprints and extensions
- Loads configuration from environment variables

### Routes (`app/routes.py`)
- Defines HTTP endpoints
- Handles request validation
- Coordinates between services and templates

### Services (`app/services/`)
- `generator.py`: Handles DeepSeek API integration
- Implements business logic for budget calculations
- Manages error handling and logging

### Templates (`app/templates/`)
- Contains Jinja2 templates for rendering HTML
- Implements responsive design
- Handles client-side interactivity

## Data Flow
1. User submits budget amount and duration
2. Route handler validates input
3. Budget service calculates daily equivalent
4. DeepSeek service generates personalized advice
5. Response is formatted and returned to user

## Future Enhancements
- Database integration for tip storage
- User authentication system
- Feedback collection
- Analytics dashboard
