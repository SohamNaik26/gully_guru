"""
Configuration module for GullyGuru.
Loads environment variables and provides settings for the application.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # Telegram Bot settings
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    # Database settings
    DATABASE_URL = os.getenv("DATABASE_URL")

    # API settings
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

    # Authentication settings
    ALLOW_UNAUTHENTICATED = os.getenv("ALLOW_UNAUTHENTICATED", "False").lower() in (
        "true",
        "1",
        "t",
    )
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

    # Other settings
    DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

    def __init__(self):
        """Validate required settings."""
        if not self.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")

        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is not set")


# Create a settings instance
settings = Settings()
