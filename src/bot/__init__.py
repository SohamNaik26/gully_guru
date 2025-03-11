"""
Bot module for the GullyGuru application.
"""

import logging
from typing import Optional

from telegram.ext import Application

from src.api.client import APIClient
from src.config import settings

logger = logging.getLogger(__name__)

# Global API client instance
api_client: Optional[APIClient] = None


async def initialize_api_client():
    """
    Initialize the API client.

    Returns:
        The initialized API client
    """
    global api_client

    if api_client is None:
        api_base_url = settings.API_BASE_URL
        logger.info(f"Initializing API client with base URL: {api_base_url}")
        api_client = APIClient(api_base_url)

    return api_client


async def close_api_client():
    """Close the API client."""
    global api_client

    if api_client is not None:
        logger.info("Closing API client")
        await api_client.close()
        api_client = None


async def create_bot_application():
    """
    Create and configure the bot application.

    Returns:
        The configured Application instance
    """
    # Initialize API client
    await initialize_api_client()

    # Create bot application
    application = Application.builder().token(settings.BOT_TOKEN).build()

    # Configure application
    # ... (existing configuration code)

    return application
