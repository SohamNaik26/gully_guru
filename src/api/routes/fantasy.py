"""
Fantasy routes for the GullyGuru API.
This module provides API endpoints for fantasy-related operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from src.db.models.models import UserPlayerStatus
from src.db.session import get_session
from src.api.schemas.fantasy import (
    DraftPlayerCreate,
    DraftPlayerResponse,
    SubmissionStatusResponse,
    AuctionStartResponse,
    ContestPlayerResponse,
    SuccessResponse,
    SquadResponse,
    SubmitSquadResponse,
)
from src.api.services.fantasy import FantasyService
from src.api.factories.fantasy import (
    DraftPlayerResponseFactory,
    SubmissionStatusResponseFactory,
    AuctionStartResponseFactory,
    ContestPlayerResponseFactory,
    SquadResponseFactory,
)

router = APIRouter(
    prefix="/fantasy",
    tags=["fantasy"],
)


# Define the get_fantasy_service dependency
def get_fantasy_service(
    db: AsyncSession = Depends(get_session),
) -> FantasyService:
    """Get the fantasy service client."""
    return FantasyService(db)


# Squad Building Endpoints


@router.post(
    "/users/{user_id}/draft/players",
    response_model=DraftPlayerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_player_to_draft(
    user_id: int,
    player_data: DraftPlayerCreate,
    fantasy_service: FantasyService = Depends(get_fantasy_service),
):
    """
    Add a player to a user's draft squad.

    Args:
        user_id: User ID
        player_data: Player data including player_id and gully_id

    Returns:
        DraftPlayerResponse: Added draft player

    Raises:
        HTTPException: If player already in draft or other error occurs
    """
    try:
        draft_player = await fantasy_service.add_to_draft_squad(
            user_id=user_id,
            player_id=player_data.player_id,
            gully_id=player_data.gully_id,
        )
        return DraftPlayerResponseFactory.create_response(draft_player)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/users/{user_id}/draft/players/{player_id}",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
)
async def remove_player_from_draft(
    user_id: int,
    player_id: int,
    gully_id: int = Query(..., description="ID of the gully"),
    fantasy_service: FantasyService = Depends(get_fantasy_service),
):
    """
    Remove a player from a user's draft squad.

    Args:
        user_id: User ID
        player_id: Player ID to remove
        gully_id: Gully ID

    Returns:
        SuccessResponse: Success status

    Raises:
        HTTPException: If player not in draft or other error occurs
    """
    try:
        success = await fantasy_service.remove_from_draft_squad(
            user_id=user_id,
            player_id=player_id,
            gully_id=gully_id,
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found in draft squad",
            )
        return {"success": True, "message": "Player removed from draft squad"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/users/{user_id}/draft/squad",
    response_model=SquadResponse,
    status_code=status.HTTP_200_OK,
)
async def get_draft_squad(
    user_id: int,
    gully_id: int = Query(..., description="ID of the gully"),
    fantasy_service: FantasyService = Depends(get_fantasy_service),
):
    """
    Get a user's draft squad for a specific gully.

    Args:
        user_id: User ID
        gully_id: Gully ID

    Returns:
        SquadResponse: User's draft squad

    Raises:
        HTTPException: If user or gully not found
    """
    try:
        draft_squad = await fantasy_service.get_draft_squad(
            user_id=user_id,
            gully_id=gully_id,
        )
        return SquadResponseFactory.create_response(draft_squad)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/users/{user_id}/submit-squad",
    response_model=SubmitSquadResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_squad(
    user_id: int,
    gully_id: int = Query(..., description="ID of the gully"),
    fantasy_service: FantasyService = Depends(get_fantasy_service),
):
    """
    Submit a user's final squad for a gully.

    Args:
        user_id: User ID
        gully_id: Gully ID

    Returns:
        SubmitSquadResponse: Submission status

    Raises:
        HTTPException: If submission fails
    """
    try:
        await fantasy_service.submit_squad(
            user_id=user_id,
            gully_id=gully_id,
        )
        return {"success": True, "message": "Squad submitted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/users/{user_id}/players/{player_id}/status",
    response_model=DraftPlayerResponse,
    status_code=status.HTTP_200_OK,
)
async def update_player_status(
    user_id: int,
    player_id: int,
    status: UserPlayerStatus,
    gully_id: int = Query(..., description="ID of the gully"),
    fantasy_service: FantasyService = Depends(get_fantasy_service),
):
    """
    Update a player's status in a user's draft squad.

    Args:
        user_id: User ID
        player_id: Player ID
        status: New status for the player
        gully_id: Gully ID

    Returns:
        DraftPlayerResponse: Updated player status

    Raises:
        HTTPException: If update fails
    """
    try:
        updated_player = await fantasy_service.update_player_status(
            user_id=user_id,
            player_id=player_id,
            gully_id=gully_id,
            status=status,
        )
        return DraftPlayerResponseFactory.create_response(updated_player)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# Gully Management Endpoints


@router.get(
    "/gullies/{gully_id}/submission-status",
    response_model=SubmissionStatusResponse,
    status_code=status.HTTP_200_OK,
)
async def get_submission_status(
    gully_id: int,
    fantasy_service: FantasyService = Depends(get_fantasy_service),
):
    """
    Check submission status for a gully.

    Args:
        gully_id: Gully ID

    Returns:
        SubmissionStatusResponse: Submission status for the gully

    Raises:
        HTTPException: If gully not found
    """
    try:
        submission_status = await fantasy_service.get_submission_status(gully_id)
        return SubmissionStatusResponseFactory.create_response(submission_status)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/gullies/{gully_id}/start-auction",
    response_model=AuctionStartResponse,
    status_code=status.HTTP_200_OK,
)
async def start_auction(
    gully_id: int,
    fantasy_service: FantasyService = Depends(get_fantasy_service),
):
    """
    Start auction for a gully.

    Args:
        gully_id: Gully ID

    Returns:
        AuctionStartResponse: Auction start status

    Raises:
        HTTPException: If auction cannot be started
    """
    try:
        auction_start = await fantasy_service.start_auction(gully_id)
        return AuctionStartResponseFactory.create_response(auction_start)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/gullies/{gully_id}/contested-players",
    response_model=List[ContestPlayerResponse],
    status_code=status.HTTP_200_OK,
)
async def get_contested_players(
    gully_id: int,
    fantasy_service: FantasyService = Depends(get_fantasy_service),
):
    """
    Get contested players for a gully.

    Args:
        gully_id: Gully ID

    Returns:
        List[ContestPlayerResponse]: List of contested players

    Raises:
        HTTPException: If gully not found
    """
    try:
        contested_players = await fantasy_service.get_contested_players(gully_id)
        return [
            ContestPlayerResponseFactory.create_response(player)
            for player in contested_players
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/gullies/{gully_id}/uncontested-players",
    response_model=List[ContestPlayerResponse],
    status_code=status.HTTP_200_OK,
)
async def get_uncontested_players(
    gully_id: int,
    fantasy_service: FantasyService = Depends(get_fantasy_service),
):
    """
    Get uncontested players for a gully.

    Args:
        gully_id: Gully ID

    Returns:
        List[ContestPlayerResponse]: List of uncontested players

    Raises:
        HTTPException: If gully not found
    """
    try:
        uncontested_players = await fantasy_service.get_uncontested_players(gully_id)
        return [
            ContestPlayerResponseFactory.create_response(player)
            for player in uncontested_players
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/gullies/{gully_id}/status",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
)
async def update_gully_status(
    gully_id: int,
    status: str = Query(..., description="New status for the gully"),
    fantasy_service: FantasyService = Depends(get_fantasy_service),
):
    """
    Update a gully's status.

    Args:
        gully_id: Gully ID
        status: New status for the gully

    Returns:
        SuccessResponse: Success status

    Raises:
        HTTPException: If update fails
    """
    try:
        success = await fantasy_service.update_gully_status(
            gully_id=gully_id,
            status=status,
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Gully with ID {gully_id} not found",
            )
        return {"success": True, "message": f"Gully status updated to {status}"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/auction/{auction_queue_id}/status",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
)
async def update_auction_status(
    auction_queue_id: int,
    status: str = Query(..., description="New status for the auction"),
    gully_id: int = Query(..., description="ID of the gully"),
    fantasy_service: FantasyService = Depends(get_fantasy_service),
):
    """
    Update an auction's status.

    Args:
        auction_queue_id: Auction queue ID
        status: New status for the auction
        gully_id: Gully ID

    Returns:
        SuccessResponse: Success status

    Raises:
        HTTPException: If update fails
    """
    try:
        success = await fantasy_service.update_auction_status(
            auction_queue_id=auction_queue_id,
            status=status,
            gully_id=gully_id,
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Auction with ID {auction_queue_id} not found",
            )
        return {"success": True, "message": f"Auction status updated to {status}"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/gullies/{gully_id}/resolve-contested/{player_id}/{winner_participant_id}",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
)
async def resolve_contested_player(
    gully_id: int,
    player_id: int,
    winner_participant_id: int,
    fantasy_service: FantasyService = Depends(get_fantasy_service),
):
    """
    Resolve a contested player.

    Args:
        gully_id: Gully ID
        player_id: Player ID
        winner_participant_id: ID of the winning participant

    Returns:
        SuccessResponse: Success status

    Raises:
        HTTPException: If resolution fails
    """
    try:
        success = await fantasy_service.resolve_contested_player(
            gully_id=gully_id,
            player_id=player_id,
            winner_participant_id=winner_participant_id,
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Failed to resolve contested player",
            )
        return {"success": True, "message": "Contested player resolved successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/player-status/{participant_player_id}/{new_status}",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
)
async def update_participant_player_status(
    participant_player_id: int,
    new_status: UserPlayerStatus,
    fantasy_service: FantasyService = Depends(get_fantasy_service),
):
    """
    Update a participant player's status.

    Args:
        participant_player_id: Participant player ID
        new_status: New status for the participant player

    Returns:
        SuccessResponse: Success status

    Raises:
        HTTPException: If update fails
    """
    try:
        success = await fantasy_service.update_participant_player_status(
            participant_player_id=participant_player_id,
            new_status=new_status,
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Participant player with ID {participant_player_id} not found",
            )
        return {
            "success": True,
            "message": f"Participant player status updated to {new_status}",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
