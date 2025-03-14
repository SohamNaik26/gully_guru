"""
Admin service for the GullyGuru API.
This module provides methods for interacting with admin-related database operations.
"""

import logging
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.api.services.base import BaseService
from src.db.models import User, GullyParticipant

logger = logging.getLogger(__name__)


class AdminService(BaseService):
    """Service for admin-related operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize the admin service.

        Args:
            db: Database session
        """
        super().__init__(None, None)
        self.db = db

    async def get_gully_admins(self, gully_id: int) -> List[Dict[str, Any]]:
        """
        Get all admins for a gully.

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
                admin_user = {
                    "id": user.id,
                    "telegram_id": user.telegram_id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at,
                    "role": participant.role,
                }
                admin_users.append(admin_user)

        return admin_users

    async def is_gully_admin(self, user_id: int, gully_id: int) -> bool:
        """
        Check if a user is an admin of a gully.

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

    async def assign_admin_role(self, user_id: int, gully_id: int) -> Dict[str, Any]:
        """
        Assign admin role to a user.

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

            # Create response dictionary
            response = {
                "id": participant.id,
                "user_id": participant.user_id,
                "gully_id": participant.gully_id,
                "role": participant.role,
                "created_at": participant.created_at,
                "updated_at": participant.updated_at,
            }
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

            # Create response dictionary
            response = {
                "id": new_participant.id,
                "user_id": new_participant.user_id,
                "gully_id": new_participant.gully_id,
                "role": new_participant.role,
                "created_at": new_participant.created_at,
                "updated_at": new_participant.updated_at,
            }

        return response

    async def remove_admin_role(self, user_id: int, gully_id: int) -> bool:
        """
        Remove admin role from a user.

        Args:
            user_id: The ID of the user
            gully_id: The ID of the gully

        Returns:
            True if the role was removed, False otherwise
        """
        # Check if user is an admin in the gully
        query = select(GullyParticipant).where(
            (GullyParticipant.gully_id == gully_id)
            & (GullyParticipant.user_id == user_id)
            & (GullyParticipant.role.in_(["admin", "owner"]))
        )
        result = await self.db.execute(query)
        admin_participant = result.scalars().first()

        if not admin_participant:
            return False

        # Downgrade role to member
        admin_participant.role = "member"
        await self.db.commit()
        return True

    async def get_user_permissions(self, user_id: int, gully_id: int) -> Dict[str, Any]:
        """
        Get a user's permissions in a gully.

        Args:
            user_id: The ID of the user
            gully_id: The ID of the gully

        Returns:
            Dictionary of permissions
        """
        # Check if user is a participant in the gully
        query = select(GullyParticipant).where(
            (GullyParticipant.gully_id == gully_id)
            & (GullyParticipant.user_id == user_id)
        )
        result = await self.db.execute(query)
        participant = result.scalars().first()

        if not participant:
            return {
                "is_participant": False,
                "is_admin": False,
                "role": None,
                "permissions": [],
            }

        # Determine permissions based on role
        is_admin = participant.role in ["admin", "owner"]
        permissions = []

        if is_admin:
            permissions = [
                "manage_participants",
                "manage_players",
                "manage_settings",
                "view_all_data",
            ]
        else:
            permissions = ["view_public_data"]

        return {
            "is_participant": True,
            "is_admin": is_admin,
            "role": participant.role,
            "permissions": permissions,
        }
