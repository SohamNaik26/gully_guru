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

    async def assign_admin_role(self, user_id: int, gully_id: int) -> Dict[str, Any]:
        """Assign admin role to a user.

        Args:
            user_id: The ID of the user
            gully_id: The ID of the gully

        Returns:
            Assignment result data
        """
        response = await self._make_request(
            "POST", f"{self.endpoint}/gully/{gully_id}/admins/{user_id}"
        )
        if "error" in response:
            logger.error(f"Error assigning admin role: {response['error']}")
            return {"success": False, "error": response["error"]}
        return response

    async def remove_admin_role(self, user_id: int, gully_id: int) -> Dict[str, Any]:
        """Remove admin role from a user.

        Args:
            user_id: The ID of the user
            gully_id: The ID of the gully

        Returns:
            Removal result data
        """
        response = await self._make_request(
            "DELETE", f"{self.endpoint}/gully/{gully_id}/admins/{user_id}"
        )
        if "error" in response:
            logger.error(f"Error removing admin role: {response['error']}")
            return {"success": False, "error": response["error"]}
        return response

    async def assign_admin_permission(
        self, user_id: int, gully_id: int, permission_type: str
    ) -> Dict[str, Any]:
        """Assign a specific permission to an admin.

        Args:
            user_id: The ID of the user
            gully_id: The ID of the gully
            permission_type: The type of permission to assign

        Returns:
            Assignment result data
        """
        response = await self._make_request(
            "POST",
            f"{self.endpoint}/permissions/{gully_id}/{user_id}/{permission_type}",
        )
        if "error" in response:
            logger.error(f"Error assigning admin permission: {response['error']}")
            return {"success": False, "error": response["error"]}
        return response

    async def remove_admin_permission(
        self, user_id: int, gully_id: int, permission_type: str
    ) -> Dict[str, Any]:
        """Remove a specific permission from an admin.

        Args:
            user_id: The ID of the user
            gully_id: The ID of the gully
            permission_type: The type of permission to remove

        Returns:
            Removal result data
        """
        response = await self._make_request(
            "DELETE",
            f"{self.endpoint}/permissions/{gully_id}/{user_id}/{permission_type}",
        )
        if "error" in response:
            logger.error(f"Error removing admin permission: {response['error']}")
            return {"success": False, "error": response["error"]}
        return response

    async def nominate_admin(self, nominee_id: int, gully_id: int) -> Dict[str, Any]:
        """Nominate a user as admin.

        Args:
            nominee_id: The ID of the user to nominate
            gully_id: The ID of the gully

        Returns:
            Nomination result data
        """
        response = await self._make_request(
            "POST", f"{self.endpoint}/gully/{gully_id}/nominate/{nominee_id}"
        )
        if "error" in response:
            logger.error(f"Error nominating admin: {response['error']}")
            return {"success": False, "error": response["error"]}
        return response

    async def generate_invite_link(
        self, gully_id: int, expiration_hours: int = 24
    ) -> Dict[str, Any]:
        """Generate an invite link for a gully.

        Args:
            gully_id: The ID of the gully
            expiration_hours: The number of hours the link should be valid

        Returns:
            Invite link data
        """
        response = await self._make_request(
            "POST",
            f"{self.endpoint}/gully/{gully_id}/invite",
            params={"expiration_hours": expiration_hours},
        )
        if "error" in response:
            logger.error(f"Error generating invite link: {response['error']}")
            return {"success": False, "error": response["error"]}
        return response
