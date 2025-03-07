"""
Module to provide a global API client instance.
This helps avoid circular imports between bot.py and handlers.
"""

import logging
from src.bot.client import APIClient

# Configure logging
logger = logging.getLogger(__name__)

# Create global API client
api_client = APIClient()
