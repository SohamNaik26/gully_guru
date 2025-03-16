"""
Bot package for the GullyGuru application.
This package contains the Telegram bot implementation focused on onboarding.
"""

import logging
from telegram.ext import Application
from src.bot.api_client.base import initialize_api_client as initialize_client
from src.bot.api_client.base import get_api_client
from src.utils.config import settings

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

# Make API functions available from the bot package
from src.bot.api_client.onboarding import (  # noqa
    handle_complete_onboarding,
    create_gully_for_group,
    add_admin_to_gully,
)

from src.bot.features.squad import (  # noqa
    register_squad_handlers,
    squad_entry_point,
    squad_menu_entry,
    view_squad,
)

__all__ = [
    "initialize_api_client",
    "close_api_client",
    "create_bot_application",
    "get_user",
    "create_user",
    "get_gully",
    "get_gully_by_telegram_id",
    "join_gully",
    "get_user_gullies",
    "get_user_gully_participation",
    "create_gully",
    "handle_complete_onboarding",
    "create_gully_for_group",
    "add_admin_to_gully",
    "register_squad_handlers",
    "squad_menu_entry",
    "view_squad",
]


# Initialize API client
async def initialize_api_client():
    """Initialize the API client."""
    logger.info("Initializing API client")
    return await initialize_client()


# Close API client
async def close_api_client():
    """Close the API client."""
    logger.info("Closing API client")
    client = await get_api_client()
    if client:
        await client.close()


async def create_bot_application():
    """
    Create and configure the bot application.

    Returns:
        Application: The configured bot application
    """
    # Create application
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Register handlers
    from src.bot.features import register_handlers

    register_handlers(application)

    return application
