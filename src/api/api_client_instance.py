"""
Module to provide a global API client instance.
This helps avoid circular imports between bot.py and handlers.
"""

import logging
import os
from src.api.client_factory import APIClientFactory
from src.utils.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Check if we're in a test environment
is_test_environment = os.environ.get("TEST_MODE", "").lower() == "true"

# Create global API client
api_base_url = settings.API_BASE_URL
if not api_base_url.endswith("/api"):
    api_base_url = f"{api_base_url}/api"

if is_test_environment:
    logger.info("Test environment detected - using mock API client")
    # In test mode, we'll use a special test URL that won't affect production
    api_base_url = "http://testserver/api"

logger.info(f"Initializing API client with base URL: {api_base_url}")
# Use test token for authentication in development
api_client = APIClientFactory(base_url=api_base_url, auth_token="test")
