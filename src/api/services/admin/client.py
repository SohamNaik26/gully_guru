import logging
from typing import Dict, Any, List, Optional
import httpx
from sqlmodel import select

from sqlalchemy.ext.asyncio import AsyncSession
from src.api.schemas.admin import AdminUserResponse, AdminRoleResponse
from src.db.models import User, GullyParticipant
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

    async def assign_admin_role(
        self, gully_id: int, user_id: int, role: str
    ) -> Optional[Dict[str, Any]]:
        """Assign admin role to a user.

        Args:
            gully_id: The ID of the gully
            user_id: The ID of the user
            role: The role to assign ("admin" or "owner")

        Returns:
            Admin role data or None if assignment failed
        """
        role_data = {"user_id": user_id, "gully_id": gully_id, "role": role}
        response = await self._make_request(
            "POST", f"{self.endpoint}/gully/{gully_id}/admins/{user_id}", json=role_data
        )
        if "error" in response:
            logger.error(f"Error assigning admin role: {response['error']}")
            return None
        return response


class AdminServiceClient:
    """Client for interacting with admin-related database operations."""

    def __init__(self, db: AsyncSession):
        """Initialize the admin service client.

        Args:
            db: The database session
        """
        self.db = db

    async def get_gully_admins(self, gully_id: int) -> List[AdminUserResponse]:
        """Get all admins for a gully.

        Args:
            gully_id: The ID of the gully

        Returns:
            List of admin users
        """
        # Query for all admin participants in the gully
        query = select(GullyParticipant).where(
            (GullyParticipant.gully_id == gully_id)
            & (GullyParticipant.role.in_(["admin", "owner"]))
        )

        result = await self.db.execute(query)
        admin_participants = result.scalars().all()

        # Get the user details for each admin
        admin_users = []
        for participant in admin_participants:
            user = await self.db.get(User, participant.user_id)
            if user:
                admin_user = AdminUserResponse(
                    id=user.id,
                    telegram_id=user.telegram_id,
                    username=user.username,
                    full_name=user.full_name,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                    role=participant.role,
                    permissions=[],  # Add permissions logic here if needed
                )
                admin_users.append(admin_user)

        return admin_users

    async def is_user_admin(self, user_id: int, gully_id: int) -> bool:
        """Check if a user is an admin of a gully.

        Args:
            user_id: The ID of the user
            gully_id: The ID of the gully

        Returns:
            True if the user is an admin, False otherwise
        """
        query = select(GullyParticipant).where(
            (GullyParticipant.gully_id == gully_id)
            & (GullyParticipant.user_id == user_id)
            & (GullyParticipant.role.in_(["admin", "owner"]))
        )
        result = await self.db.execute(query)
        admin_participant = result.scalars().first()
        return admin_participant is not None

    async def assign_admin_role(self, user_id: int, gully_id: int) -> AdminRoleResponse:
        """Assign admin role to a user.

        Args:
            user_id: The ID of the user
            gully_id: The ID of the gully

        Returns:
            Admin role data
        """
        # Check if user is already a participant in the gully
        query = select(GullyParticipant).where(
            (GullyParticipant.gully_id == gully_id)
            & (GullyParticipant.user_id == user_id)
        )
        result = await self.db.execute(query)
        participant = result.scalars().first()

        if participant:
            # Update existing participant to admin role regardless of current role
            participant.role = "admin"
            await self.db.commit()
            await self.db.refresh(participant)

            # Create response
            response = AdminRoleResponse(
                id=participant.id,
                user_id=participant.user_id,
                gully_id=participant.gully_id,
                role=participant.role,
                created_at=participant.created_at,
                updated_at=participant.updated_at,
            )
        else:
            # Get user for team name
            user = await self.db.get(User, user_id)
            if not user:
                raise ValueError(f"User with ID {user_id} not found")

            # Create new participant with admin role
            new_participant = GullyParticipant(
                user_id=user_id,
                gully_id=gully_id,
                role="admin",
                team_name=f"{user.username}'s Team",  # Default team name
            )
            self.db.add(new_participant)
            await self.db.commit()
            await self.db.refresh(new_participant)

            # Create response
            response = AdminRoleResponse(
                id=new_participant.id,
                user_id=new_participant.user_id,
                gully_id=new_participant.gully_id,
                role=new_participant.role,
                created_at=new_participant.created_at,
                updated_at=new_participant.updated_at,
            )

        return response
