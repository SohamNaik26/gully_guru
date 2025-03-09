"""
Service layer for admin operations.
Provides a clean interface for admin-related functionality.
"""

import logging
from typing import Dict, Any, List

from src.api.api_client_instance import api_client

logger = logging.getLogger(__name__)


class AdminService:
    """Service for admin-related operations."""

    @staticmethod
    async def check_admin_status(user_id: int, gully_id: int) -> bool:
        """
        Check if a user is an admin in a specific gully.

        Args:
            user_id: The user's database ID
            gully_id: The gully ID

        Returns:
            bool: True if the user is an admin, False otherwise
        """
        try:
            # Get all admins for the gully
            admins = await api_client.admin.get_gully_admins(gully_id)

            # Check if the user is in the admin list
            return any(admin["user_id"] == user_id for admin in admins)
        except Exception as e:
            logger.error(f"Error checking admin status: {str(e)}")
            return False

    @staticmethod
    async def assign_admin_role(user_id: int, gully_id: int) -> Dict[str, Any]:
        """
        Assign admin role to a user in a gully.

        Args:
            user_id: The user's database ID
            gully_id: The gully ID

        Returns:
            Dict: Result of the operation with success status
        """
        try:
            # Call the API endpoint to assign admin role
            response = await api_client.admin.assign_admin_role(user_id, gully_id)

            if response.get("success", False):
                logger.info(f"User {user_id} assigned as admin in gully {gully_id}")
            else:
                logger.error(
                    f"Failed to assign admin role: {response.get('error', 'Unknown error')}"
                )

            return response
        except Exception as e:
            logger.error(f"Error assigning admin role: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    async def get_gully_admins(gully_id: int) -> List[Dict[str, Any]]:
        """
        Get all admins of a gully.

        Args:
            gully_id: The gully ID

        Returns:
            List[Dict]: List of admin users
        """
        try:
            # Call the API endpoint to get gully admins
            return await api_client.admin.get_gully_admins(gully_id)
        except Exception as e:
            logger.error(f"Error getting gully admins: {str(e)}")
            return []

    @staticmethod
    async def remove_admin_role(user_id: int, gully_id: int) -> Dict[str, Any]:
        """
        Remove admin role from a user in a gully.

        Args:
            user_id: The user's database ID
            gully_id: The gully ID

        Returns:
            Dict: Result of the operation with success status
        """
        try:
            # Call the API endpoint to remove admin role
            response = await api_client.admin.remove_admin_role(user_id, gully_id)

            if response.get("success", False):
                logger.info(
                    f"Admin role removed from user {user_id} in gully {gully_id}"
                )
            else:
                logger.error(
                    f"Failed to remove admin role: {response.get('error', 'Unknown error')}"
                )

            return response
        except Exception as e:
            logger.error(f"Error removing admin role: {str(e)}")
            return {"success": False, "error": str(e)}


# Create a singleton instance
admin_service = AdminService()
