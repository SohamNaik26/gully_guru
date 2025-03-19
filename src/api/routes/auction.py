"""
Auction routes for the GullyGuru API.
This module provides API endpoints for auction-related operations.
"""

import logging
from fastapi import APIRouter, Depends, Path, Query, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional

from src.api.dependencies.database import get_db
from src.api.schemas.auction import (
    AuctionQueueListResponse,
    ReleasePlayersRequest,
    ReleasePlayersResponse,
    ResolveContestedPlayerRequest,
    RevertAuctionRequest,
)
from src.api.schemas.fantasy import (
    AuctionStartResponse,
    ContestPlayerResponse,
    SuccessResponse,
)
from src.api.services.auction import AuctionService
from src.api.factories.fantasy import (
    AuctionStartResponseFactory,
    ContestPlayerResponseFactory,
)
from src.api.factories.auction import AuctionResponseFactory
from src.api.exceptions import handle_exceptions, NotFoundException, ValidationException

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auction",
    tags=["Auction"],
)


def get_auction_service(
    db: AsyncSession = Depends(get_db),
) -> AuctionService:
    """
    Get the auction service client.

    Args:
        db: Database session

    Returns:
        AuctionService instance
    """
    return AuctionService(db)


@router.post(
    "/gullies/{gully_id}/start",
    response_model=Dict[str, Any],
    summary="Start auction for a gully",
    status_code=status.HTTP_200_OK,
)
@handle_exceptions
async def start_auction(
    gully_id: int, auction_service: AuctionService = Depends(get_auction_service)
):
    """
    Start auction for a gully.

    Args:
        gully_id: Gully ID
        auction_service: Auction service

    Returns:
        Auction start response
    """
    auction_start = await auction_service.start_auction(gully_id)

    # Convert Pydantic model to dictionary if needed
    if hasattr(auction_start, "model_dump"):
        # For Pydantic v2
        auction_start_dict = auction_start.model_dump()
    elif hasattr(auction_start, "dict"):
        # For Pydantic v1
        auction_start_dict = auction_start.dict()
    else:
        # Already a dict
        auction_start_dict = auction_start

    # Use factory to create response
    return AuctionResponseFactory.create_start_auction_response(auction_start_dict)


@router.post("/gullies/{gully_id}/stop", response_model=Dict[str, Any])
async def stop_auction(
    gully_id: int, auction_service: AuctionService = Depends(get_auction_service)
):
    """
    Stop auction for a gully.

    Args:
        gully_id: Gully ID
        auction_service: Auction service

    Returns:
        Success response
    """
    response = await auction_service.stop_auction(gully_id)

    # Convert Pydantic model to dictionary if needed
    if hasattr(response, "model_dump"):
        # For Pydantic v2
        response_dict = response.model_dump()
    elif hasattr(response, "dict"):
        # For Pydantic v1
        response_dict = response.dict()
    else:
        # Already a dict
        response_dict = response

    # Use factory to create response
    return AuctionResponseFactory.create_stop_auction_response(
        gully_id=gully_id,
        success=response_dict.get("success", True),
        message=response_dict.get("message", "Auction stopped successfully"),
    )


@router.get(
    "/gullies/{gully_id}/auction-queue",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
)
@handle_exceptions
async def get_all_players_from_auction_queue(
    gully_id: int = Path(..., description="ID of the gully"),
    auction_service: AuctionService = Depends(get_auction_service),
):
    """
    Get all players from the auction queue for a specific gully.

    Args:
        gully_id: Gully ID
        auction_service: Auction service instance

    Returns:
        List of AuctionQueueResponse objects
    """
    players = await auction_service.get_all_players_from_auction_queue(gully_id)
    return AuctionResponseFactory.create_auction_queue_response(players, gully_id)


@router.get(
    "/gullies/{gully_id}/contested-players",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
)
@handle_exceptions
async def get_contested_players(
    gully_id: int = Path(..., description="ID of the gully"),
    auction_service: AuctionService = Depends(get_auction_service),
):
    """
    Get contested players for a gully.

    Args:
        gully_id: Gully ID
        auction_service: Auction service instance

    Returns:
        Dict with gully info and participants with their contested players

    Raises:
        NotFoundException: If gully not found
    """
    result = await auction_service.get_contested_players(gully_id)
    return AuctionResponseFactory.create_players_by_participant_response(result)


@router.get(
    "/gullies/{gully_id}/uncontested-players",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
)
@handle_exceptions
async def get_uncontested_players(
    gully_id: int = Path(..., description="ID of the gully"),
    auction_service: AuctionService = Depends(get_auction_service),
):
    """
    Get uncontested players for a gully.

    Args:
        gully_id: Gully ID
        auction_service: Auction service instance

    Returns:
        Dict with gully info and participants with their uncontested players

    Raises:
        NotFoundException: If gully not found
    """
    result = await auction_service.get_uncontested_players(gully_id)
    return AuctionResponseFactory.create_players_by_participant_response(result)


@router.get(
    "/gullies/{gully_id}/all-players",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
)
@handle_exceptions
async def get_all_players(
    gully_id: int = Path(..., description="ID of the gully"),
    auction_service: AuctionService = Depends(get_auction_service),
):
    """
    Get all players for a gully.

    Args:
        gully_id: Gully ID
        auction_service: Auction service instance

    Returns:
        Dict with gully info and participants with all their players

    Raises:
        NotFoundException: If gully not found
    """
    result = await auction_service.get_all_players(gully_id)
    return AuctionResponseFactory.create_players_by_participant_response(result)


