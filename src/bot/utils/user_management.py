"""
Utility functions for user management.
Centralizes user creation and registration logic to avoid code duplication.
"""

import logging
from telegram import User as TelegramUser
from src.bot.api_client_instance import api_client

logger = logging.getLogger(__name__)


async def ensure_user_exists(
    telegram_user: TelegramUser, from_gully_id: int = None
) -> dict:
    """
    Ensures a user exists in the database. Creates the user if they don't exist.
    Returns the user data from the database.

    Args:
        telegram_user: The Telegram user object
        from_gully_id: Optional gully ID from where the user was initiated

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

        # If gully ID was provided, ensure user is in that gully
        if from_gully_id and db_user:
            await ensure_user_in_gully(db_user["id"], from_gully_id)

    return db_user


async def ensure_user_in_gully(user_id: int, gully_id: int) -> dict:
    """
    Ensures a user is a member of a specific gully.
    Adds the user to the gully if they're not already a member.

    Args:
        user_id: The user's database ID
        gully_id: The gully ID

    Returns:
        dict: The gully participant data if successful, None otherwise
    """
    try:
        # Get all gully participations for the user
        participations = await api_client.get_user_gully_participations(user_id)

        # Check if user is already in the gully
        for participation in participations:
            if participation.get("id") == gully_id:
                return participation

        # User is not in the gully, add them
        participant = await api_client.add_user_to_gully(user_id, gully_id)
        if participant:
            logger.info(f"Added user {user_id} to gully {gully_id}")
            return participant

        logger.error(f"Failed to add user {user_id} to gully {gully_id}")
        return None
    except Exception as e:
        logger.error(f"Error ensuring user in gully: {e}")
        return None


async def assign_admin_role(user_id: int, gully_id: int) -> bool:
    """
    Assigns admin role to a user in a specific gully.

    Args:
        user_id: The user's database ID
        gully_id: The gully ID

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get the user's participation in the gully
        participant = await api_client.get_user_gully_participation(user_id, gully_id)

        if not participant:
            # User is not in the gully yet, add them first
            participant = await ensure_user_in_gully(user_id, gully_id)
            if not participant:
                return False

        # Update the participant's role to admin
        await api_client.update_gully_participant_role(participant["id"], "admin")
        logger.info(f"User {user_id} assigned as admin in gully {gully_id}")
        return True
    except Exception as e:
        logger.error(
            f"Error assigning admin role to user {user_id} in gully {gully_id}: {e}"
        )
        return False


async def get_active_gully(user_id: int) -> dict:
    """
    Gets the user's active gully.

    Args:
        user_id: The user's database ID

    Returns:
        dict: The active gully data if found, None otherwise
    """
    try:
        # Get all user's gully participations
        participations = await api_client.get_user_gully_participations(user_id)

        # Find the active one
        active_participation = next(
            (p for p in participations if p.get("is_active", False)), None
        )

        if active_participation:
            # Get the full gully details
            gully = await api_client.get_gully(active_participation["gully_id"])
            return gully

        return None
    except Exception as e:
        logger.error(f"Error getting active gully for user {user_id}: {e}")
        return None


async def set_active_gully(user_id: int, gully_id: int) -> bool:
    """
    Set a gully as the active gully for a user.

    Args:
        user_id: The user's database ID
        gully_id: The gully ID to set as active

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure user is in the gully
        participant = await ensure_user_in_gully(user_id, gully_id)
        if not participant:
            return False

        # Set this gully as active
        result = await api_client.set_active_gully(user_id, gully_id)
        if result:
            logger.info(f"Set gully {gully_id} as active for user {user_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error setting active gully for user {user_id}: {e}")
        return False
