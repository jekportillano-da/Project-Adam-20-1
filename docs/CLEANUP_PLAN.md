# Workspace Cleanup Plan

## CORE FILES (DO NOT REMOVE) - Required for Production/Demo

### Application Entry Points
- main_prod.py (Production server - port 8080)
- main_dev.py (Demo server - port 8000)

### Core Configuration
- settings.py (Environment-aware configuration)
- .env.dev (Development environment)
- .env.prod (Production environment)

### Application Modules
- auth/ (Authentication module - used by production)
- common/ (Shared utilities and app factory)
- static/ (CSS, JS, images - served by both environments)
- templates/ (HTML templates - used by both environments)

### Database & Dependencies
- requirements.txt
- budget_app.db (Main database)
- budget_assistant.db (Secondary database)

### Documentation (Keep Core)
- README.md (Main documentation)
- DEV_PROD_GUIDE.md (Setup guide)

## FILES TO CLEAN UP

### Test Files (Move to tests/ folder)
- test_*.py (All test files in root)
- test-*.html (Test HTML files)

### Legacy/Backup Files (Move to _archive/)
- gateway_*.py (Old gateway files)
- *_old.md (Old documentation)
- cookies.txt (Debug file)
- debug_*.json (Debug files)
- login_data.json, register_data.json (Test data)

### Temporary/Generated Files (Remove)
- quick_test.py
- simple_test.py
- manual_login_test.py

### Documentation Cleanup (Consolidate)
- Multiple summary files (consolidate into main docs)
- Redundant implementation status files

### Build/Cache Cleanup
- __pycache__/ (Clean up)
- .pytest_cache/ (Keep but ignore in git)

## TARGET STRUCTURE
```
PROJECT-ADAM-20-1/
├── main_prod.py & main_dev.py (Entry points)
├── settings.py (Configuration)
├── .env.* (Environment files)
├── requirements.txt
├── *.db (Databases)
├── README.md, DEV_PROD_GUIDE.md (Core docs)
│
├── auth/ (Authentication module)
├── common/ (Shared utilities)
├── static/ (Frontend assets)
├── templates/ (HTML templates)
├── services/ (Microservices)
├── goals/ (Goals feature)
├── ai/ (AI features)
│
├── tests/ (All test files)
├── docs/ (Documentation)
├── scripts/ (Utility scripts)
├── _archive/ (Legacy files)
│
├── docker-compose.yml (Container config)
├── .git/ (Version control)
└── .vscode/ (Editor config)
```

## CLEANUP STEPS
1. Move test files to tests/
2. Move legacy files to _archive/
3. Consolidate documentation in docs/
4. Remove temporary files
5. Clean __pycache__
6. Update .gitignore
7. Commit organized structure
