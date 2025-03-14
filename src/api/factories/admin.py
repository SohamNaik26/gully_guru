"""Factory classes for creating Admin-related response objects."""

from typing import Dict, Any, List
from src.api.factories.base import ResponseFactory
from src.api.schemas import AdminRoleResponse, AdminUserResponse
from src.db.models import GullyParticipant


class AdminFactory(ResponseFactory[GullyParticipant, AdminRoleResponse]):
    """Factory for creating Admin role response objects."""

    response_model = AdminRoleResponse

    @classmethod
    def create_response_list(
        cls, admin_users: List[Dict[str, Any]]
    ) -> List[AdminUserResponse]:
        """
        Create a list of AdminUserResponse objects from admin user data.

        Args:
            admin_users: List of dictionaries containing admin user data

        Returns:
            List of AdminUserResponse objects
        """
        result = []
        for admin_user in admin_users:
            # Determine permissions based on role
            permissions = []
            if admin_user.get("role") in ["admin", "owner"]:
                permissions = [
                    "manage_participants",
                    "manage_players",
                    "manage_settings",
                    "view_all_data",
                ]
            else:
                permissions = ["view_public_data"]

            # Create AdminUserResponse with permissions
            response = AdminUserResponse(
                id=admin_user["id"],
                telegram_id=admin_user["telegram_id"],
                username=admin_user["username"],
                full_name=admin_user["full_name"],
                created_at=admin_user["created_at"],
                updated_at=admin_user["updated_at"],
                role=admin_user["role"],
                permissions=permissions,
            )
            result.append(response)

        return result

    @classmethod
    def create_role_response(cls, admin_role: Dict[str, Any]) -> AdminRoleResponse:
        """
        Create an AdminRoleResponse from admin role data.

        Args:
            admin_role: Dictionary containing admin role data

        Returns:
            AdminRoleResponse object
        """
        return AdminRoleResponse(
            id=admin_role["id"],
            user_id=admin_role["user_id"],
            gully_id=admin_role["gully_id"],
            role=admin_role["role"],
            created_at=admin_role["created_at"],
            updated_at=admin_role["updated_at"],
        )
