"""
Service layer for user operations.
Provides a clean interface for user-related functionality.
"""

import logging
from typing import Dict, Any, Optional
from telegram import User as TelegramUser

from src.api.api_client_instance import api_client

logger = logging.getLogger(__name__)


class UserService:
    """Service for user-related operations."""

    @staticmethod
    async def ensure_user_exists(
        telegram_user: TelegramUser, from_gully_id: int = None
    ) -> Optional[Dict[str, Any]]:
        """
        Ensures a user exists in the database. Creates the user if they don't exist.

        Args:
            telegram_user: The Telegram user object
            from_gully_id: Optional gully ID from where the user was initiated

        Returns:
            Optional[Dict]: The user data from the database or None if failed
        """
        try:
            # Check if user exists in database
            db_user = await api_client.users.get_user(telegram_user.id)

            if not db_user:
                # User doesn't exist, create them
                logger.info(f"Creating new user {telegram_user.id} in database")

                # Prepare user data
                name = telegram_user.full_name
                if not name:
                    name = telegram_user.first_name or ""
                    if telegram_user.last_name:
                        name += f" {telegram_user.last_name}"

                user_data = {
                    "telegram_id": telegram_user.id,
                    "full_name": name,
                    "username": telegram_user.username or f"user_{telegram_user.id}",
                }

                # Create the user
                db_user = await api_client.users.create_user(user_data)
                if not db_user:
                    logger.error(
                        f"Failed to create user {telegram_user.id} in database"
                    )
                    return None

                logger.info(f"Created new user {telegram_user.id} in database")

                # If gully ID was provided, ensure user is in that gully
                if from_gully_id and db_user:
                    from src.bot.services.gully_service import gully_service

                    await gully_service.add_user_to_gully(db_user["id"], from_gully_id)

            return db_user
        except Exception as e:
            logger.error(f"Error ensuring user exists: {str(e)}")
            return None

    @staticmethod
    async def get_user(telegram_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a user by Telegram ID.

        Args:
            telegram_id: The Telegram user ID

        Returns:
            Optional[Dict]: The user data or None if not found
        """
        try:
            return await api_client.users.get_user(telegram_id)
        except Exception as e:
            logger.error(f"Error getting user {telegram_id}: {str(e)}")
            return None

    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a user by database ID.

        Args:
            user_id: The database user ID

        Returns:
            Optional[Dict]: The user data or None if not found
        """
        try:
            return await api_client.users.get_user_by_id(user_id)
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {str(e)}")
            return None

    @staticmethod
    async def update_user(
        telegram_id: int, user_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update a user's data.

        Args:
            telegram_id: The Telegram user ID
            user_data: The data to update

        Returns:
            Optional[Dict]: The updated user data or None if failed
        """
        try:
            return await api_client.users.update_user(telegram_id, user_data)
        except Exception as e:
            logger.error(f"Error updating user {telegram_id}: {str(e)}")
            return None

    @staticmethod
    async def get_active_gully(user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the user's active gully.

        Args:
            user_id: The user's database ID

        Returns:
            Optional[Dict]: The active gully data or None if not found
        """
        try:
            # Get all gully participations for the user
            participations = await api_client.gullies.get_user_gully_participations(
                user_id
            )

            # Find the active participation
            active_participation = next(
                (p for p in participations if p.get("is_active", False)), None
            )

            if active_participation:
                gully_id = active_participation.get("gully_id")
                if gully_id:
                    from src.bot.services.gully_service import gully_service

                    return await gully_service.get_gully(gully_id)

            return None
        except Exception as e:
            logger.error(f"Error getting active gully for user {user_id}: {str(e)}")
            return None

    @staticmethod
    async def set_active_gully(user_id: int, gully_id: int) -> bool:
        """
        Set a gully as active for a user.

        Args:
            user_id: The user's database ID
            gully_id: The gully ID

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get the user's participation in the gully
            participation = await api_client.gullies.get_user_gully_participation(
                user_id, gully_id
            )

            if not participation:
                logger.error(f"User {user_id} is not a participant in gully {gully_id}")
                return False

            # Set this gully as active
            result = await api_client.gullies.set_active_gully(participation["id"])

            if result and result.get("success", False):
                logger.info(f"Set gully {gully_id} as active for user {user_id}")
                return True

            logger.error(f"Failed to set gully {gully_id} as active for user {user_id}")
            return False
        except Exception as e:
            logger.error(f"Error setting active gully: {str(e)}")
            return False


# Create a singleton instance
user_service = UserService()
