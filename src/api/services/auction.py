"""
Auction service for the GullyGuru API.
This module provides business logic for auction-related operations.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
from sqlalchemy import select, update, and_, or_, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone

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
    Bid,
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
    NextPlayerResponse,
    ResolveContestedPlayerRequest,
    RevertAuctionRequest,
    RevertAuctionResponse,
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

        This function:
        1. Retrieves all draft squad selections for the gully
        2. Identifies contested and uncontested players
        3. Moves uncontested players to participant_players
        4. Adds contested players to the auction queue

        Args:
            gully_id: Gully ID

        Returns:
            Tuple of (contested_players, uncontested_players)
        """
        # Get all participants for this gully
        stmt = select(GullyParticipant).where(GullyParticipant.gully_id == gully_id)
        result = await self.db.execute(stmt)
        participants = {p.id: p for p in result.scalars().all()}

        # Get all draft selections for this gully
        draft_selections = []
        for participant_id in participants.keys():
            stmt = select(DraftSelection).where(
                DraftSelection.gully_participant_id == participant_id
            )
            result = await self.db.execute(stmt)
            selections = result.scalars().all()
            for s in selections:
                draft_selections.append(
                    {"participant_id": participant_id, "player_id": s.player_id}
                )

        # Count player occurrences to identify contested players
        player_counts = {}
        for selection in draft_selections:
            player_id = selection["player_id"]
            if player_id not in player_counts:
                player_counts[player_id] = []
            player_counts[player_id].append(selection["participant_id"])

        # Separate contested and uncontested players
        contested_players = []
        uncontested_players = []

        # Get player details
        all_player_ids = list(player_counts.keys())
        if not all_player_ids:
            return [], []

        stmt = select(Player).where(Player.id.in_(all_player_ids))
        result = await self.db.execute(stmt)
        players = {p.id: p for p in result.scalars().all()}

        # Process each player
        for player_id, participant_ids in player_counts.items():
            player = players.get(player_id)
            if not player:
                logger.warning(f"Player {player_id} not found in database")
                continue

            if len(participant_ids) > 1:
                # CONTESTED: Use ContestPlayerResponse schema directly
                logger.info(
                    f"Player {player_id} ({player.name}) is contested among {len(participant_ids)} participants"
                )

                # Create participant info objects for each contestant
                contestant_list = [
                    ParticipantInfo(
                        participant_id=pid,
                        user_id=participants[pid].user_id,
                        team_name=(
                            participants[pid].team_name
                            if pid in participants
                            else "Unknown"
                        ),
                    )
                    for pid in participant_ids
                ]

                # Add to contested players list using schema objects
                contest_player = ContestPlayerResponse(
                    player_id=player_id,
                    name=player.name,
                    team=player.team,
                    player_type=player.player_type,
                    base_price=float(player.base_price or 0),
                    contested_by=contestant_list,
                    contest_count=len(participant_ids),
                )
                contested_players.append(contest_player)

                # Add contested players to auction queue ONLY, not to participant_players
                new_queue_item = AuctionQueue(
                    gully_id=gully_id,
                    player_id=player_id,
                    auction_type=AuctionType.NEW_PLAYER.value,
                    status=AuctionStatus.PENDING.value,
                )
                self.db.add(new_queue_item)

            else:
                # UNCONTESTED: Use UncontestedPlayerResponse schema directly
                participant_id = participant_ids[0]
                logger.info(
                    f"Player {player_id} ({player.name}) is uncontested for participant {participant_id}"
                )

                # Create participant info for the owner
                participant_info = ParticipantInfo(
                    participant_id=participant_id,
                    user_id=participants[participant_id].user_id,
                    team_name=(
                        participants[participant_id].team_name
                        if participant_id in participants
                        else "Unknown"
                    ),
                )

                # Add to uncontested players list using schema objects
                uncontested_player = UncontestedPlayerResponse(
                    player_id=player_id,
                    player_name=player.name,
                    team=player.team,
                    role=player.player_type,
                    participants=[participant_info],
                )
                uncontested_players.append(uncontested_player)

                # Add to participant_players with a purchase_price value
                new_participant_player = ParticipantPlayer(
                    gully_participant_id=participant_id,
                    player_id=player_id,
                    status=UserPlayerStatus.LOCKED.value,  # Locked until release window
                    purchase_price=player.base_price,  # Always set to base_price during squad selection
                    is_captain=False,
                    is_vice_captain=False,
                    is_playing_xi=True,
                )
                self.db.add(new_participant_player)

        await self.db.commit()
        return contested_players, uncontested_players

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
        Get all players for a gully. Uncontested + Contested players are not included.

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

    async def get_next_player(self, gully_id: int) -> Dict[str, Any]:
        """
        Get the next player from the auction queue for a specific gully.
        Also provides current budget & team details for all participants.

        Args:
            gully_id: ID of the gully

        Returns:
            Dict with next player and participant information

        Raises:
            NotFoundException: If gully not found
            ValidationException: If gully is not in auction state or if participants
                                haven't confirmed their initial players
        """
        # Ensure gully exists and is in auction state
        gully = await self._get_gully(gully_id)
        if not gully:
            raise NotFoundException(resource_type="Gully", resource_id=gully_id)

        if gully.status != GullyStatus.AUCTION.value:
            raise ValidationException(
                f"Gully {gully_id} is not in auction state. Current state: {gully.status}"
            )

        async with self.db as session:
            # Check if all participants have confirmed their initial players
            # Get all participants for this gully
            stmt = select(GullyParticipant).where(GullyParticipant.gully_id == gully_id)
            result = await session.execute(stmt)
            gully_participants = result.scalars().all()

            # For each participant, check if they have any players that are not in "owned" status
            for participant in gully_participants:
                stmt = select(ParticipantPlayer).where(
                    ParticipantPlayer.gully_participant_id == participant.id,
                    ParticipantPlayer.status != UserPlayerStatus.OWNED.value,
                )
                result = await session.execute(stmt)
                non_owned_players = result.scalars().all()

                if non_owned_players:
                    raise ValidationException(
                        f"Participant {participant.id} ({participant.team_name}) has players that are not in 'owned' status"
                    )

            # Get a random pending player from the auction queue
            stmt = (
                select(AuctionQueue)
                .where(
                    AuctionQueue.gully_id == gully_id,
                    AuctionQueue.status == AuctionStatus.PENDING.value,
                )
                .order_by(func.random())
                .limit(1)
            )
            result = await session.execute(stmt)
            next_auction_item = result.scalar_one_or_none()

            # If no pending player, try to find any in "bidding" status
            if not next_auction_item:
                stmt = (
                    select(AuctionQueue)
                    .where(
                        AuctionQueue.gully_id == gully_id,
                        AuctionQueue.status == AuctionStatus.BIDDING.value,
                    )
                    .order_by(func.random())
                    .limit(1)
                )
                result = await session.execute(stmt)
                next_auction_item = result.scalar_one_or_none()

            # If a player is found, update status to "bidding"
            if (
                next_auction_item
                and next_auction_item.status == AuctionStatus.PENDING.value
            ):
                next_auction_item.status = AuctionStatus.BIDDING.value
                await session.commit()

            # Prepare the next player info
            player_info = None
            if next_auction_item:
                # Get the player details
                stmt = select(Player).where(Player.id == next_auction_item.player_id)
                result = await session.execute(stmt)
                player = result.scalar_one_or_none()

                if player:
                    player_info = {
                        "auction_queue_id": next_auction_item.id,
                        "player_id": player.id,
                        "name": player.name,
                        "team": player.team,
                        "player_type": player.player_type,
                        "base_price": (
                            float(player.base_price) if player.base_price else 0.0
                        ),
                    }

            # Get all participants with their budget and current team
            participants_info = []
            for participant in gully_participants:
                # Get the player information for this participant
                stmt = (
                    select(ParticipantPlayer, Player)
                    .join(Player, ParticipantPlayer.player_id == Player.id)
                    .where(
                        ParticipantPlayer.gully_participant_id == participant.id,
                        ParticipantPlayer.status == UserPlayerStatus.OWNED.value,
                    )
                )
                result = await session.execute(stmt)
                owned_players = result.all()

                # Calculate players owned and remaining
                players_owned = len(owned_players)
                max_squad_size = 18  # This should be configurable or from a constant
                players_remaining = max_squad_size - players_owned

                # Format each player info
                team = []
                for pp, player in owned_players:
                    team.append(
                        {
                            "player_id": player.id,
                            "name": player.name,
                            "purchase_price": float(pp.purchase_price),
                        }
                    )

                participants_info.append(
                    {
                        "participant_id": participant.id,
                        "team_name": participant.team_name,
                        "budget": float(participant.budget),
                        "players_owned": players_owned,
                        "players_remaining": players_remaining,
                        "team": team,
                    }
                )

            return {"player": player_info, "participants": participants_info}

    async def resolve_contested_player(
        self,
        player_id: int,
        winning_participant_id: int,
        auction_queue_id: int,
        bid_amount: float,
    ) -> Dict[str, Any]:
        """
        Resolve a contested player by assigning it to the winning participant.

        Args:
            player_id: ID of the player
            winning_participant_id: ID of the winning participant
            auction_queue_id: ID of the auction queue item
            bid_amount: Amount of the winning bid

        Returns:
            Dict with resolution information

        Raises:
            NotFoundException: If player, participant, or auction queue item not found
            ValidationException: If bid amount exceeds budget or auction status is not valid
        """
        async with self.db as session:
            # Verify the auction queue item exists and is in bidding status
            stmt = select(AuctionQueue).where(
                AuctionQueue.id == auction_queue_id,
                AuctionQueue.player_id == player_id,
                AuctionQueue.status == AuctionStatus.BIDDING.value,
            )
            result = await session.execute(stmt)
            auction_item = result.scalar_one_or_none()

            if not auction_item:
                raise NotFoundException(
                    f"Player {player_id} not found in auction queue or not in bidding status"
                )

            # Get gully ID from auction item
            gully_id = auction_item.gully_id

            # Verify gully is in auction state
            stmt = select(Gully).where(Gully.id == gully_id)
            result = await session.execute(stmt)
            gully = result.scalar_one_or_none()

            if not gully or gully.status != GullyStatus.AUCTION.value:
                raise ValidationException(f"Gully {gully_id} is not in auction state")

            # Verify the winning participant exists and belongs to this gully
            stmt = select(GullyParticipant).where(
                GullyParticipant.id == winning_participant_id,
                GullyParticipant.gully_id == gully_id,
            )
            result = await session.execute(stmt)
            participant = result.scalar_one_or_none()

            if not participant:
                raise NotFoundException(
                    f"Participant {winning_participant_id} not found in gully {gully_id}"
                )

            # Check budget is sufficient
            if float(participant.budget) < bid_amount:
                raise ValidationException(
                    f"Participant {winning_participant_id} has insufficient budget: {participant.budget} < {bid_amount}"
                )

            # Get player details for response
            stmt = select(Player).where(Player.id == player_id)
            result = await session.execute(stmt)
            player = result.scalar_one_or_none()

            if not player:
                raise NotFoundException(resource_type="Player", resource_id=player_id)

            # 1. Register the final bid
            bid = Bid(
                auction_queue_id=auction_queue_id,
                gully_participant_id=winning_participant_id,
                bid_amount=bid_amount,
                bid_time=datetime.now(timezone.utc),
            )
            session.add(bid)

            # 2. Update player status to owned
            stmt = select(ParticipantPlayer).where(
                and_(
                    ParticipantPlayer.player_id == player_id,
                    ParticipantPlayer.gully_participant_id == winning_participant_id,
                )
            )
            result = await session.execute(stmt)
            participant_player = result.scalar_one_or_none()

            if not participant_player:
                raise NotFoundException(
                    f"Participant player for player {player_id} and participant {winning_participant_id} not found"
                )

            participant_player.status = UserPlayerStatus.OWNED.value

            # 3. Update auction queue item status to completed
            stmt = select(AuctionQueue).where(
                and_(
                    AuctionQueue.id == auction_queue_id,
                    AuctionQueue.player_id == player_id,
                )
            )
            result = await session.execute(stmt)
            auction_item = result.scalar_one_or_none()

            if not auction_item:
                raise NotFoundException(
                    f"Auction queue item for player {player_id} not found"
                )

            auction_item.status = AuctionStatus.COMPLETED.value

            # Commit changes
            await session.commit()

            return {
                "success": True,
                "message": f"Player {player.name} has been assigned to {participant.team_name}",
                "data": {
                    "status": "resolved",
                    "auction_queue_id": auction_queue_id,
                    "player_id": player_id,
                    "player_name": player.name,
                    "winning_participant_id": winning_participant_id,
                    "winning_team_name": participant.team_name,
                },
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
        Also updates the status of remaining locked players to owned and
        deducts their cost from participant's budget.

        Args:
            participant_id: ID of the participant
            player_ids: IDs of the players to release

        Returns:
            Dict with released player information and budget impact
        """
        # Check if participant exists
        stmt = select(GullyParticipant).where(GullyParticipant.id == participant_id)
        result = await self.db.execute(stmt)
        participant = result.scalars().first()
        if not participant:
            raise NotFoundException(
                resource_type="GullyParticipant", resource_id=participant_id
            )

        gully_id = participant.gully_id

        # Get players from participant
        stmt = (
            select(ParticipantPlayer, Player)
            .join(Player, ParticipantPlayer.player_id == Player.id)
            .where(
                and_(
                    ParticipantPlayer.gully_participant_id == participant_id,
                    ParticipantPlayer.player_id.in_(player_ids),
                )
            )
        )
        result = await self.db.execute(stmt)
        participant_players = result.all()

        if not participant_players:
            raise NotFoundException(
                f"No players found for participant {participant_id}"
            )

        released_players = []
        for pp, player in participant_players:
            # Delete the participant player entry
            await self.db.delete(pp)

            # Add to auction queue
            auction_queue = AuctionQueue(
                gully_id=gully_id,
                player_id=player.id,
                seller_participant_id=participant_id,
                auction_type=AuctionType.TRANSFER.value,
                status=AuctionStatus.PENDING.value,
            )
            self.db.add(auction_queue)

            released_players.append(
                {
                    "player_id": player.id,
                    "player_name": player.name,
                    "team": player.team,
                    "player_type": player.player_type,
                    "base_price": (
                        float(player.base_price) if player.base_price else 0.0
                    ),
                }
            )

        # Find all LOCKED players and update their status to OWNED
        stmt = select(ParticipantPlayer).where(
            and_(
                ParticipantPlayer.gully_participant_id == participant_id,
                ParticipantPlayer.status == UserPlayerStatus.LOCKED.value,
            )
        )
        result = await self.db.execute(stmt)
        remaining_players = result.scalars().all()

        updated_count = 0
        updated_budget = Decimal("0.0")

        # For each LOCKED player: update status to OWNED and track base price
        for player in remaining_players:
            # Get the player's base price
            stmt = select(Player).where(Player.id == player.player_id)
            result = await self.db.execute(stmt)
            player_obj = result.scalar_one_or_none()

            # Update status to OWNED
            player.status = UserPlayerStatus.OWNED.value

            # Track the price to deduct from budget
            if player_obj and player_obj.base_price:
                updated_budget += player_obj.base_price

            updated_count += 1

        # Update participant's budget if any players were changed to OWNED
        if updated_budget > Decimal("0.0"):
            # Ensure participant has enough budget
            if participant.budget < updated_budget:
                raise ValidationException(
                    f"Participant {participant_id} has insufficient budget: {participant.budget} < {updated_budget}"
                )

            # Deduct the budget for owned players
            stmt = (
                update(GullyParticipant)
                .where(GullyParticipant.id == participant_id)
                .values(budget=GullyParticipant.budget - updated_budget)
            )
            await self.db.execute(stmt)

        # Commit all changes
        await self.db.commit()

        return {
            "released_count": len(released_players),
            "updated_count": updated_count,
            "released_players": released_players,
            "budget_updated": float(updated_budget),
            "message": f"Released {len(released_players)} players and updated status for {updated_count} players for participant {participant_id}",
        }

    async def revert_auction(
        self, player_id: int, winning_participant_id: int, auction_queue_id: int
    ) -> Dict[str, Any]:
        """
        Revert a previously assigned auctioned player, restoring the auction queue
        and refunding the bid amount. Ensures participant's budget doesn't exceed 120.0.

        Args:
            player_id: ID of the player to revert
            winning_participant_id: ID of the participant that won the player
            auction_queue_id: ID of the auction queue item

        Returns:
            Dict with status and message

        Raises:
            NotFoundException: If player, participant, or auction queue item not found
            ValidationException: If the player is not owned by the participant or gully is not in auction state
        """
        async with self.db as session:
            # Verify auction queue item exists
            stmt = select(AuctionQueue).where(AuctionQueue.id == auction_queue_id)
            result = await session.execute(stmt)
            auction_item = result.scalar_one_or_none()

            if not auction_item:
                raise NotFoundException(
                    resource_type="AuctionQueue", resource_id=auction_queue_id
                )

            # Verify gully is in auction state
            gully_id = auction_item.gully_id
            stmt = select(Gully).where(Gully.id == gully_id)
            result = await session.execute(stmt)
            gully = result.scalar_one_or_none()

            if not gully or gully.status != GullyStatus.AUCTION.value:
                raise ValidationException(f"Gully {gully_id} is not in auction state")

            # Verify participant owns the player
            stmt = select(ParticipantPlayer).where(
                ParticipantPlayer.gully_participant_id == winning_participant_id,
                ParticipantPlayer.player_id == player_id,
                ParticipantPlayer.status == UserPlayerStatus.OWNED.value,
            )
            result = await session.execute(stmt)
            participant_player = result.scalar_one_or_none()

            if not participant_player:
                raise ValidationException(
                    f"Player {player_id} is not owned by participant {winning_participant_id}"
                )

            # Get bid amount - first check bid table, then fallback to purchase price
            stmt = select(Bid).where(
                Bid.auction_queue_id == auction_queue_id,
                Bid.gully_participant_id == winning_participant_id,
            )
            result = await session.execute(stmt)
            bid = result.scalar_one_or_none()

            if bid:
                bid_amount = bid.bid_amount
            else:
                # If no bid is found, use the purchase price from ParticipantPlayer
                bid_amount = participant_player.purchase_price

            # Get participant to check current budget
            stmt = select(GullyParticipant).where(
                GullyParticipant.id == winning_participant_id
            )
            result = await session.execute(stmt)
            participant = result.scalar_one_or_none()

            if not participant:
                raise NotFoundException(
                    resource_type="GullyParticipant", resource_id=winning_participant_id
                )

            # Calculate new budget (refund the bid amount)
            new_budget = participant.budget + bid_amount

            # Cap budget at 120.0 if it exceeds the maximum
            max_budget = Decimal("120.0")
            if new_budget > max_budget:
                new_budget = max_budget

            # 1. Refund the bid amount to participant's budget (with cap)
            stmt = (
                update(GullyParticipant)
                .where(GullyParticipant.id == winning_participant_id)
                .values(budget=new_budget)
            )
            await session.execute(stmt)

            # 2. Remove player from participant's squad
            stmt = delete(ParticipantPlayer).where(
                ParticipantPlayer.gully_participant_id == winning_participant_id,
                ParticipantPlayer.player_id == player_id,
            )
            await session.execute(stmt)

            # 3. Reset the auction queue item status to "pending"
            stmt = (
                update(AuctionQueue)
                .where(AuctionQueue.id == auction_queue_id)
                .values(status=AuctionStatus.PENDING.value)
            )
            await session.execute(stmt)

            # Commit the transaction
            await session.commit()

            return {
                "status": "success",
                "auction_queue_id": auction_queue_id,
                "message": "Auction result reverted. Player returned to auction queue.",
            }