@router.put(
    "/queue/{auction_queue_id}/status",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
)
@handle_exceptions
async def update_auction_status(
    auction_queue_id: int = Path(..., description="ID of the auction queue"),
    status: str = Query(..., description="New status for the auction"),
    gully_id: int = Query(..., description="ID of the gully"),
    auction_service: AuctionService = Depends(get_auction_service),
):
    """
    Update an auction's status.

    Args:
        auction_queue_id: Auction queue ID
        status: New status for the auction
        gully_id: Gully ID
        auction_service: Auction service instance

    Returns:
        SuccessResponse: Success status

    Raises:
        NotFoundException: If auction not found
    """
    success = await auction_service.update_auction_status(
        auction_queue_id=auction_queue_id,
        status=status,
        gully_id=gully_id,
    )
    if not success:
        raise NotFoundException(resource_type="Auction", resource_id=auction_queue_id)
    return {"success": True, "message": f"Auction status updated to {status}"}


@router.get(
    "/gullies/{gully_id}/next-player",
    response_model=Dict[str, Any],
    summary="Get the next player from the auction queue",
    status_code=status.HTTP_200_OK,
)
@handle_exceptions
async def get_next_player(
    gully_id: int = Path(..., description="ID of the gully"),
    auction_service: AuctionService = Depends(get_auction_service),
):
    """
    Get the next player from the auction queue for a specific gully.
    Also provides current budget & team details for all participants.

    Args:
        gully_id: ID of the gully
        auction_service: Auction service instance

    Returns:
        Dict with next player and participant information

    Raises:
        NotFoundException: If gully not found
        ValidationException: If gully is not in auction state or participants haven't confirmed their players
    """
    result = await auction_service.get_next_player(gully_id)
    return AuctionResponseFactory.create_next_player_response(result)


@router.post(
    "/resolve-contested/{player_id}/{winning_participant_id}",
    response_model=Dict[str, Any],
    summary="Resolve a contested player",
    status_code=status.HTTP_200_OK,
)
@handle_exceptions
async def resolve_contested_player(
    player_id: int = Path(..., description="ID of the player"),
    winning_participant_id: int = Path(
        ..., description="ID of the winning participant"
    ),
    request: ResolveContestedPlayerRequest = Body(..., description="Bid details"),
    auction_service: AuctionService = Depends(get_auction_service),
):
    """
    Resolve a contested player by assigning it to the winning participant.

    Args:
        player_id: ID of the player
        winning_participant_id: ID of the winning participant
        request: Bid details including auction_queue_id and bid_amount
        auction_service: Auction service instance

    Returns:
        Dict with status and resolution information

    Raises:
        NotFoundException: If player, participant, or auction queue item not found
        ValidationException: If bid amount exceeds budget or auction status is not valid
    """
    result = await auction_service.resolve_contested_player(
        player_id=player_id,
        winning_participant_id=winning_participant_id,
        auction_queue_id=request.auction_queue_id,
        bid_amount=request.bid_amount,
    )
    return AuctionResponseFactory.create_resolve_contested_player_response(result)


@router.post(
    "/revert/{player_id}/{winning_participant_id}",
    response_model=Dict[str, Any],
    summary="Revert an auction result",
    status_code=status.HTTP_200_OK,
)
@handle_exceptions
async def revert_auction(
    player_id: int = Path(..., description="ID of the player"),
    winning_participant_id: int = Path(
        ..., description="ID of the winning participant"
    ),
    request: RevertAuctionRequest = Body(..., description="Auction queue ID"),
    auction_service: AuctionService = Depends(get_auction_service),
):
    """
    Revert a previously assigned auctioned player, restoring the auction queue
    and refunding the bid amount.

    Args:
        player_id: ID of the player
        winning_participant_id: ID of the winning participant
        request: Request body with auction queue ID
        auction_service: Auction service instance

    Returns:
        Dict with status and message

    Raises:
        NotFoundException: If player, participant, or auction queue item not found
        ValidationException: If the player is not owned by the participant or gully is not in auction state
    """
    result = await auction_service.revert_auction(
        player_id=player_id,
        winning_participant_id=winning_participant_id,
        auction_queue_id=request.auction_queue_id,
    )
    return AuctionResponseFactory.create_revert_auction_response(result)


@router.post(
    "/participants/{participant_id}/release-players",
    response_model=Dict[str, Any],
    summary="Release players from a participant",
    status_code=status.HTTP_200_OK,
)
@handle_exceptions
async def release_players(
    participant_id: int = Path(..., description="ID of the participant"),
    request: ReleasePlayersRequest = Body(..., description="Release players request"),
    auction_service: AuctionService = Depends(get_auction_service),
):
    """
    Release players from a participant and add them to the auction queue.

    Args:
        participant_id: ID of the participant
        request: Release players request
        auction_service: Auction service

    Returns:
        Release players response
    """

    result = await auction_service.release_players(
        participant_id=participant_id,
        player_ids=request.player_ids,
    )

    return AuctionResponseFactory.create_release_players_response(result)
