# Environment-specific settings for dev/prod split
import os
from enum import Enum
from typing import Optional
import secrets

class AppEnvironment(str, Enum):
    DEV = "dev"
    PROD = "prod"

class AppSettings:
    """Application settings with dev/prod environment support"""
    
    def __init__(self, app_env: Optional[AppEnvironment] = None):
        # Get environment from parameter or environment variable
        self.app_env = app_env or AppEnvironment(os.getenv("APP_ENV", "dev"))
        
        # Security
        self.secret_key = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        
        # Environment-specific configuration
        if self.app_env == AppEnvironment.DEV:
            self.host = "0.0.0.0"
            self.port = 8000
            self.require_auth = False
            self.route_prefix = "/demo"
            self.app_title = "Smart Budget Assistant - Development"
            self.debug = True
        else:  # PROD
            self.host = "0.0.0.0"
            self.port = 8080
            self.require_auth = True
            self.route_prefix = ""
            self.app_title = "Smart Budget Assistant"
            self.debug = os.getenv("DEBUG", "False").lower() == "true"
        
        # API Keys
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        
        # Database
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./budget_assistant.db")
        
        # Services
        self.budget_service_url = os.getenv("BUDGET_SERVICE_URL", "http://localhost:8081")
        self.savings_service_url = os.getenv("SAVINGS_SERVICE_URL", "http://localhost:8082")
        self.insights_service_url = os.getenv("INSIGHTS_SERVICE_URL", "http://localhost:8083")
        
        # Security & CORS
        if self.app_env == AppEnvironment.DEV:
            allowed_origins_default = "http://localhost:3000,http://localhost:8000"
        else:
            allowed_origins_default = "http://localhost:3000,http://localhost:8080"
            
        allowed_origins_str = os.getenv("ALLOWED_ORIGINS", allowed_origins_default)
        self.allowed_origins = [origin.strip() for origin in allowed_origins_str.split(',')]
        
        # Cookie settings
        environment = os.getenv("ENVIRONMENT", "development")
        self.cookie_secure = environment == "production"
        self.cookie_samesite = "lax"
        self.cookie_domain = None
        self.cookie_path = "/"
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Validate critical settings for production
        if self.app_env == AppEnvironment.PROD:
            self._validate_production()
    
    def _validate_production(self):
        """Validate critical configuration for production"""
        if self.secret_key == "your-secret-key-here-please-change-in-production":
            raise ValueError("Please set a proper SECRET_KEY environment variable for production")
        
        if not self.groq_api_key:
            print("Warning: GROQ_API_KEY not set in production")
    
    @property
    def services(self):
        """Get service URLs as dictionary"""
        return {
            "budget": self.budget_service_url,
            "savings": self.savings_service_url,
            "insights": self.insights_service_url
        }

# Factory functions for each environment
def get_dev_settings() -> AppSettings:
    """Get development environment settings"""
    return AppSettings(AppEnvironment.DEV)

def get_prod_settings() -> AppSettings:
    """Get production environment settings"""
    return AppSettings(AppEnvironment.PROD)
