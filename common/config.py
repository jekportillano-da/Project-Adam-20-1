# Configuration Management Module
import os
from typing import Optional
import secrets

class Settings:
    """Application settings with validation"""
    
    def __init__(self):
        # Security
        self.secret_key = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        
        # API Keys
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        
        # Database
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./budget_assistant.db")
        
        # Services
        self.budget_service_url = os.getenv("BUDGET_SERVICE_URL", "http://localhost:8081")
        self.savings_service_url = os.getenv("SAVINGS_SERVICE_URL", "http://localhost:8082")
        self.insights_service_url = os.getenv("INSIGHTS_SERVICE_URL", "http://localhost:8083")
        
        # Server
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))
        self.debug = os.getenv("DEBUG", "False").lower() == "true"
        self.environment = os.getenv("ENVIRONMENT", "development")
        
        # Security & CORS
        allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000")
        self.allowed_origins = [origin.strip() for origin in allowed_origins_str.split(',')]
        self.max_request_size = int(os.getenv("MAX_REQUEST_SIZE", str(1024 * 1024)))  # 1MB
        self.rate_limit_requests = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.rate_limit_window = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour
        
        # Cookie settings
        self.cookie_secure = self.environment == "production"  # Only secure cookies in production
        self.cookie_samesite = "lax"  # More permissive for localhost development
        self.cookie_domain = None  # Let browser determine domain
        self.cookie_path = "/"  # Available to all routes
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_format = os.getenv("LOG_FORMAT", "json")
        
        # Validate critical settings
        self._validate()
    
    def _validate(self):
        """Validate critical configuration"""
        if self.secret_key == "your-secret-key-here-please-change-in-production":
            raise ValueError("Please set a proper SECRET_KEY environment variable")
        
        if not self.groq_api_key and self.environment == "production":
            raise ValueError("GROQ_API_KEY must be set in production")
    
    @property
    def services(self):
        """Get service URLs as dictionary"""
        return {
            "budget": self.budget_service_url,
            "savings": self.savings_service_url,
            "insights": self.insights_service_url
        }

# Global settings instance
settings = Settings()
