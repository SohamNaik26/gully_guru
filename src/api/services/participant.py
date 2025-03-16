"""
Participant service for the GullyGuru API.
This module provides methods for interacting with participant-related database operations.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from sqlalchemy import func

from src.api.services.base import BaseService
from src.db.models.models import GullyParticipant, User

logger = logging.getLogger(__name__)


class ParticipantService(BaseService):
    """Service for participant-related operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize the participant service.

        Args:
            db: Database session
        """
        super().__init__(None, None)
        self.db = db

    async def get_participants(
        self,
        gully_id: Optional[int] = None,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get participants with optional filtering.

        Args:
            gully_id: Optional filter by gully ID
            user_id: Optional filter by user ID
            skip: Number of participants to skip
            limit: Maximum number of participants to return

        Returns:
            Tuple of (list of participants, total count)
        """
        stmt = select(GullyParticipant)

        if gully_id:
            stmt = stmt.where(GullyParticipant.gully_id == gully_id)
        if user_id:
            stmt = stmt.where(GullyParticipant.user_id == user_id)

        # Get total count
        count_query = select(func.count()).select_from(stmt.subquery())
        total = await self.db.scalar(count_query) or 0

        # Apply pagination
        stmt = stmt.offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        participants = result.scalars().all()

        # Convert to list of dictionaries
        participant_dicts = []
        for participant in participants:
            participant_dict = {
                "id": participant.id,
                "gully_id": participant.gully_id,
                "user_id": participant.user_id,
                "role": participant.role,
                "team_name": participant.team_name,
                "created_at": participant.created_at,
                "updated_at": participant.updated_at,
            }
            participant_dicts.append(participant_dict)

        return participant_dicts, total

    async def get_participant(
        self, gully_id: int, user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific participant by gully ID and user ID.

        Args:
            gully_id: The ID of the gully
            user_id: The ID of the user

        Returns:
            Participant data or None if not found
        """
        stmt = select(GullyParticipant).where(
            (GullyParticipant.gully_id == gully_id)
            & (GullyParticipant.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        participant = result.scalars().first()

        if not participant:
            return None

        return {
            "id": participant.id,
            "user_id": participant.user_id,
            "gully_id": participant.gully_id,
            "role": participant.role,
            "team_name": participant.team_name,
            "created_at": participant.created_at,
            "updated_at": participant.updated_at,
        }

    async def get_participant_by_id(
        self, participant_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get a participant by ID.

        Args:
            participant_id: The ID of the participant

        Returns:
            Participant data or None if not found
        """
        participant = await self.db.get(GullyParticipant, participant_id)
        if not participant:
            return None

        return {
            "id": participant.id,
            "user_id": participant.user_id,
            "gully_id": participant.gully_id,
            "role": participant.role,
            "team_name": participant.team_name,
            "created_at": participant.created_at,
            "updated_at": participant.updated_at,
        }

    async def add_participant(
        self,
        gully_id: int,
        user_id: int,
        role: str = "member",
        team_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Add a participant to a gully.

        Args:
            gully_id: The ID of the gully
            user_id: The ID of the user to add
            role: The role of the user in the gully
            team_name: Optional team name for the user

        Returns:
            Added participant data
        """
        # Check if participant already exists
        existing = await self.get_participant(gully_id, user_id)
        if existing:
            logger.info(
                f"User {user_id} is already a participant in gully {gully_id}, returning existing participant"
            )
            return existing

        # Create new participant without admin permission checks
        participant = GullyParticipant(
            gully_id=gully_id,
            user_id=user_id,
            role=role,
            team_name=team_name,
        )

        self.db.add(participant)
        await self.db.commit()
        await self.db.refresh(participant)

        return {
            "id": participant.id,
            "user_id": participant.user_id,
            "gully_id": participant.gully_id,
            "role": participant.role,
            "team_name": participant.team_name,
            "created_at": participant.created_at,
            "updated_at": participant.updated_at,
        }

    async def remove_participant(self, gully_id: int, user_id: int) -> bool:
        """
        Remove a participant from a gully.

        Args:
            gully_id: The ID of the gully
            user_id: The ID of the user to remove

        Returns:
            True if removal was successful, False otherwise
        """
        stmt = select(GullyParticipant).where(
            (GullyParticipant.gully_id == gully_id)
            & (GullyParticipant.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        participant = result.scalars().first()

        if not participant:
            return False

        await self.db.delete(participant)
        await self.db.commit()
        return True

    async def update_participant(
        self, participant_id: int, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update a participant's role or team name.

        Args:
            participant_id: The ID of the participant
            update_data: Update data including role and/or team_name

        Returns:
            Updated participant data or None if not found
        """
        participant = await self.db.get(GullyParticipant, participant_id)
        if not participant:
            return None

        for key, value in update_data.items():
            setattr(participant, key, value)

        await self.db.commit()
        await self.db.refresh(participant)

        return {
            "id": participant.id,
            "user_id": participant.user_id,
            "gully_id": participant.gully_id,
            "role": participant.role,
            "team_name": participant.team_name,
            "created_at": participant.created_at,
            "updated_at": participant.updated_at,
        }

    async def get_user_participations(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all gully participations for a user.

        Args:
            user_id: The ID of the user

        Returns:
            List of participations
        """
        stmt = select(GullyParticipant).where(GullyParticipant.user_id == user_id)
        result = await self.db.execute(stmt)
        participations = result.scalars().all()

        # Convert to dictionaries
        participation_dicts = []
        for participation in participations:
            participation_dict = {
                "id": participation.id,
                "user_id": participation.user_id,
                "gully_id": participation.gully_id,
                "role": participation.role,
                "team_name": participation.team_name,
                "created_at": participation.created_at,
                "updated_at": participation.updated_at,
            }
            participation_dicts.append(participation_dict)

        return participation_dicts

    async def is_admin(self, user_id: int, gully_id: int) -> bool:
        """
        Check if a user is an admin in a gully.

        Args:
            user_id: The ID of the user
            gully_id: The ID of the gully

        Returns:
            True if the user is an admin, False otherwise
        """
        # Special case for bot operations - if user_id is 1 (bot user), always return True
        if user_id == 1:
            logger.info(
                f"Bot user (ID: {user_id}) granted admin access to gully {gully_id}"
            )
            return True

        participant = await self.get_participant(gully_id, user_id)
        if not participant:
            return False
        return participant["role"] == "admin"

    async def get_participants_by_telegram_ids(
        self,
        gully_id: int,
        telegram_ids: List[int],
        skip: int = 0,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get participants in a gully by their Telegram IDs.

        This method is useful for bot operations where we have Telegram IDs
        but need to find the corresponding participants.

        Args:
            gully_id: The ID of the gully
            telegram_ids: List of Telegram IDs to find
            skip: Number of participants to skip
            limit: Maximum number of participants to return

        Returns:
            List of participants matching the Telegram IDs
        """
        from sqlalchemy import and_

        # Join GullyParticipant with User to filter by telegram_id
        stmt = (
            select(GullyParticipant)
            .join(User, GullyParticipant.user_id == User.id)
            .where(
                and_(
                    GullyParticipant.gully_id == gully_id,
                    User.telegram_id.in_(telegram_ids),
                )
            )
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        participants = result.scalars().all()

        # Convert to dictionaries
        participant_dicts = []
        for participant in participants:
            participant_dict = {
                "id": participant.id,
                "user_id": participant.user_id,
                "gully_id": participant.gully_id,
                "role": participant.role,
                "team_name": participant.team_name,
                "created_at": participant.created_at,
                "updated_at": participant.updated_at,
            }
            participant_dicts.append(participant_dict)

        return participant_dicts
