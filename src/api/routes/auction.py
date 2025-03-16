"""
Auction routes for the GullyGuru API.
This module provides API endpoints for auction-related operations.
"""

import logging
from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional

from src.api.dependencies.database import get_db
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
from src.api.exceptions import handle_exceptions, NotFoundException

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
    response_model=AuctionStartResponse,
    summary="Start auction for a gully",
    status_code=status.HTTP_200_OK,
)
@handle_exceptions
async def start_auction(
    gully_id: int = Path(..., description="ID of the gully"),
    auction_service: AuctionService = Depends(get_auction_service),
):
    """
    Start auction for a gully.

    Args:
        gully_id: Gully ID
        auction_service: Auction service instance

    Returns:
        AuctionStartResponse: Auction start status

    Raises:
        ValidationException: If auction cannot be started
    """
    auction_start = await auction_service.start_auction(gully_id)
    return AuctionStartResponseFactory.create_response(auction_start)


@router.post(
    "/gullies/{gully_id}/mark-contested",
    summary="Mark contested players in a gully",
    status_code=status.HTTP_200_OK,
)
@handle_exceptions
async def mark_contested_players(
    gully_id: int = Path(..., description="ID of the gully"),
    auction_service: AuctionService = Depends(get_auction_service),
):
    """
    Mark players as contested if they are selected by multiple users.

    Args:
        gully_id: ID of the gully
        auction_service: Auction service instance

    Returns:
        Result with counts of contested and uncontested players

    Raises:
        ValidationException: If marking contested players fails
    """
    result = await auction_service.mark_contested_players(gully_id)
    return result


@router.get(
    "/gullies/{gully_id}/contested-players",
    response_model=List[ContestPlayerResponse],
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
        List[ContestPlayerResponse]: List of contested players

    Raises:
        NotFoundException: If gully not found
    """
    contested_players = await auction_service.get_contested_players(gully_id)
    return [
        ContestPlayerResponseFactory.create_response(player)
        for player in contested_players
    ]


@router.get(
    "/gullies/{gully_id}/uncontested-players",
    response_model=List[ContestPlayerResponse],
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
        List[ContestPlayerResponse]: List of uncontested players

    Raises:
        NotFoundException: If gully not found
    """
    uncontested_players = await auction_service.get_uncontested_players(gully_id)
    return [
        ContestPlayerResponseFactory.create_response(player)
        for player in uncontested_players
    ]


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


@router.post(
    "/resolve-contested/{player_id}/{winning_participant_id}",
    summary="Resolve a contested player",
    status_code=status.HTTP_200_OK,
)
@handle_exceptions
async def resolve_contested_player(
    player_id: int = Path(..., description="ID of the player"),
    winning_participant_id: int = Path(
        ..., description="ID of the winning participant"
    ),
    auction_service: AuctionService = Depends(get_auction_service),
):
    """
    Resolve a contested player by assigning it to the winning participant.

    Args:
        player_id: ID of the player
        winning_participant_id: ID of the winning participant
        auction_service: Auction service instance

    Returns:
        Updated player data
    """
    result = await auction_service.resolve_contested_player(
        player_id, winning_participant_id
    )
    return result
