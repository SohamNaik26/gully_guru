#!/usr/bin/env python
"""
Test script for user management functions.
"""

import asyncio
import logging
from telegram import User as TelegramUser
from src.bot.utils.user_management import ensure_user_exists

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def test_ensure_user_exists():
    """Test the ensure_user_exists function."""
    # Create a mock Telegram user
    mock_user = TelegramUser(
        id=987654321,
        first_name="Test",
        last_name="User",
        is_bot=False,
        username="testuser",
    )

    # Call ensure_user_exists
    logger.info("Calling ensure_user_exists...")
    db_user = await ensure_user_exists(mock_user)

    # Log the result
    if db_user:
        logger.info(f"User created/found successfully: {db_user}")
    else:
        logger.error("Failed to create/find user")


if __name__ == "__main__":
    asyncio.run(test_ensure_user_exists())
