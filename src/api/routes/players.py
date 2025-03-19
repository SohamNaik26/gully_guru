"""
Player routes for the GullyGuru API.
This module provides API endpoints for player-related operations.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.player import (
    PlayerCreate,
    PlayerUpdate,
    PlayerResponse,
    PlayerStatsResponse,
)
from src.api.schemas.pagination import PaginatedResponse
from src.api.services.player import PlayerService
from src.api.factories.player import PlayerResponseFactory
from src.api.dependencies.database import get_db
from src.api.dependencies.pagination import pagination_params, PaginationParams
from src.api.dependencies.permissions import check_is_system_admin
from src.api.exceptions import NotFoundException, handle_exceptions

router = APIRouter(
    prefix="/players",
    tags=["Players"],
)


@router.post("/", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
@handle_exceptions
async def create_player(
    player_data: PlayerCreate,
    admin_user_id: int = Query(
        ..., description="ID of the admin user creating the player"
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new player.

    Args:
        player_data: Player data including name, team, role, etc.
        admin_user_id: ID of the admin user creating the player
        db: Database session
        _: Permission check dependency (hidden)

    Returns:
        PlayerResponse: Created player with ID

    Raises:
        AuthorizationException: If user is not an admin
    """
    player_service = PlayerService(db)
    player_dict = await player_service.create_player(player_data.dict())
    return PlayerResponseFactory.create_response(player_dict)


@router.get("/", response_model=PaginatedResponse[PlayerResponse])
@handle_exceptions
async def get_players(
    name: Optional[str] = Query(
        None, description="Filter by player name (partial match)"
    ),
    team: Optional[str] = Query(None, description="Filter by team"),
    player_type: Optional[str] = Query(
        None, description="Filter by player type (BAT, BOWL, ALL, WK)"
    ),
    pagination: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a paginated list of players with optional filtering.

    Args:
        name: Optional filter by player name (partial match)
        team: Optional filter by team
        player_type: Optional filter by player type (BAT, BOWL, ALL, WK)
        pagination: Pagination parameters
        db: Database session

    Returns:
        PaginatedResponse[PlayerResponse]: Paginated list of players
    """
    player_service = PlayerService(db)

    # Build filters
    filters = {}
    if name is not None:
        filters["name"] = name
    if team is not None:
        filters["team"] = team
    if player_type is not None:
        filters["player_type"] = player_type

    player_dicts, total = await player_service.get_players(
        pagination.limit, pagination.offset, filters
    )

    return {
        "items": [
            PlayerResponseFactory.create_response(player) for player in player_dicts
        ],
        "total": total,
        "limit": pagination.limit,
        "offset": pagination.offset,
    }


@router.get("/{player_id}", response_model=PlayerResponse)
@handle_exceptions
async def get_player(
    player_id: int = Path(..., description="ID of the player"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a player by ID.

    Args:
        player_id: Player ID
        db: Database session

    Returns:
        PlayerResponse: Player details

    Raises:
        NotFoundException: If player not found
    """
    player_service = PlayerService(db)

    player_dict = await player_service.get_player(player_id)
    if not player_dict:
        raise NotFoundException(resource_type="Player", resource_id=player_id)

    return PlayerResponseFactory.create_response(player_dict)


@router.put("/{player_id}", response_model=PlayerResponse)
@handle_exceptions
async def update_player(
    player_id: int = Path(..., description="ID of the player"),
    player_data: PlayerUpdate = None,
    admin_user_id: int = Query(
        ..., description="ID of the admin user updating the player"
    ),
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(lambda: check_is_system_admin(admin_user_id, db)),
):
    """
    Update a player by ID.

    Args:
        player_id: Player ID
        player_data: Player data to update
        admin_user_id: ID of the admin user updating the player
        db: Database session
        _: Permission check dependency (hidden)

    Returns:
        PlayerResponse: Updated player details

    Raises:
        NotFoundException: If player not found
        AuthorizationException: If user is not an admin
    """
    player_service = PlayerService(db)
    player_dict = await player_service.update_player(
        player_id, player_data.dict(exclude_unset=True)
    )
    if not player_dict:
        raise NotFoundException(resource_type="Player", resource_id=player_id)

    return PlayerResponseFactory.create_response(player_dict)


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_exceptions
async def delete_player(
    player_id: int = Path(..., description="ID of the player"),
    admin_user_id: int = Query(
        ..., description="ID of the admin user deleting the player"
    ),
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(lambda: check_is_system_admin(admin_user_id, db)),
):
    """
    Delete a player by ID.

    Args:
        player_id: Player ID
        admin_user_id: ID of the admin user deleting the player
        db: Database session
        _: Permission check dependency (hidden)

    Returns:
        None

    Raises:
        NotFoundException: If player not found
        AuthorizationException: If user is not an admin
    """
    player_service = PlayerService(db)

    deleted = await player_service.delete_player(player_id)
    if not deleted:
        raise NotFoundException(resource_type="Player", resource_id=player_id)

    return None


@router.get("/{player_id}/stats", response_model=PlayerStatsResponse)
async def get_player_stats(
    player_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get statistics for a player.

    Args:
        player_id: Player ID

    Returns:
        PlayerStatsResponse: Player statistics

    Raises:
        NotFoundException: If player not found
    """
    player_service = PlayerService(db)

    # Check if player exists
    player = await player_service.get_player(player_id)
    if not player:
        raise NotFoundException(resource_type="Player", resource_id=player_id)

    # Get player stats
    stats = await player_service.get_player_stats(player_id)

    return stats
