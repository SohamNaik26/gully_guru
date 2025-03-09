"""
Module to provide a global API client instance.
This helps avoid circular imports between bot.py and handlers.
"""

import logging
from src.api.client_factory import APIClientFactory
from src.utils.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create global API client
api_base_url = settings.API_BASE_URL
if not api_base_url.endswith("/api"):
    api_base_url = f"{api_base_url}/api"

logger.info(f"Initializing API client with base URL: {api_base_url}")
api_client = APIClientFactory(base_url=api_base_url)
