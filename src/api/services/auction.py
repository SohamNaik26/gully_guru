"""
Auction service for the GullyGuru API.
This module provides business logic for auction-related operations.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
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
    DraftSelection,
    GullyStatus,
    AuctionType,
)
from src.api.exceptions import NotFoundException, ValidationException
from src.api.schemas.auction import (
    AuctionStartResponse,
    ContestPlayerResponse,
    UncontestedPlayerResponse,
    ParticipantInfo,
    ResolveContestedPlayerResponse,
    AuctionStatusEnum,
    AuctionQueueResponse,
)
from src.api.schemas.player import PlayerType
from src.api.schemas.common import SuccessResponse

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

    async def start_auction(self, gully_id: int) -> AuctionStartResponse:
        """
        Start auction for a gully by transitioning from draft to auction state.

        This function:
        1. Validates the gully exists and is in draft state
        2. Processes draft selections, categorizing players as contested or uncontested
        3. Moves uncontested players directly to participant_players with "locked" status
        4. Adds contested players to the auction queue with "pending" status
        5. Adds remaining players from the master player list to the auction queue
        6. Updates the gully status to "auction"

        Args:
            gully_id: Gully ID

        Returns:
            AuctionStartResponse with auction start status and player counts

        Raises:
            NotFoundException: If gully not found
            ValidationException: If auction cannot be started
        """
        # Check if gully exists
        gully = await self._get_gully(gully_id)
        if not gully:
            raise NotFoundException(resource_type="Gully", resource_id=gully_id)

        # Ensure gully is in draft state
        if gully.status != GullyStatus.DRAFT.value:
            raise ValidationException(
                f"Gully must be in draft state to start auction, current state: {gully.status}"
            )

        # Process draft selections and categorize players
        contested_players, uncontested_players = await self._process_draft_selections(
            gully_id
        )

        # Add remaining players from the master player list to the auction queue
        await self._add_players_to_auction_queue_from_player_list(gully_id)

        # Update gully status to auction
        gully.status = GullyStatus.AUCTION.value
        await self.db.commit()

        # Create auction response
        return AuctionStartResponse(
            gully_id=gully_id,
            status="started",
            message="Auction has been started successfully",
            contested_count=len(contested_players),
            uncontested_count=len(uncontested_players),
            contested_players=contested_players,
            uncontested_players=uncontested_players,
        )

    async def _process_draft_selections(
        self, gully_id: int
    ) -> Tuple[List[ContestPlayerResponse], List[UncontestedPlayerResponse]]:
        """
        Process draft selections for a gully, categorizing players as contested or uncontested.

        Args:
            gully_id: Gully ID

        Returns:
            Tuple containing lists of contested and uncontested players
        """
        # Get all draft selections for this gully
        stmt = (
            select(DraftSelection)
            .join(
                GullyParticipant,
                DraftSelection.gully_participant_id == GullyParticipant.id,
            )
            .where(GullyParticipant.gully_id == gully_id)
        )
        result = await self.db.execute(stmt)
        draft_selections = result.scalars().all()

        # Get player IDs and participant IDs
        player_ids = [ds.player_id for ds in draft_selections]
        participant_ids = [ds.gully_participant_id for ds in draft_selections]

        # Fetch players
        stmt = select(Player).where(Player.id.in_(player_ids))
        result = await self.db.execute(stmt)
        players = {p.id: p for p in result.scalars().all()}

        # Fetch participants
        stmt = select(GullyParticipant).where(GullyParticipant.id.in_(participant_ids))
        result = await self.db.execute(stmt)
        participants = {p.id: p for p in result.scalars().all()}

        # Count occurrences of each player
        player_counts = {}
        for draft_selection in draft_selections:
            player_id = draft_selection.player_id
            if player_id in player_counts:
                player_counts[player_id].append(draft_selection)
            else:
                player_counts[player_id] = [draft_selection]

        contested_players = []
        uncontested_players = []

        # Process each player based on selection count
        for player_id, selections in player_counts.items():
            player = players.get(player_id)
            if not player:
                logger.warning(f"Player {player_id} not found in database")
                continue

            if len(selections) > 1:
                # Player is contested - add to auction queue
                await self._add_contested_player_to_auction(
                    gully_id, player_id, selections
                )

                # Add to contested players list for response
                contested_players.append(
                    ContestPlayerResponse(
                        player_id=player.id,
                        name=player.name,
                        team=player.team,
                        player_type=PlayerType(player.player_type),
                        base_price=float(player.base_price or 0),
                        contested_by=[
                            ParticipantInfo(
                                participant_id=selection.gully_participant_id,
                                user_id=participants[
                                    selection.gully_participant_id
                                ].user_id,
                                team_name=participants[
                                    selection.gully_participant_id
                                ].team_name,
                            )
                            for selection in selections
                            if selection.gully_participant_id in participants
                        ],
                        contest_count=len(selections),
                    )
                )
            else:
                # Player is uncontested - add directly to participant_player
                selection = selections[0]
                await self._add_uncontested_player_to_participant(selection)

                # Add to uncontested players list for response
                participant = participants.get(selection.gully_participant_id)
                if participant:
                    uncontested_players.append(
                        UncontestedPlayerResponse(
                            player_id=player.id,
                            player_name=player.name,
                            team=player.team,
                            role=player.player_type,
                            participants=[
                                ParticipantInfo(
                                    participant_id=participant.id,
                                    user_id=participant.user_id,
                                    team_name=participant.team_name,
                                )
                            ],
                        )
                    )

        # Commit all changes
        await self.db.commit()

        return contested_players, uncontested_players

    async def _add_contested_player_to_auction(
        self, gully_id: int, player_id: int, selections: List[DraftSelection]
    ) -> None:
        """
        Add a contested player to the auction queue and create participant_player entries with contested status.

        Args:
            gully_id: Gully ID
            player_id: Player ID
            selections: List of draft selections for this player
        """
        # Add to auction queue if not already there
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
                auction_type=AuctionType.NEW_PLAYER.value,
                status=AuctionStatus.PENDING.value,
            )
            self.db.add(new_queue_item)

        # Create participant_player entries with contested status for each participant
        for selection in selections:
            # Check if participant_player entry already exists
            stmt = select(ParticipantPlayer).where(
                and_(
                    ParticipantPlayer.gully_participant_id
                    == selection.gully_participant_id,
                    ParticipantPlayer.player_id == player_id,
                )
            )
            result = await self.db.execute(stmt)
            existing_participant_player = result.scalars().first()

            if not existing_participant_player:
                # Get player base price
                stmt = select(Player).where(Player.id == player_id)
                result = await self.db.execute(stmt)
                player = result.scalars().first()
                base_price = player.base_price or Decimal("0.0")

                # Create new participant_player entry
                new_participant_player = ParticipantPlayer(
                    gully_participant_id=selection.gully_participant_id,
                    player_id=player_id,
                    purchase_price=base_price,
                    status=UserPlayerStatus.CONTESTED.value,
                )
                self.db.add(new_participant_player)

    async def _add_uncontested_player_to_participant(
        self, selection: DraftSelection
    ) -> None:
        """
        Add an uncontested player directly to participant_player with locked status.

        Args:
            selection: Draft selection for this player
        """
        # Check if participant_player entry already exists
        stmt = select(ParticipantPlayer).where(
            and_(
                ParticipantPlayer.gully_participant_id
                == selection.gully_participant_id,
                ParticipantPlayer.player_id == selection.player_id,
            )
        )
        result = await self.db.execute(stmt)
        existing_participant_player = result.scalars().first()

        if not existing_participant_player:
            # Get player base price
            stmt = select(Player).where(Player.id == selection.player_id)
            result = await self.db.execute(stmt)
            player = result.scalars().first()
            base_price = player.base_price or Decimal("0.0")

            # Create new participant_player entry
            new_participant_player = ParticipantPlayer(
                gully_participant_id=selection.gully_participant_id,
                player_id=selection.player_id,
                purchase_price=base_price,
                status=UserPlayerStatus.LOCKED.value,
            )
            self.db.add(new_participant_player)

    async def _add_players_to_auction_queue_from_player_list(
        self, gully_id: int
    ) -> None:
        """
        Add players from the master Player table to the auction queue if they're not already assigned.

        This ensures all available players are in the auction queue for future transfers.

        Args:
            gully_id: Gully ID
        """
        logger.info(
            f"Adding players from master list to auction queue for gully {gully_id}"
        )

        # Get all players from the master table for the current season
        current_season = 2025  # You might want to get this from a config or the gully
        stmt = select(Player).where(Player.season == current_season)
        result = await self.db.execute(stmt)
        all_players = result.scalars().all()

        # Get players already in the auction queue for this gully
        stmt = select(AuctionQueue.player_id).where(AuctionQueue.gully_id == gully_id)
        result = await self.db.execute(stmt)
        existing_queue_player_ids = {row[0] for row in result.fetchall()}

        # Get players already assigned to participants in this gully
        stmt = (
            select(ParticipantPlayer.player_id)
            .join(
                GullyParticipant,
                ParticipantPlayer.gully_participant_id == GullyParticipant.id,
            )
            .where(GullyParticipant.gully_id == gully_id)
        )
        result = await self.db.execute(stmt)
        assigned_player_ids = {row[0] for row in result.fetchall()}

        # Add players that are not already in the queue or assigned to participants
        players_added = 0
        for player in all_players:
            if (
                player.id not in existing_queue_player_ids
                and player.id not in assigned_player_ids
            ):
                new_queue_item = AuctionQueue(
                    gully_id=gully_id,
                    player_id=player.id,
                    auction_type=AuctionType.NEW_PLAYER.value,
                    status=AuctionStatus.PENDING.value,
                )
                self.db.add(new_queue_item)
                players_added += 1

        logger.info(
            f"Added {players_added} new players to auction queue for gully {gully_id}"
        )

        # Commit changes
        await self.db.commit()

    async def get_players_by_participant(
        self, gully_id: int, status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get players grouped by participant for a gully.

        Args:
            gully_id: Gully ID
            status: Optional filter for player status (locked, contested, owned)

        Returns:
            Dict with gully info and participants with their players

        Raises:
            NotFoundException: If gully not found
        """
        # Check if gully exists
        gully = await self._get_gully(gully_id)
        if not gully:
            raise NotFoundException(resource_type="Gully", resource_id=gully_id)

        # Build the query for participant players
        query = (
            select(ParticipantPlayer)
            .join(
                GullyParticipant,
                ParticipantPlayer.gully_participant_id == GullyParticipant.id,
            )
            .where(GullyParticipant.gully_id == gully_id)
        )

        # Add status filter if provided
        if status:
            query = query.where(ParticipantPlayer.status == status)

        # Execute the query
        result = await self.db.execute(query)
        participant_players = result.scalars().all()

        # Get player IDs and participant IDs
        player_ids = [pp.player_id for pp in participant_players]
        participant_ids = [pp.gully_participant_id for pp in participant_players]

        # Fetch players
        stmt = select(Player).where(Player.id.in_(player_ids))
        result = await self.db.execute(stmt)
        players = {p.id: p for p in result.scalars().all()}

        # Fetch participants
        stmt = select(GullyParticipant).where(GullyParticipant.id.in_(participant_ids))
        result = await self.db.execute(stmt)
        participants = {p.id: p for p in result.scalars().all()}

        # Group players by participant
        participant_players_map = {}
        for participant_player in participant_players:
            player_id = participant_player.player_id
            participant_id = participant_player.gully_participant_id

            player = players.get(player_id)
            participant = participants.get(participant_id)

            if not player or not participant:
                continue

            if participant_id not in participant_players_map:
                participant_players_map[participant_id] = {
                    "participant_id": participant_id,
                    "user_id": participant.user_id,
                    "team_name": participant.team_name,
                    "players": [],
                }

            participant_players_map[participant_id]["players"].append(
                {
                    "player_id": player_id,
                    "player_name": player.name,
                    "team": player.team,
                    "player_type": player.player_type,
                    "base_price": float(player.base_price or 0),
                    "status": participant_player.status,
                }
            )

        # Create response
        return {
            "gully_id": gully_id,
            "gully_name": gully.name,
            "gully_status": gully.status,
            "participants": list(participant_players_map.values()),
            "total_players": len(participant_players),
        }

    async def get_contested_players(self, gully_id: int) -> Dict[str, Any]:
        """
        Get contested players for a gully.

        Args:
            gully_id: Gully ID

        Returns:
            Dict with gully info and participants with their contested players

        Raises:
            NotFoundException: If gully not found
        """
        return await self.get_players_by_participant(
            gully_id, UserPlayerStatus.CONTESTED.value
        )

    async def get_uncontested_players(self, gully_id: int) -> Dict[str, Any]:
        """
        Get uncontested players for a gully.

        Args:
            gully_id: Gully ID

        Returns:
            Dict with gully info and participants with their uncontested players

        Raises:
            NotFoundException: If gully not found
        """
        return await self.get_players_by_participant(
            gully_id, UserPlayerStatus.LOCKED.value
        )

    async def get_all_players(self, gully_id: int) -> Dict[str, Any]:
        """
        Get all players for a gully.

        Args:
            gully_id: Gully ID

        Returns:
            Dict with gully info and participants with all their players

        Raises:
            NotFoundException: If gully not found
        """
        return await self.get_players_by_participant(gully_id)

    async def update_auction_status(
        self, auction_queue_id: int, status: AuctionStatusEnum, gully_id: int
    ) -> SuccessResponse:
        """
        Update an auction's status.

        Args:
            auction_queue_id: Auction queue ID
            status: New status
            gully_id: Gully ID

        Returns:
            SuccessResponse indicating whether the update was successful

        Raises:
            ValidationException: If status is invalid
        """
        # Update auction status
        stmt = (
            update(AuctionQueue)
            .where(
                and_(
                    AuctionQueue.id == auction_queue_id,
                    AuctionQueue.gully_id == gully_id,
                )
            )
            .values(status=status.value)
        )
        result = await self.db.execute(stmt)

        # Commit changes
        await self.db.commit()

        success = result.rowcount > 0
        return SuccessResponse(
            success=success,
            message=(
                f"Auction status updated to {status}"
                if success
                else "Failed to update auction status"
            ),
        )

    async def resolve_contested_player(
        self, player_id: int, winning_participant_id: int
    ) -> ResolveContestedPlayerResponse:
        """
        Resolve a contested player by assigning it to the winning participant.

        Args:
            player_id: Player ID
            winning_participant_id: ID of the winning participant

        Returns:
            ResolveContestedPlayerResponse with updated player data

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

        return ResolveContestedPlayerResponse(
            player_id=player_id,
            player_name=player.name,
            winning_participant_id=winning_participant_id,
            winning_team_name=winning_participant.team_name,
            status="resolved",
            message=f"Player {player.name} has been assigned to {winning_participant.team_name}",
        )

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

    async def stop_auction(self, gully_id: int) -> SuccessResponse:
        """
        Stop auction for a gully by transitioning from auction back to draft state.

        This function:
        1. Validates the gully exists and is in auction state
        2. Deletes participant players that were created during the auction process
        3. Deletes auction queue items that were created during the auction process
        4. Reverts the gully status back to draft

        Args:
            gully_id: Gully ID

        Returns:
            SuccessResponse with success status and message

        Raises:
            NotFoundException: If gully not found
            ValidationException: If auction cannot be stopped
        """
        # Check if gully exists
        gully = await self._get_gully(gully_id)
        if not gully:
            raise NotFoundException(resource_type="Gully", resource_id=gully_id)

        # Ensure gully is in auction state
        if gully.status != GullyStatus.AUCTION.value:
            raise ValidationException(
                f"Gully must be in auction state to stop auction, current state: {gully.status}"
            )

        # Get all participant players for this gully
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

        # Delete all participant players
        for participant_player in participant_players:
            await self.db.delete(participant_player)

        # Delete all auction queue items for this gully
        stmt = select(AuctionQueue).where(AuctionQueue.gully_id == gully_id)
        result = await self.db.execute(stmt)
        auction_queue_items = result.scalars().all()

        for auction_queue_item in auction_queue_items:
            await self.db.delete(auction_queue_item)

        # Reset draft selections' is_submitted flag
        # NEW IMPLEMENTATION: no need to reset draft selections' is_submitted flag

        # Update gully status back to draft
        gully.status = GullyStatus.DRAFT.value

        # Commit changes
        await self.db.commit()

        return SuccessResponse(
            success=True,
            message=f"Auction stopped for gully {gully_id}. Gully status reverted to draft.",
        )

    # method to get all players from the auction queue
    async def get_all_players_from_auction_queue(
        self, gully_id: int
    ) -> List[AuctionQueueResponse]:
        """
        Get all players from the auction queue for a specific gully.

        Args:
            gully_id: Gully ID

        Returns:
            List of AuctionQueueResponse objects
        """
        stmt = select(AuctionQueue).where(AuctionQueue.gully_id == gully_id)
        result = await self.db.execute(stmt)
        auction_queue_items = result.scalars().all()

        # Fetch players
        player_ids = [item.player_id for item in auction_queue_items]
        stmt = select(Player).where(Player.id.in_(player_ids))
        result = await self.db.execute(stmt)
        players = {p.id: p for p in result.scalars().all()}

        # Create response
        response = []
        for item in auction_queue_items:
            player = players.get(item.player_id)
            if player:
                response.append(
                    AuctionQueueResponse(
                        id=item.id,
                        gully_id=gully_id,
                        player_id=player.id,
                        seller_participant_id=item.seller_participant_id,
                        auction_type=item.auction_type,
                        status=item.status,
                        listed_at=item.listed_at,
                        player_name=player.name,
                        team=player.team,
                        player_type=player.player_type,
                        base_price=float(player.base_price or 0),
                    )
                )
        return response

    async def release_players(
        self, participant_id: int, player_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Release players from a participant and add them to the auction queue.

        This function:
        1. Validates the participant exists
        2. Validates the players are owned by the participant
        3. Removes the players from the participant_players table
        4. Adds the players to the auction queue

        Args:
            participant_id: ID of the participant releasing the players
            player_ids: List of player IDs to release

        Returns:
            Dict with release status and released players

        Raises:
            NotFoundException: If participant not found
            ValidationException: If players are not owned by the participant
        """
        # Check if participant exists
        stmt = select(GullyParticipant).where(GullyParticipant.id == participant_id)
        result = await self.db.execute(stmt)
        participant = result.scalars().first()

        if not participant:
            raise NotFoundException(
                resource_type="Participant", resource_id=participant_id
            )

        gully_id = participant.gully_id

        # Get all participant players for this participant
        stmt = select(ParticipantPlayer).where(
            and_(
                ParticipantPlayer.gully_participant_id == participant_id,
                ParticipantPlayer.player_id.in_(player_ids),
                ParticipantPlayer.status.in_(
                    [UserPlayerStatus.LOCKED.value, UserPlayerStatus.OWNED.value]
                ),
            )
        )
        result = await self.db.execute(stmt)
        participant_players = result.scalars().all()

        # Check if all players are owned by the participant
        found_player_ids = [pp.player_id for pp in participant_players]
        missing_player_ids = set(player_ids) - set(found_player_ids)

        if missing_player_ids:
            raise ValidationException(
                f"Players with IDs {missing_player_ids} are not owned by participant {participant_id}"
            )

        # Get player details for response
        player_ids_to_release = [pp.player_id for pp in participant_players]
        stmt = select(Player).where(Player.id.in_(player_ids_to_release))
        result = await self.db.execute(stmt)
        players = {p.id: p for p in result.scalars().all()}

        released_players = []

        # Process each player
        for participant_player in participant_players:
            player_id = participant_player.player_id
            player = players.get(player_id)

            if not player:
                logger.warning(f"Player {player_id} not found in database")
                continue

            # Add to auction queue
            new_queue_item = AuctionQueue(
                gully_id=gully_id,
                player_id=player_id,
                seller_participant_id=participant_id,
                auction_type=AuctionType.TRANSFER.value,
                status=AuctionStatus.PENDING.value,
            )
            self.db.add(new_queue_item)

            # Add to released players list for response
            released_players.append(
                {
                    "player_id": player_id,
                    "player_name": player.name,
                    "team": player.team,
                    "player_type": player.player_type,
                    "base_price": float(player.base_price or 0),
                }
            )

            # Delete from participant_players
            await self.db.delete(participant_player)

        # Commit changes
        await self.db.commit()

        return {
            "released_count": len(released_players),
            "released_players": released_players,
            "message": f"Released {len(released_players)} players from participant {participant_id}",
        }
