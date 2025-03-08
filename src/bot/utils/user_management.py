"""
Utility functions for user management.
Centralizes user creation and registration logic to avoid code duplication.
"""

import logging
from telegram import User as TelegramUser
from src.bot.api_client_instance import api_client

logger = logging.getLogger(__name__)


async def ensure_user_exists(telegram_user: TelegramUser) -> dict:
    """
    Ensures a user exists in the database. Creates the user if they don't exist.
    Returns the user data from the database.

    Args:
        telegram_user: The Telegram user object

    Returns:
        dict: The user data from the database
    """
    # Check if user exists in database
    db_user = await api_client.get_user(telegram_user.id)

    if not db_user:
        # Create a new user with Telegram information
        name = telegram_user.first_name
        if telegram_user.last_name:
            name += f" {telegram_user.last_name}"

        user_data = {
            "telegram_id": telegram_user.id,
            "full_name": name,
            "username": telegram_user.username or f"user_{telegram_user.id}",
        }

        # Create the user
        db_user = await api_client.create_user(user_data)
        if not db_user:
            logger.error(f"Failed to create user {telegram_user.id} in database")
            return None

        logger.info(f"Created new user {telegram_user.id} in database")

    return db_user


async def ensure_user_in_gully(user_id: int, gully_id: int) -> bool:
    """
    Ensures a user is a member of a specific gully.
    Adds the user to the gully if they're not already a member.

    Args:
        user_id: The user's Telegram ID
        gully_id: The gully ID

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if user is already in the gully
        is_member = await api_client.is_user_in_gully(user_id, gully_id)
        if not is_member:
            # Add user to gully
            await api_client.add_user_to_gully(user_id, gully_id)
            logger.info(f"User {user_id} added to gully {gully_id}")
        return True
    except Exception as e:
        logger.error(f"Error ensuring user {user_id} is in gully {gully_id}: {e}")
        return False


async def assign_admin_role(user_id: int, gully_id: int) -> bool:
    """
    Assigns admin role to a user in a specific gully.

    Args:
        user_id: The user's Telegram ID
        gully_id: The gully ID

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        await api_client.assign_admin_role(user_id, gully_id)
        logger.info(f"User {user_id} assigned as admin in gully {gully_id}")
        return True
    except Exception as e:
        logger.error(
            f"Error assigning admin role to user {user_id} in gully {gully_id}: {e}"
        )
        return False
