"""
API client initialization module.
Handles initializing API clients once and providing them throughout the application.
"""

import logging
import asyncio
from typing import Dict, Any, Optional

from src.bot.api_client.base import get_api_client
from src.bot.api_client.onboarding import get_onboarding_client
from src.bot.api_client.squad import get_squad_client

# Configure logging
logger = logging.getLogger(__name__)

# Global client instances
_onboarding_client = None
_squad_client = None
_api_client = None
_initialized = False
_initialization_lock = asyncio.Lock()


async def initialize_clients() -> bool:
    """
    Initialize all API clients.

    Returns:
        bool: True if initialization was successful, False otherwise
    """
    global _onboarding_client, _squad_client, _api_client, _initialized

    # Use a lock to prevent multiple concurrent initializations
    async with _initialization_lock:
        if _initialized:
            logger.debug("Clients already initialized")
            return True

        logger.info("Initializing API clients...")

        try:
            # Initialize base API client first
            _api_client = await get_api_client()

            # Initialize other clients using the base client
            _onboarding_client = await get_onboarding_client()
            _squad_client = await get_squad_client()

            # Test connection with a simple API call
            users = await _onboarding_client.get_users()

            _initialized = True
            logger.info("API clients initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize API clients: {e}")
            return False


async def get_initialized_onboarding_client():
    """
    Get the initialized onboarding client.

    Returns:
        OnboardingApiClient or None if initialization failed
    """
    global _onboarding_client, _initialized

    if not _initialized:
        success = await initialize_clients()
        if not success:
            return None

    return _onboarding_client


async def get_initialized_squad_client():
    """
    Get the initialized squad client.

    Returns:
        SquadApiClient or None if initialization failed
    """
    global _squad_client, _initialized

    if not _initialized:
        success = await initialize_clients()
        if not success:
            return None

    return _squad_client


async def wait_for_api(max_attempts: int = 5, delay: int = 2) -> bool:
    """
    Wait for the API to be available by attempting to initialize clients.

    Args:
        max_attempts: Maximum number of attempts
        delay: Delay between attempts in seconds

    Returns:
        bool: True if API is available, False otherwise
    """
    logger.info("Checking API availability...")

    for attempt in range(1, max_attempts + 1):
        try:
            success = await initialize_clients()
            if success:
                logger.info("API is available!")
                return True
        except Exception as e:
            logger.warning(f"API not available (attempt {attempt}/{max_attempts}): {e}")

        if attempt < max_attempts:
            logger.info(f"Waiting {delay} seconds before next attempt...")
            await asyncio.sleep(delay)

    logger.error(f"API not available after {max_attempts} attempts")
    return False
