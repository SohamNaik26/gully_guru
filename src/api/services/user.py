"""
User service for the GullyGuru API.
This module provides client methods for interacting with user-related API endpoints and database operations.
"""

import logging
from typing import Dict, Any, Optional, List
import httpx

from sqlmodel import select

from src.api.services.base import BaseService, BaseServiceClient
from src.db.models.models import User, UserPlayer

logger = logging.getLogger(__name__)


class UserService(BaseService):
    """Client for interacting with user-related API endpoints."""

    def __init__(self, base_url: str, client: httpx.AsyncClient = None):
        """Initialize the user service client.

        Args:
            base_url: The base URL for the API
            client: An optional httpx AsyncClient instance
        """
        super().__init__(base_url, client)
        self.endpoint = f"{self.base_url}/users"

    async def get_user(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Get a user by Telegram ID.

        Args:
            telegram_id: The Telegram ID of the user

        Returns:
            User data or None if not found
        """
        response = await self._make_request(
            "GET", f"{self.endpoint}/telegram/{telegram_id}"
        )
        if "error" in response:
            logger.error(f"Error getting user: {response['error']}")
            return None
        return response

    async def create_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new user.

        Args:
            user_data: User data to create

        Returns:
            Created user data or None if creation failed
        """
        # Map 'name' to 'full_name' if it exists
        if "name" in user_data and "full_name" not in user_data:
            user_data["full_name"] = user_data.pop("name")

        response = await self._make_request("POST", self.endpoint, json=user_data)
        if "error" in response:
            logger.error(f"Error creating user: {response['error']}")
            return None
        return response

    async def update_user(
        self, telegram_id: int, user_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update a user.

        Args:
            telegram_id: The Telegram ID of the user to update
            user_data: User data to update

        Returns:
            Updated user data or None if update failed
        """
        # Map 'name' to 'full_name' if it exists
        if "name" in user_data and "full_name" not in user_data:
            user_data["full_name"] = user_data.pop("name")

        response = await self._make_request(
            "PUT", f"{self.endpoint}/telegram/{telegram_id}", json=user_data
        )
        if "error" in response:
            logger.error(f"Error updating user: {response['error']}")
            return None
        return response

    async def delete_user(self, telegram_id: int) -> bool:
        """Delete a user.

        Args:
            telegram_id: The Telegram ID of the user to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        response = await self._make_request(
            "DELETE", f"{self.endpoint}/telegram/{telegram_id}"
        )
        if "error" in response:
            logger.error(f"Error deleting user: {response['error']}")
            return False
        return True

    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get a user by ID.

        Args:
            user_id: The ID of the user

        Returns:
            User data or None if not found
        """
        response = await self._make_request("GET", f"{self.endpoint}/{user_id}")
        if "error" in response:
            logger.error(f"Error getting user: {response['error']}")
            return None
        return response

    async def get_user_players(
        self, user_id: int, gully_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get players owned by a user.

        Args:
            user_id: The ID of the user
            gully_id: Optional gully ID to filter by

        Returns:
            List of players owned by the user
        """
        params = {}
        if gully_id:
            params["gully_id"] = gully_id

        response = await self._make_request(
            "GET", f"{self.endpoint}/{user_id}/players", params=params
        )
        if "error" in response:
            logger.error(f"Error getting user players: {response['error']}")
            return []
        return response

    async def create_user_player(
        self, user_player_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Create a new user player.

        Args:
            user_player_data: User player data to create

        Returns:
            Created user player data or None if creation failed
        """
        user_id = user_player_data.get("user_id")
        if not user_id:
            logger.error("User ID is required to create a user player")
            return None

        response = await self._make_request(
            "POST", f"{self.endpoint}/{user_id}/players", json=user_player_data
        )
        if "error" in response:
            logger.error(f"Error creating user player: {response['error']}")
            return None
        return response


class UserServiceClient(BaseServiceClient):
    """Client for interacting with user-related database operations."""

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get a user by Telegram ID.

        Args:
            telegram_id: The Telegram ID of the user

        Returns:
            User object or None if not found
        """
        query = select(User).where(User.telegram_id == telegram_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_user(self, user_id: int) -> Optional[User]:
        """Get a user by ID.

        Args:
            user_id: The ID of the user

        Returns:
            User object or None if not found
        """
        return await self.db.get(User, user_id)

    async def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user.

        Args:
            user_data: User data to create

        Returns:
            Created user object
        """
        # Map 'name' to 'full_name' if it exists
        if "name" in user_data and "full_name" not in user_data:
            user_data["full_name"] = user_data.pop("name")

        user = User(**user_data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_user(
        self, user_id: int, user_data: Dict[str, Any]
    ) -> Optional[User]:
        """Update a user.

        Args:
            user_id: The ID of the user to update
            user_data: User data to update

        Returns:
            Updated user object or None if not found
        """
        user = await self.db.get(User, user_id)
        if not user:
            return None

        # Map 'name' to 'full_name' if it exists
        if "name" in user_data and "full_name" not in user_data:
            user_data["full_name"] = user_data.pop("name")

        for key, value in user_data.items():
            setattr(user, key, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: int) -> bool:
        """Delete a user.

        Args:
            user_id: The ID of the user to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        user = await self.db.get(User, user_id)
        if not user:
            return False

        await self.db.delete(user)
        await self.db.commit()
        return True

    async def get_user_players(
        self, user_id: int, gully_id: Optional[int] = None
    ) -> List[UserPlayer]:
        """Get players owned by a user.

        Args:
            user_id: The ID of the user
            gully_id: Optional gully ID to filter by

        Returns:
            List of user player objects
        """
        query = select(UserPlayer).where(UserPlayer.user_id == user_id)
        if gully_id:
            query = query.where(UserPlayer.gully_id == gully_id)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_user_player(self, user_player_data: Dict[str, Any]) -> UserPlayer:
        """Create a new user player.

        Args:
            user_player_data: User player data to create

        Returns:
            Created user player object
        """
        user_player = UserPlayer(**user_player_data)
        self.db.add(user_player)
        await self.db.commit()
        await self.db.refresh(user_player)
        return user_player
