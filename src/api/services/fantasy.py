"""
Fantasy service for the GullyGuru API.
This module provides methods for interacting with fantasy-related database operations.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from sqlmodel import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, and_, or_

from src.api.services.base import BaseService
from src.db.models.models import (
    ParticipantPlayer,
    Player,
    GullyParticipant,
    User,
    AuctionStatus,
    UserPlayerStatus,
)

logger = logging.getLogger(__name__)


class FantasyService(BaseService):
    """Service for fantasy-related operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize the fantasy service.

        Args:
            db: Database session
        """
        super().__init__(None, None)
        self.db = db

    async def get_gully_participant(
        self, user_id: int, gully_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get a gully participant by user_id and gully_id.

        Args:
            user_id: ID of the user
            gully_id: ID of the gully

        Returns:
            Dictionary with participant data or None if not found
        """
        stmt = select(GullyParticipant).where(
            and_(
                GullyParticipant.user_id == user_id,
                GullyParticipant.gully_id == gully_id,
            )
        )
        result = await self.db.execute(stmt)
        participant = result.scalars().first()

        if not participant:
            return None

        # Convert SQLModel to dict
        participant_dict = {
            "id": participant.id,
            "gully_id": participant.gully_id,
            "user_id": participant.user_id,
            "created_at": participant.created_at,
            "updated_at": participant.updated_at,
        }

        return participant_dict

    async def add_to_draft_squad(
        self, gully_participant_id: int, player_id: int
    ) -> Dict[str, Any]:
        """
        Add a player to a participant's draft squad.

        Args:
            gully_participant_id: ID of the gully participant
            player_id: ID of the player to add

        Returns:
            Dictionary with added player data
        """
        # Check if player exists
        player = await self.db.get(Player, player_id)
        if not player:
            raise ValueError(f"Player with ID {player_id} not found")

        # Check if participant exists
        participant = await self.db.get(GullyParticipant, gully_participant_id)
        if not participant:
            raise ValueError(f"Participant with ID {gully_participant_id} not found")

        # Check if player is already in squad
        stmt = select(ParticipantPlayer).where(
            and_(
                ParticipantPlayer.gully_participant_id == gully_participant_id,
                ParticipantPlayer.player_id == player_id,
            )
        )
        result = await self.db.execute(stmt)
        existing_player = result.scalars().first()

        if existing_player:
            raise ValueError(f"Player with ID {player_id} is already in squad")

        # Count players in squad
        stmt = (
            select(func.count())
            .select_from(ParticipantPlayer)
            .where(ParticipantPlayer.gully_participant_id == gully_participant_id)
        )
        result = await self.db.execute(stmt)
        player_count = result.scalar() or 0

        # Check if squad is full (max 11 players)
        if player_count >= 11:
            raise ValueError("Squad is full (max 11 players)")

        # Add player to squad
        participant_player = ParticipantPlayer(
            gully_participant_id=gully_participant_id,
            player_id=player_id,
            status=UserPlayerStatus.DRAFT,
        )
        self.db.add(participant_player)
        await self.db.commit()
        await self.db.refresh(participant_player)

        # Get player details
        player = await self.db.get(Player, player_id)

        # Convert SQLModel to dict
        player_dict = {
            "id": participant_player.id,
            "gully_participant_id": participant_player.gully_participant_id,
            "player_id": participant_player.player_id,
            "status": participant_player.status,
            "created_at": participant_player.created_at,
            "updated_at": participant_player.updated_at,
            "player": {
                "id": player.id,
                "name": player.name,
                "team": player.team,
                "role": player.role,
                "price": player.price,
            },
        }

        return player_dict

    async def remove_from_draft_squad(
        self, gully_participant_id: int, player_id: int
    ) -> bool:
        """
        Remove a player from a participant's draft squad.

        Args:
            gully_participant_id: ID of the gully participant
            player_id: ID of the player to remove

        Returns:
            True if player was removed, False if not found
        """
        # Find the participant player
        stmt = select(ParticipantPlayer).where(
            and_(
                ParticipantPlayer.gully_participant_id == gully_participant_id,
                ParticipantPlayer.player_id == player_id,
            )
        )
        result = await self.db.execute(stmt)
        participant_player = result.scalars().first()

        if not participant_player:
            return False

        # Check if player can be removed (only DRAFT status)
        if participant_player.status != UserPlayerStatus.DRAFT:
            raise ValueError(
                f"Cannot remove player with status {participant_player.status}"
            )

        # Remove player from squad
        await self.db.delete(participant_player)
        await self.db.commit()

        return True

    async def get_draft_squad(self, gully_participant_id: int) -> Dict[str, Any]:
        """
        Get a participant's draft squad.

        Args:
            gully_participant_id: ID of the gully participant

        Returns:
            Dictionary with squad data
        """
        # Check if participant exists
        participant = await self.db.get(GullyParticipant, gully_participant_id)
        if not participant:
            raise ValueError(f"Participant with ID {gully_participant_id} not found")

        # Get players in squad
        stmt = (
            select(ParticipantPlayer, Player)
            .join(Player, ParticipantPlayer.player_id == Player.id)
            .where(ParticipantPlayer.gully_participant_id == gully_participant_id)
        )
        result = await self.db.execute(stmt)
        squad = result.all()

        # Convert SQLModels to dicts
        players = []
        for participant_player, player in squad:
            player_dict = {
                "id": participant_player.id,
                "gully_participant_id": participant_player.gully_participant_id,
                "player_id": participant_player.player_id,
                "status": participant_player.status,
                "created_at": participant_player.created_at,
                "updated_at": participant_player.updated_at,
                "player": {
                    "id": player.id,
                    "name": player.name,
                    "team": player.team,
                    "role": player.role,
                    "price": player.price,
                },
            }
            players.append(player_dict)

        # Get user and gully details
        user = await self.db.get(User, participant.user_id)

        # Build squad dict
        squad_dict = {
            "gully_participant_id": gully_participant_id,
            "gully_id": participant.gully_id,
            "user_id": participant.user_id,
            "username": user.username if user else None,
            "players": players,
            "player_count": len(players),
        }

        return squad_dict

    async def submit_squad(self, gully_participant_id: int) -> Dict[str, Any]:
        """
        Submit a participant's draft squad.

        Args:
            gully_participant_id: ID of the gully participant

        Returns:
            Dictionary with submission result
        """
        # Check if participant exists
        participant = await self.db.get(GullyParticipant, gully_participant_id)
        if not participant:
            raise ValueError(f"Participant with ID {gully_participant_id} not found")

        # Get players in squad
        stmt = select(ParticipantPlayer).where(
            ParticipantPlayer.gully_participant_id == gully_participant_id
        )
        result = await self.db.execute(stmt)
        squad = result.scalars().all()

        # Check if squad has enough players (min 11)
        if len(squad) < 11:
            raise ValueError(
                f"Squad must have at least 11 players (currently has {len(squad)})"
            )

        # Update player statuses to LOCKED
        for player in squad:
            if player.status == UserPlayerStatus.DRAFT:
                player.status = UserPlayerStatus.LOCKED
                player.updated_at = datetime.utcnow()

        await self.db.commit()

        # Update participant has_submitted_squad flag
        participant.has_submitted_squad = True
        participant.updated_at = datetime.utcnow()
        await self.db.commit()

        return {
            "success": True,
            "message": "Squad submitted successfully",
            "gully_participant_id": gully_participant_id,
            "player_count": len(squad),
        }

    async def update_participant_player_status(
        self, player_id: int, new_status: UserPlayerStatus
    ) -> Dict[str, Any]:
        """
        Update the status of a participant player.

        Args:
            player_id: ID of the participant player
            new_status: New status to set

        Returns:
            Dictionary with updated player data
        """
        # Check if participant player exists
        participant_player = await self.db.get(ParticipantPlayer, player_id)
        if not participant_player:
            raise ValueError(f"Participant player with ID {player_id} not found")

        # Validate status transition
        if not self._is_valid_player_status_transition(
            participant_player.status, new_status
        ):
            raise ValueError(
                f"Invalid status transition from {participant_player.status} to {new_status}"
            )

        # Update status
        participant_player.status = new_status
        participant_player.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(participant_player)

        # Get player details
        player = await self.db.get(Player, participant_player.player_id)

        # Convert SQLModel to dict
        player_dict = {
            "id": participant_player.id,
            "gully_participant_id": participant_player.gully_participant_id,
            "player_id": participant_player.player_id,
            "status": participant_player.status,
            "created_at": participant_player.created_at,
            "updated_at": participant_player.updated_at,
            "player": {
                "id": player.id,
                "name": player.name,
                "team": player.team,
                "role": player.role,
                "price": player.price,
            },
        }

        return player_dict

    def _is_valid_player_status_transition(
        self, current_status: UserPlayerStatus, new_status: UserPlayerStatus
    ) -> bool:
        """
        Check if a status transition is valid.

        Args:
            current_status: Current status
            new_status: New status

        Returns:
            True if transition is valid, False otherwise
        """
        # Define valid transitions
        valid_transitions = {
            UserPlayerStatus.DRAFT: [UserPlayerStatus.LOCKED],
            UserPlayerStatus.LOCKED: [
                UserPlayerStatus.CONTESTED,
                UserPlayerStatus.OWNED,
            ],
            UserPlayerStatus.CONTESTED: [UserPlayerStatus.OWNED],
            UserPlayerStatus.OWNED: [],
        }

        # Allow same status
        if current_status == new_status:
            return True

        # Check if transition is valid
        return new_status in valid_transitions.get(current_status, [])

    async def mark_contested_players(self, gully_id: int) -> Dict[str, Any]:
        """
        Mark players as contested if they are selected by multiple users.

        Args:
            gully_id: ID of the gully

        Returns:
            Dictionary with counts of contested and uncontested players
        """
        # Find players selected by multiple users
        subquery = (
            select(ParticipantPlayer.player_id, func.count().label("count"))
            .join(
                GullyParticipant,
                ParticipantPlayer.gully_participant_id == GullyParticipant.id,
            )
            .where(
                and_(
                    GullyParticipant.gully_id == gully_id,
                    ParticipantPlayer.status == UserPlayerStatus.LOCKED,
                )
            )
            .group_by(ParticipantPlayer.player_id)
            .having(func.count() > 1)
            .subquery()
        )

        # Get participant players for contested players
        stmt = (
            select(ParticipantPlayer)
            .join(
                GullyParticipant,
                ParticipantPlayer.gully_participant_id == GullyParticipant.id,
            )
            .join(subquery, ParticipantPlayer.player_id == subquery.c.player_id)
            .where(
                and_(
                    GullyParticipant.gully_id == gully_id,
                    ParticipantPlayer.status == UserPlayerStatus.LOCKED,
                )
            )
        )

        result = await self.db.execute(stmt)
        contested_players = result.scalars().all()

        # Update status to CONTESTED
        contested_count = 0
        for player in contested_players:
            player.status = UserPlayerStatus.CONTESTED
            player.updated_at = datetime.utcnow()
            contested_count += 1

        # Find uncontested players
        stmt = (
            select(ParticipantPlayer)
            .join(
                GullyParticipant,
                ParticipantPlayer.gully_participant_id == GullyParticipant.id,
            )
            .where(
                and_(
                    GullyParticipant.gully_id == gully_id,
                    ParticipantPlayer.status == UserPlayerStatus.LOCKED,
                    ~ParticipantPlayer.player_id.in_(select(subquery.c.player_id)),
                )
            )
        )

        result = await self.db.execute(stmt)
        uncontested_players = result.scalars().all()

        # Update status to OWNED
        uncontested_count = 0
        for player in uncontested_players:
            player.status = UserPlayerStatus.OWNED
            player.updated_at = datetime.utcnow()
            uncontested_count += 1

        await self.db.commit()

        return {
            "contested_count": contested_count,
            "uncontested_count": uncontested_count,
            "total_count": contested_count + uncontested_count,
        }

    async def resolve_contested_player(
        self, player_id: int, winning_participant_id: int
    ) -> Dict[str, Any]:
        """
        Resolve a contested player by assigning it to the winning participant.

        Args:
            player_id: ID of the player
            winning_participant_id: ID of the winning participant

        Returns:
            Dictionary with updated player data
        """
        # Find all participant players for this player
        stmt = select(ParticipantPlayer).where(
            and_(
                ParticipantPlayer.player_id == player_id,
                ParticipantPlayer.status == UserPlayerStatus.CONTESTED,
            )
        )
        result = await self.db.execute(stmt)
        contested_players = result.scalars().all()

        if not contested_players:
            raise ValueError(f"No contested players found with player ID {player_id}")

        # Find winning participant player
        winning_player = None
        for player in contested_players:
            if player.gully_participant_id == winning_participant_id:
                winning_player = player
                break

        if not winning_player:
            raise ValueError(
                f"Winning participant with ID {winning_participant_id} not found among contested players"
            )

        # Update winning player status to OWNED
        winning_player.status = UserPlayerStatus.OWNED
        winning_player.updated_at = datetime.utcnow()

        # Delete losing participant players
        for player in contested_players:
            if player.id != winning_player.id:
                await self.db.delete(player)

        await self.db.commit()
        await self.db.refresh(winning_player)

        # Get player details
        player = await self.db.get(Player, winning_player.player_id)

        # Convert SQLModel to dict
        player_dict = {
            "id": winning_player.id,
            "gully_participant_id": winning_player.gully_participant_id,
            "player_id": winning_player.player_id,
            "status": winning_player.status,
            "created_at": winning_player.created_at,
            "updated_at": winning_player.updated_at,
            "player": {
                "id": player.id,
                "name": player.name,
                "team": player.team,
                "role": player.role,
                "price": player.price,
            },
        }

        return player_dict
