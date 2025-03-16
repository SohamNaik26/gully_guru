import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.models import (
    Player,
    Gully,
    GullyParticipant,
    DraftSelection,
    GullyStatus,
)
from src.api.services.base import BaseService

# Configure logging
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

    async def _verify_draft_status(self, gully_id: int) -> Gully:
        """
        Verify that a gully is in draft status.

        Args:
            gully_id: ID of the gully

        Returns:
            Gully object if in draft status

        Raises:
            ValueError: If gully is not in draft status
        """
        gully = await self.db.get(Gully, gully_id)
        if not gully:
            raise ValueError(f"Gully with ID {gully_id} not found")

        if gully.status != GullyStatus.DRAFT.value:
            raise ValueError(
                f"Gully is not in draft status. Current status: {gully.status}"
            )

        return gully

    async def _get_participant(
        self, participant_id: int
    ) -> Tuple[GullyParticipant, Gully]:
        """
        Get a participant by ID.

        Args:
            participant_id: ID of the participant

        Returns:
            Tuple of participant and gully

        Raises:
            ValueError: If participant not found
        """
        # Use a join to get both participant and gully in one query
        stmt = (
            select(GullyParticipant, Gully)
            .join(Gully, GullyParticipant.gully_id == Gully.id)
            .where(GullyParticipant.id == participant_id)
        )

        result = await self.db.execute(stmt)
        row = result.first()

        if not row:
            raise ValueError(f"Participant with ID {participant_id} not found")

        return row[0], row[1]

    async def get_gully_participant(
        self, user_id: int, gully_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get a gully participant by user ID and gully ID.

        Args:
            user_id: User ID
            gully_id: Gully ID

        Returns:
            Gully participant data or None if not found
        """
        result = await self.db.execute(
            select(GullyParticipant).where(
                GullyParticipant.user_id == user_id,
                GullyParticipant.gully_id == gully_id,
            )
        )
        participant = result.scalar_one_or_none()

        if not participant:
            return None

        return {
            "id": participant.id,
            "user_id": participant.user_id,
            "gully_id": participant.gully_id,
            "team_name": participant.team_name,
            "budget": float(participant.budget),
            "points": participant.points,
            "role": participant.role,
            "has_submitted_squad": participant.has_submitted_squad,
            "submission_time": participant.submission_time,
            "created_at": participant.created_at,
            "updated_at": participant.updated_at,
        }

    async def get_draft_squad(self, participant_id: int) -> Dict[str, Any]:
        """
        Get a participant's draft squad.

        Args:
            participant_id: ID of the gully participant

        Returns:
            Dictionary with squad data
        """
        participant, _ = await self._get_participant(participant_id)

        # Get draft selections for this participant
        stmt = (
            select(DraftSelection, Player)
            .join(Player, DraftSelection.player_id == Player.id)
            .where(DraftSelection.gully_participant_id == participant_id)
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        # Convert to dictionary format
        players = []
        for selection, player in rows:
            player_dict = {
                "id": player.id,
                "name": player.name,
                "team": player.team,
                "player_type": player.player_type,  # This is already the enum value string
                "base_price": (float(player.base_price) if player.base_price else None),
                "sold_price": (float(player.sold_price) if player.sold_price else None),
                "season": player.season,
                "draft_selection_id": selection.id,
                "selected_at": selection.selected_at,
            }
            players.append(player_dict)

        return {
            "players": players,
        }

    async def bulk_add_players_to_draft(
        self, participant_id: int, player_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Add multiple players to a participant's draft squad.

        Args:
            participant_id: ID of the gully participant
            player_ids: List of player IDs to add

        Returns:
            Dictionary with result information
        """
        participant, _ = await self._get_participant(participant_id)

        # Add players to draft
        added_count = 0
        failed_ids = []

        for player_id in player_ids:
            try:
                # Check if player exists
                player = await self.db.get(Player, player_id)
                if not player:
                    failed_ids.append(player_id)
                    continue

                # Check if player is already in draft for this participant
                existing_selection = await self.db.execute(
                    select(DraftSelection).where(
                        DraftSelection.gully_participant_id == participant_id,
                        DraftSelection.player_id == player_id,
                    )
                )
                existing_selection = existing_selection.scalar_one_or_none()

                if existing_selection:
                    # Player already in draft, skip
                    continue

                # Add player to draft
                draft_selection = DraftSelection(
                    gully_participant_id=participant_id,
                    player_id=player_id,
                    selected_at=datetime.now(timezone.utc),
                )

                self.db.add(draft_selection)
                added_count += 1

            except Exception as e:
                logger.error(f"Error adding player {player_id}: {str(e)}")
                failed_ids.append(player_id)

        await self.db.commit()

        return {
            "success": added_count > 0,
            "message": f"Added {added_count} players to draft squad. Failed: {len(failed_ids)}.",
            "added_count": added_count,
            "failed_ids": failed_ids,
        }

    async def bulk_remove_players_from_draft(
        self, participant_id: int, player_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Remove multiple players from a participant's draft squad.

        Args:
            participant_id: ID of the gully participant
            player_ids: List of player IDs to remove

        Returns:
            Dictionary with result information
        """
        participant, _ = await self._get_participant(participant_id)

        # Remove players from draft
        removed_count = 0
        failed_ids = []

        for player_id in player_ids:
            try:
                # Find the draft selection
                draft_selection = await self.db.execute(
                    select(DraftSelection).where(
                        DraftSelection.gully_participant_id == participant_id,
                        DraftSelection.player_id == player_id,
                    )
                )
                draft_selection = draft_selection.scalar_one_or_none()

                if not draft_selection:
                    failed_ids.append(player_id)
                    continue

                # Remove player from draft
                await self.db.delete(draft_selection)
                removed_count += 1

            except Exception as e:
                logger.error(f"Error removing player {player_id}: {str(e)}")
                failed_ids.append(player_id)

        await self.db.commit()

        return {
            "success": removed_count > 0,
            "message": f"Removed {removed_count} players from draft squad. Failed: {len(failed_ids)}.",
            "removed_count": removed_count,
            "failed_ids": failed_ids,
        }

    async def update_draft_squad(
        self, participant_id: int, player_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Update a participant's draft squad by replacing all players.

        This method removes all existing draft selections and adds the new ones.

        Args:
            participant_id: ID of the gully participant
            player_ids: List of player IDs for the updated squad

        Returns:
            Dictionary with result information
        """
        participant, _ = await self._get_participant(participant_id)

        # First, remove all existing draft selections
        await self.db.execute(
            delete(DraftSelection).where(
                DraftSelection.gully_participant_id == participant_id
            )
        )

        # Then add all the new players
        result = await self.bulk_add_players_to_draft(participant_id, player_ids)

        return {
            "success": result["success"],
            "message": f"Updated draft squad with {result['added_count']} players.",
            "added_count": result["added_count"],
            "failed_ids": result["failed_ids"],
        }
