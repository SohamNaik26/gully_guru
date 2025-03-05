import os
from typing import List
from pydantic import BaseSettings, PostgresDsn

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: PostgresDsn
    
    # Authentication
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str
    
    # External APIs
    KAGGLE_USERNAME: str = ""
    KAGGLE_KEY: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings() 