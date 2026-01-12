from pydantic_settings import BaseSettings
from typing import List, Optional
from pydantic import field_validator
import os


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Joyfull UI Hub Backend"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = False
    
    # Database settings
    DATABASE_URL: str
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 3600  # 1 hour
    
    # JWT settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS settings
    CORS_ORIGINS: str = "*"  # Comma-separated list of origins
    
    # Email settings (for password reset)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@joyfullhub.com"
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # "json" or "standard"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert the CORS_ORIGINS string to a list."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    @field_validator('DATABASE_URL')
    @classmethod
    def validate_database_url(cls, v):
        if not v:
            raise ValueError('DATABASE_URL cannot be empty')
        return v
    
    @field_validator('JWT_SECRET_KEY')
    @classmethod
    def validate_jwt_secret_key(cls, v):
        if not v:
            raise ValueError('JWT_SECRET_KEY cannot be empty')
        if len(v) < 16:
            raise ValueError('JWT_SECRET_KEY should be at least 16 characters long for security')
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create a global settings instance
settings = Settings()