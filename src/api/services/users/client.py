import logging
from typing import Dict, Any, Optional, List
import httpx

from src.api.services.base import BaseService

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
        """Update an existing user.

        Args:
            telegram_id: The Telegram ID of the user to update
            user_data: User data to update

        Returns:
            Updated user data or None if update failed
        """
        response = await self._make_request(
            "PUT", f"{self.endpoint}/telegram/{telegram_id}", json=user_data
        )
        if "error" in response:
            logger.error(f"Error updating user: {response['error']}")
            return None
        return response

    async def delete_user(self, telegram_id: int) -> bool:
        """Delete a user by Telegram ID.

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
        """Get a user by database ID.

        Args:
            user_id: The database ID of the user

        Returns:
            User data or None if not found
        """
        response = await self._make_request("GET", f"{self.endpoint}/{user_id}")
        if "error" in response:
            logger.error(f"Error getting user by ID: {response['error']}")
            return None
        return response

    async def get_user_players(
        self, user_id: int, gully_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all players owned by a user, optionally filtered by gully.

        Args:
            user_id: The database ID of the user
            gully_id: Optional gully ID to filter by

        Returns:
            List of user player data
        """
        url = f"{self.endpoint}/players/{user_id}"
        if gully_id:
            url += f"?gully_id={gully_id}"

        response = await self._make_request("GET", url)
        if "error" in response:
            logger.error(f"Error getting user players: {response['error']}")
            return []
        return response

    async def create_user_player(
        self, user_player_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Create a new user player relationship.

        Args:
            user_player_data: User player data to create

        Returns:
            Created user player data or None if creation failed
        """
        response = await self._make_request(
            "POST", f"{self.endpoint}/players", json=user_player_data
        )
        if "error" in response:
            logger.error(f"Error creating user player: {response['error']}")
            return None
        return response
