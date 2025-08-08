# Environment-aware settings for dev/prod split
import os
from pathlib import Path
from typing import Optional
import secrets
from dotenv import load_dotenv

class AppSettings:
    """Environment-aware application settings"""
    
    def __init__(self, env_file: Optional[str] = None):
        # Load environment-specific .env file
        if env_file:
            load_dotenv(env_file)
        else:
            # Auto-detect based on ENV variable
            env = os.getenv("ENV", "dev")
            if env == "prod":
                load_dotenv(".env.prod")
            else:
                load_dotenv(".env.dev")
        
        # Core settings
        self.env = os.getenv("ENV", "dev")
        self.port = int(os.getenv("PORT", "8000"))
        self.route_prefix = os.getenv("ROUTE_PREFIX", "/demo")
        self.debug = os.getenv("DEBUG", "true").lower() == "true"
        
        # Authentication settings
        self.require_auth = self.env == "prod"  # Only prod requires auth
        self.secret_key = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        
        # API Keys
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        
        # Database
        self.database_url = os.getenv("DATABASE_URL", f"sqlite:///./budget_assistant_{self.env}.db")
        
        # Services
        self.budget_service_url = os.getenv("BUDGET_SERVICE_URL", "http://localhost:8001")
        self.savings_service_url = os.getenv("SAVINGS_SERVICE_URL", "http://localhost:8002")
        self.insights_service_url = os.getenv("INSIGHTS_SERVICE_URL", "http://localhost:8003")
        
        # Server settings
        self.host = "0.0.0.0"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # CORS settings
        allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000,http://localhost:8080")
        self.allowed_origins = [origin.strip() for origin in allowed_origins_str.split(',')]
        
        # Cookie settings
        self.cookie_secure = os.getenv("COOKIE_SECURE", "false").lower() == "true" if self.env == "prod" else False
        self.cookie_samesite = os.getenv("COOKIE_SAMESITE", "strict") if self.env == "prod" else "lax"
        self.cookie_domain = None
        self.cookie_path = "/"
        
        # App title
        if self.env == "prod":
            self.app_title = "Smart Budget Assistant"
        else:
            self.app_title = "Smart Budget Assistant - Demo"
        
        # Validate production settings
        if self.env == "prod":
            self._validate_production()
    
    def _validate_production(self):
        """Validate critical settings for production"""
        if self.secret_key == "production-secret-key-please-change-this":
            raise ValueError("Please change the default SECRET_KEY in .env.prod")
        
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
    
    def __repr__(self):
        return f"AppSettings(env={self.env}, port={self.port}, auth={self.require_auth}, prefix='{self.route_prefix}')"

# Factory functions for specific environments
def get_dev_settings() -> AppSettings:
    """Get development environment settings"""
    return AppSettings(".env.dev")

def get_prod_settings() -> AppSettings:
    """Get production environment settings"""
    return AppSettings(".env.prod")

def get_settings() -> AppSettings:
    """Get settings based on current environment"""
    return AppSettings()
