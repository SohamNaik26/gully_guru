"""
User service for the GullyGuru API.
This module provides methods for interacting with user-related database operations.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func

from src.api.services.base import BaseService
from src.db.models.models import User, ParticipantPlayer, GullyParticipant

logger = logging.getLogger(__name__)


class UserService(BaseService):
    """Service for user-related operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize the user service.

        Args:
            db: Database session
        """
        super().__init__(None, None)
        self.db = db

    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user.

        Args:
            user_data: Dictionary containing user data

        Returns:
            Dictionary with created user data
        """
        # Map 'name' to 'full_name' if it exists
        if "name" in user_data and "full_name" not in user_data:
            user_data["full_name"] = user_data.pop("name")

        # Check if user with telegram_id already exists
        stmt = select(User).where(User.telegram_id == user_data["telegram_id"])
        result = await self.db.execute(stmt)
        existing_user = result.scalars().first()

        if existing_user:
            # Return existing user instead of raising an error
            logger.info(
                f"User with telegram_id {user_data['telegram_id']} already exists, returning existing user"
            )
            return await self.get_user(existing_user.id)

        # Create new user
        user = User(**user_data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        # Convert SQLModel to dict and add gully_ids
        user_dict = {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "full_name": user.full_name,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }

        return user_dict

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a user by ID.

        Args:
            user_id: ID of the user to retrieve

        Returns:
            Dictionary with user data or None if not found
        """
        user = await self.db.get(User, user_id)
        if not user:
            return None

        # Convert SQLModel to dict and add gully_ids
        user_dict = {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "full_name": user.full_name,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }

        return user_dict

    async def get_user_by_telegram_id(
        self, telegram_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get a user by Telegram ID.

        Args:
            telegram_id: Telegram ID of the user to retrieve

        Returns:
            Dictionary with user data or None if not found
        """
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.db.execute(stmt)
        user = result.scalars().first()

        if not user:
            return None

        # Convert SQLModel to dict and add gully_ids
        user_dict = {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "full_name": user.full_name,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }

        return user_dict

    async def get_users_by_telegram_id(
        self, telegram_id: int, limit: int = None, offset: int = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get users filtered by Telegram ID.

        This method is specifically optimized for bot integration, providing a direct
        way to filter users by their Telegram ID.

        Args:
            telegram_id: Telegram ID to filter by
            limit: DEPRECATED - Kept for backward compatibility
            offset: DEPRECATED - Kept for backward compatibility

        Returns:
            Tuple of (list of user dictionaries, total count) for backward compatibility
        """
        # Build query with telegram_id filter
        query = select(User).where(User.telegram_id == telegram_id)

        # Execute query
        result = await self.db.execute(query)
        users = result.scalars().all()

        # Convert SQLModels to dicts
        user_dicts = []
        for user in users:
            user_dict = {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "full_name": user.full_name,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
            }
            user_dicts.append(user_dict)

        # Return tuple of (user_dicts, total) for backward compatibility
        return user_dicts, len(user_dicts)

    async def get_users(
        self, limit: int = None, offset: int = None, filters: Dict[str, Any] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get a list of users with optional filtering.

        Args:
            limit: DEPRECATED - Kept for backward compatibility
            offset: DEPRECATED - Kept for backward compatibility
            filters: Dictionary of field names and values to filter by

        Returns:
            Tuple of (list of user dictionaries, total count) for backward compatibility
        """
        # Build query with filters
        query = select(User)
        if filters:
            for field, value in filters.items():
                if hasattr(User, field) and value is not None:
                    query = query.where(getattr(User, field) == value)

        # Execute query
        result = await self.db.execute(query)
        users = result.scalars().all()

        # Convert SQLModels to dicts
        user_dicts = []
        for user in users:
            user_dict = {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "full_name": user.full_name,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
            }
            user_dicts.append(user_dict)

        # Return tuple of (user_dicts, total) for backward compatibility
        return user_dicts, len(user_dicts)

    async def update_user(
        self, user_id: int, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update a user.

        Args:
            user_id: ID of the user to update
            update_data: Dictionary containing fields to update

        Returns:
            Dictionary with updated user data or None if not found
        """
        user = await self.db.get(User, user_id)
        if not user:
            return None

        # Map 'name' to 'full_name' if it exists
        if "name" in update_data and "full_name" not in update_data:
            update_data["full_name"] = update_data.pop("name")

        # Update user attributes
        for key, value in update_data.items():
            if hasattr(user, key):
                setattr(user, key, value)

        await self.db.commit()
        await self.db.refresh(user)

        # Convert SQLModel to dict and add gully_ids
        user_dict = {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "full_name": user.full_name,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }

        return user_dict

    async def delete_user(self, user_id: int) -> bool:
        """
        Delete a user.

        Args:
            user_id: ID of the user to delete

        Returns:
            True if user was deleted, False if not found
        """
        user = await self.db.get(User, user_id)
        if not user:
            return False

        await self.db.delete(user)
        await self.db.commit()

        return True

    async def get_participant_players(
        self, user_id: int, gully_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get players owned by a user.

        Args:
            user_id: The ID of the user
            gully_id: Optional gully ID to filter by

        Returns:
            List of participant player dictionaries
        """
        # First get the gully_participant_id
        query = select(GullyParticipant.id).where(GullyParticipant.user_id == user_id)
        if gully_id:
            query = query.where(GullyParticipant.gully_id == gully_id)

        result = await self.db.execute(query)
        participant_ids = result.scalars().all()

        if not participant_ids:
            return []

        # Now get the participant players
        query = select(ParticipantPlayer).where(
            ParticipantPlayer.gully_participant_id.in_(participant_ids)
        )

        result = await self.db.execute(query)
        participant_players = result.scalars().all()

        # Convert to dictionaries
        player_dicts = []
        for player in participant_players:
            player_dict = {
                "id": player.id,
                "gully_participant_id": player.gully_participant_id,
                "player_id": player.player_id,
                "status": player.status,
                "created_at": player.created_at,
                "updated_at": player.updated_at,
            }
            player_dicts.append(player_dict)

        return player_dicts

    async def create_participant_player(
        self, participant_player_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new participant player.

        Args:
            participant_player_data: Participant player data to create

        Returns:
            Dictionary with created participant player data
        """
        participant_player = ParticipantPlayer(**participant_player_data)
        self.db.add(participant_player)
        await self.db.commit()
        await self.db.refresh(participant_player)

        # Convert to dictionary
        player_dict = {
            "id": participant_player.id,
            "gully_participant_id": participant_player.gully_participant_id,
            "player_id": participant_player.player_id,
            "status": participant_player.status,
            "created_at": participant_player.created_at,
            "updated_at": participant_player.updated_at,
        }

        return player_dict

    async def get_users_simple(self) -> List[Dict[str, Any]]:
        """
        Get a list of all users without pagination.

        Returns:
            List of user dictionaries
        """
        # Build simple query
        query = select(User)

        # Execute query
        result = await self.db.execute(query)
        users = result.scalars().all()

        # Convert SQLModels to dicts
        user_dicts = []
        for user in users:
            user_dict = {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "full_name": user.full_name,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
            }
            user_dicts.append(user_dict)

        return user_dicts

    async def get_users_by_telegram_id_simple(
        self, telegram_id: int
    ) -> List[Dict[str, Any]]:
        """
        Get users filtered by Telegram ID without pagination.

        Args:
            telegram_id: Telegram ID to filter by

        Returns:
            List of user dictionaries
        """
        # Build query with telegram_id filter
        query = select(User).where(User.telegram_id == telegram_id)

        # Execute query
        result = await self.db.execute(query)
        users = result.scalars().all()

        # Convert SQLModels to dicts
        user_dicts = []
        for user in users:
            user_dict = {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "full_name": user.full_name,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
            }
            user_dicts.append(user_dict)

        return user_dicts
