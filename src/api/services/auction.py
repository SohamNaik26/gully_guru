"""
TODO: given the new draft player table, we need to update the auction service to use the new table.
Auction service for the GullyGuru API.
This module provides business logic for auction-related operations.
"""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import select, update, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.db.models.models import (
    Gully,
    GullyParticipant,
    Player,
    ParticipantPlayer,
    UserPlayerStatus,
    AuctionQueue,
    AuctionStatus,
)
from src.api.exceptions import NotFoundException, ValidationException

# Configure logging
logger = logging.getLogger(__name__)


class AuctionService:
    """Service for auction-related operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize the auction service.

        Args:
            db: Database session
        """
        self.db = db

    async def start_auction(self, gully_id: int) -> Dict[str, Any]:
        """
        Start auction for a gully.

        Args:
            gully_id: Gully ID

        Returns:
            Dict with auction start status

        Raises:
            ValidationException: If auction cannot be started
        """
        # Check if gully exists
        gully = await self._get_gully(gully_id)
        if not gully:
            raise NotFoundException(resource_type="Gully", resource_id=gully_id)

        # Check if all participants have submitted their squads
        submission_status = await self.get_submission_status(gully_id)
        if not submission_status.get("is_complete", False):
            raise ValidationException(
                "All participants must submit their squads before starting the auction"
            )

        # Mark contested players
        await self.mark_contested_players(gully_id)

        # Get counts of contested and uncontested players
        contested_players = await self.get_contested_players(gully_id)
        uncontested_players = await self.get_uncontested_players(gully_id)

        # Create auction response
        return {
            "gully_id": gully_id,
            "status": "started",
            "contested_players_count": len(contested_players),
            "uncontested_players_count": len(uncontested_players),
        }

    async def mark_contested_players(self, gully_id: int) -> Dict[str, Any]:
        """
        Mark players as contested if they are selected by multiple users.

        Args:
            gully_id: Gully ID

        Returns:
            Dict with counts of contested and uncontested players

        Raises:
            NotFoundException: If gully not found
        """
        # Check if gully exists
        gully = await self._get_gully(gully_id)
        if not gully:
            raise NotFoundException(resource_type="Gully", resource_id=gully_id)

        # Get all participant players for the gully
        stmt = (
            select(ParticipantPlayer)
            .join(
                GullyParticipant,
                ParticipantPlayer.gully_participant_id == GullyParticipant.id,
            )
            .where(GullyParticipant.gully_id == gully_id)
        )
        result = await self.db.execute(stmt)
        participant_players = result.scalars().all()

        # Count occurrences of each player
        player_counts = {}
        for participant_player in participant_players:
            player_id = participant_player.player_id
            if player_id in player_counts:
                player_counts[player_id].append(participant_player)
            else:
                player_counts[player_id] = [participant_player]

        # Mark players as contested or uncontested
        contested_count = 0
        uncontested_count = 0

        for player_id, participant_player_list in player_counts.items():
            if len(participant_player_list) > 1:
                # Player is contested
                contested_count += 1
                for participant_player in participant_player_list:
                    participant_player.status = UserPlayerStatus.CONTESTED.value

                # Add to auction queue
                await self._add_to_auction_queue(gully_id, player_id)
            else:
                # Player is uncontested
                uncontested_count += 1
                participant_player_list[0].status = UserPlayerStatus.UNCONTESTED.value

        # Commit changes
        await self.db.commit()

        return {
            "gully_id": gully_id,
            "contested_count": contested_count,
            "uncontested_count": uncontested_count,
        }

    async def _add_to_auction_queue(self, gully_id: int, player_id: int) -> None:
        """
        Add a player to the auction queue.

        Args:
            gully_id: Gully ID
            player_id: Player ID
        """
        # Check if player is already in auction queue
        stmt = select(AuctionQueue).where(
            and_(
                AuctionQueue.gully_id == gully_id,
                AuctionQueue.player_id == player_id,
            )
        )
        result = await self.db.execute(stmt)
        existing_queue_item = result.scalars().first()

        if not existing_queue_item:
            # Create new auction queue item
            new_queue_item = AuctionQueue(
                gully_id=gully_id,
                player_id=player_id,
                status=AuctionStatus.PENDING.value,
            )
            self.db.add(new_queue_item)

    async def get_contested_players(self, gully_id: int) -> List[Dict[str, Any]]:
        """
        Get contested players for a gully.

        Args:
            gully_id: Gully ID

        Returns:
            List of contested players with participant info

        Raises:
            NotFoundException: If gully not found
        """
        # Check if gully exists
        gully = await self._get_gully(gully_id)
        if not gully:
            raise NotFoundException(resource_type="Gully", resource_id=gully_id)

        # Get all contested participant players for the gully
        stmt = (
            select(ParticipantPlayer)
            .join(
                GullyParticipant,
                ParticipantPlayer.gully_participant_id == GullyParticipant.id,
            )
            .join(Player, ParticipantPlayer.player_id == Player.id)
            .where(
                and_(
                    GullyParticipant.gully_id == gully_id,
                    ParticipantPlayer.status == UserPlayerStatus.CONTESTED.value,
                )
            )
            .options(
                joinedload(ParticipantPlayer.player),
                joinedload(ParticipantPlayer.gully_participant),
            )
        )
        result = await self.db.execute(stmt)
        participant_players = result.scalars().all()

        # Group by player
        player_map = {}
        for participant_player in participant_players:
            player_id = participant_player.player_id
            if player_id not in player_map:
                player = participant_player.player
                player_map[player_id] = {
                    "player_id": player_id,
                    "player_name": player.name,
                    "team": player.team,
                    "role": player.player_type,
                    "participants": [],
                }

            # Add participant info
            participant = participant_player.gully_participant
            player_map[player_id]["participants"].append(
                {
                    "participant_id": participant.id,
                    "user_id": participant.user_id,
                    "team_name": participant.team_name,
                }
            )

        return list(player_map.values())

    async def get_uncontested_players(self, gully_id: int) -> List[Dict[str, Any]]:
        """
        Get uncontested players for a gully.

        Args:
            gully_id: Gully ID

        Returns:
            List of uncontested players with participant info

        Raises:
            NotFoundException: If gully not found
        """
        # Check if gully exists
        gully = await self._get_gully(gully_id)
        if not gully:
            raise NotFoundException(resource_type="Gully", resource_id=gully_id)

        # Get all uncontested participant players for the gully
        stmt = (
            select(ParticipantPlayer)
            .join(
                GullyParticipant,
                ParticipantPlayer.gully_participant_id == GullyParticipant.id,
            )
            .join(Player, ParticipantPlayer.player_id == Player.id)
            .where(
                and_(
                    GullyParticipant.gully_id == gully_id,
                    ParticipantPlayer.status == UserPlayerStatus.UNCONTESTED.value,
                )
            )
            .options(
                joinedload(ParticipantPlayer.player),
                joinedload(ParticipantPlayer.gully_participant),
            )
        )
        result = await self.db.execute(stmt)
        participant_players = result.scalars().all()

        # Create player list
        uncontested_players = []
        for participant_player in participant_players:
            player = participant_player.player
            participant = participant_player.gully_participant
            uncontested_players.append(
                {
                    "player_id": player.id,
                    "player_name": player.name,
                    "team": player.team,
                    "role": player.player_type,
                    "participants": [
                        {
                            "participant_id": participant.id,
                            "user_id": participant.user_id,
                            "team_name": participant.team_name,
                        }
                    ],
                }
            )

        return uncontested_players

    async def update_auction_status(
        self, auction_queue_id: int, status: str, gully_id: int
    ) -> bool:
        """
        Update an auction's status.

        Args:
            auction_queue_id: Auction queue ID
            status: New status
            gully_id: Gully ID

        Returns:
            True if update was successful, False otherwise

        Raises:
            ValidationException: If status is invalid
        """
        # Validate status
        try:
            auction_status = AuctionStatus(status)
        except ValueError:
            valid_statuses = [s.value for s in AuctionStatus]
            raise ValidationException(
                f"Invalid status. Must be one of: {valid_statuses}"
            )

        # Update auction status
        stmt = (
            update(AuctionQueue)
            .where(
                and_(
                    AuctionQueue.id == auction_queue_id,
                    AuctionQueue.gully_id == gully_id,
                )
            )
            .values(status=auction_status.value)
        )
        result = await self.db.execute(stmt)

        # Commit changes
        await self.db.commit()

        return result.rowcount > 0

    async def resolve_contested_player(
        self, player_id: int, winning_participant_id: int
    ) -> Dict[str, Any]:
        """
        Resolve a contested player by assigning it to the winning participant.

        Args:
            player_id: Player ID
            winning_participant_id: ID of the winning participant

        Returns:
            Dict with updated player data

        Raises:
            NotFoundException: If player or participant not found
            ValidationException: If player is not contested
        """
        # Check if player exists
        stmt = select(Player).where(Player.id == player_id)
        result = await self.db.execute(stmt)
        player = result.scalars().first()
        if not player:
            raise NotFoundException(resource_type="Player", resource_id=player_id)

        # Check if winning participant exists
        stmt = select(GullyParticipant).where(
            GullyParticipant.id == winning_participant_id
        )
        result = await self.db.execute(stmt)
        winning_participant = result.scalars().first()
        if not winning_participant:
            raise NotFoundException(
                resource_type="Participant", resource_id=winning_participant_id
            )

        # Get all participant players for this player in the same gully
        gully_id = winning_participant.gully_id
        stmt = (
            select(ParticipantPlayer)
            .join(
                GullyParticipant,
                ParticipantPlayer.gully_participant_id == GullyParticipant.id,
            )
            .where(
                and_(
                    ParticipantPlayer.player_id == player_id,
                    GullyParticipant.gully_id == gully_id,
                )
            )
            .options(joinedload(ParticipantPlayer.gully_participant))
        )
        result = await self.db.execute(stmt)
        participant_players = result.scalars().all()

        # Check if player is contested
        if len(participant_players) <= 1:
            raise ValidationException(f"Player {player_id} is not contested")

        # Find the winning participant player
        winning_participant_player = None
        for participant_player in participant_players:
            if participant_player.gully_participant_id == winning_participant_id:
                winning_participant_player = participant_player
                break

        if not winning_participant_player:
            raise ValidationException(
                f"Participant {winning_participant_id} did not select player {player_id}"
            )

        # Update winning participant player status
        winning_participant_player.status = UserPlayerStatus.OWNED.value

        # Delete other participant players
        for participant_player in participant_players:
            if participant_player.gully_participant_id != winning_participant_id:
                await self.db.delete(participant_player)

        # Update auction queue item if it exists
        stmt = select(AuctionQueue).where(
            and_(
                AuctionQueue.player_id == player_id,
                AuctionQueue.gully_id == gully_id,
            )
        )
        result = await self.db.execute(stmt)
        auction_queue_item = result.scalars().first()

        if auction_queue_item:
            auction_queue_item.status = AuctionStatus.COMPLETED.value

        # Commit changes
        await self.db.commit()

        return {
            "player_id": player_id,
            "winning_participant_id": winning_participant_id,
            "status": "resolved",
        }

    async def get_submission_status(self, gully_id: int) -> Dict[str, Any]:
        """
        Get the submission status for a gully.

        Args:
            gully_id: Gully ID

        Returns:
            Dict with submission status data

        Raises:
            NotFoundException: If gully not found
        """
        # Check if gully exists
        gully = await self._get_gully(gully_id)
        if not gully:
            raise NotFoundException(resource_type="Gully", resource_id=gully_id)

        # Get all participants in the gully
        stmt = select(GullyParticipant).where(GullyParticipant.gully_id == gully_id)
        result = await self.db.execute(stmt)
        participants = result.scalars().all()
        total_participants = len(participants)

        # Count submitted participants
        submitted_count = 0
        for participant in participants:
            if participant.has_submitted_squad:
                submitted_count += 1

        # Determine if all participants have submitted
        is_complete = submitted_count == total_participants and total_participants > 0

        return {
            "gully_id": gully_id,
            "total_participants": total_participants,
            "submitted_count": submitted_count,
            "is_complete": is_complete,
            "status": "complete" if is_complete else "pending",
        }

    async def _get_gully(self, gully_id: int) -> Optional[Gully]:
        """
        Get a gully by ID.

        Args:
            gully_id: Gully ID

        Returns:
            Gully if found, None otherwise
        """
        stmt = select(Gully).where(Gully.id == gully_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()
