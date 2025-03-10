import logging
from typing import Dict, Any, List
import httpx

from src.api.services.base import BaseService

logger = logging.getLogger(__name__)


class AdminService(BaseService):
    """Client for interacting with admin-related API endpoints."""

    def __init__(self, base_url: str, client: httpx.AsyncClient = None):
        """Initialize the admin service client.

        Args:
            base_url: The base URL for the API
            client: An optional httpx AsyncClient instance
        """
        super().__init__(base_url, client)
        self.endpoint = f"{self.base_url}/admin"

    async def get_user_permissions(
        self, user_id: int, gully_id: int
    ) -> List[Dict[str, Any]]:
        """Get a user's permissions in a gully.

        Args:
            user_id: The ID of the user
            gully_id: The ID of the gully

        Returns:
            List of permissions
        """
        response = await self._make_request(
            "GET", f"{self.endpoint}/permissions/{gully_id}/{user_id}"
        )
        if "error" in response:
            logger.error(f"Error getting user permissions: {response['error']}")
            return []
        return response

    async def get_gully_admins(self, gully_id: int) -> List[Dict[str, Any]]:
        """Get all admins of a gully.

        Args:
            gully_id: The ID of the gully

        Returns:
            List of admins
        """
        response = await self._make_request(
            "GET", f"{self.endpoint}/gully/{gully_id}/admins"
        )
        if "error" in response:
            logger.error(f"Error getting gully admins: {response['error']}")
            return []
        return response
