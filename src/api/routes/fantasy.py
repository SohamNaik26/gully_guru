"""
Fantasy routes for the GullyGuru API.
This module provides API endpoints for fantasy-related operations.
"""

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.database import get_db
from src.api.schemas.fantasy import (
    SquadResponse,
    BulkPlayerAddRequest,
    BulkPlayerRemoveRequest,
    BulkDraftPlayerResponse,
)
from src.api.services.fantasy import FantasyService
from src.api.factories.fantasy import (
    SquadResponseFactory,
    BulkDraftPlayerResponseFactory,
)
from src.api.exceptions import handle_exceptions, NotFoundException

router = APIRouter(
    prefix="/fantasy",
    tags=["fantasy"],
)


# Define the get_fantasy_service dependency
def get_fantasy_service(
    db: AsyncSession = Depends(get_db),
) -> FantasyService:
    """
    Get the fantasy service client.

    Args:
        db: Database session

    Returns:
        FantasyService instance
    """
    return FantasyService(db)


# Squad Building Endpoints - Participant-based


@router.get(
    "/draft-squad/{participant_id}",
    response_model=SquadResponse,
    summary="Get a participant's draft squad",
)
@handle_exceptions
async def get_draft_squad(
    participant_id: int = Path(..., description="ID of the participant"),
    fantasy_service: FantasyService = Depends(get_fantasy_service),
):
    """
    Get a participant's draft squad.

    Args:
        participant_id: ID of the participant
        fantasy_service: Fantasy service instance

    Returns:
        Squad data with players

    Raises:
        NotFoundException: If participant not found
    """
    try:
        squad = await fantasy_service.get_draft_squad(participant_id)
        return SquadResponseFactory.create_response(squad)
    except ValueError:
        raise NotFoundException(resource_type="Participant", resource_id=participant_id)


@router.post(
    "/draft-squad/{participant_id}/add",
    response_model=BulkDraftPlayerResponse,
    summary="Add players to a participant's draft squad",
)
@handle_exceptions
async def add_players_to_draft(
    request: BulkPlayerAddRequest,
    participant_id: int = Path(..., description="ID of the participant"),
    fantasy_service: FantasyService = Depends(get_fantasy_service),
):
    """
    Add multiple players to a participant's draft squad.

    Args:
        request: Request with player IDs to add
        participant_id: ID of the participant
        fantasy_service: Fantasy service instance

    Returns:
        Result of the operation

    Raises:
        ValidationException: If request is invalid
    """
    result = await fantasy_service.bulk_add_players_to_draft(
        participant_id, request.player_ids
    )
    return BulkDraftPlayerResponseFactory.create_response(result)


@router.post(
    "/draft-squad/{participant_id}/remove",
    response_model=BulkDraftPlayerResponse,
    summary="Remove players from a participant's draft squad",
)
@handle_exceptions
async def remove_players_from_draft(
    request: BulkPlayerRemoveRequest,
    participant_id: int = Path(..., description="ID of the participant"),
    fantasy_service: FantasyService = Depends(get_fantasy_service),
):
    """
    Remove multiple players from a participant's draft squad.

    Args:
        request: Request with player IDs to remove
        participant_id: ID of the participant
        fantasy_service: Fantasy service instance

    Returns:
        Result of the operation

    Raises:
        ValidationException: If request is invalid
    """
    result = await fantasy_service.bulk_remove_players_from_draft(
        participant_id, request.player_ids
    )
    return BulkDraftPlayerResponseFactory.create_response(result)


@router.put(
    "/draft-squad/{participant_id}",
    response_model=BulkDraftPlayerResponse,
    summary="Update a participant's entire draft squad",
)
@handle_exceptions
async def update_draft_squad(
    request: BulkPlayerAddRequest,
    participant_id: int = Path(..., description="ID of the participant"),
    fantasy_service: FantasyService = Depends(get_fantasy_service),
):
    """
    Update a participant's entire draft squad by replacing all players.

    This endpoint removes all existing draft selections and adds the new ones.

    Args:
        request: Request with player IDs for the updated squad
        participant_id: ID of the participant
        fantasy_service: Fantasy service instance

    Returns:
        Result of the operation

    Raises:
        ValidationException: If request is invalid
    """
    result = await fantasy_service.update_draft_squad(
        participant_id, request.player_ids
    )
    return BulkDraftPlayerResponseFactory.create_response(result)
