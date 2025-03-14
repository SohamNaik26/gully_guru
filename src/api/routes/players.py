"""
Player routes for the GullyGuru API.
This module provides API endpoints for player-related operations.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
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
from src.db.session import get_session
from src.api.exceptions import NotFoundException

router = APIRouter(
    prefix="/players",
    tags=["Players"],
)


@router.post("/", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
async def create_player(
    player_data: PlayerCreate,
    admin_user_id: int = Query(
        ..., description="ID of the admin user creating the player"
    ),
    db: AsyncSession = Depends(get_session),
):
    """
    Create a new player.

    Args:
        player_data: Player data including name, team, role, etc.
        admin_user_id: ID of the admin user creating the player

    Returns:
        PlayerResponse: Created player with ID

    Raises:
        HTTPException: If player creation fails or user is not an admin
    """
    player_service = PlayerService(db)

    # Check if user is an admin (this would be implemented in the service)
    is_admin = await player_service.is_system_admin(admin_user_id)
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create players",
        )

    try:
        player_dict = await player_service.create_player(player_data.dict())
        return PlayerResponseFactory.create_response(player_dict)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=PaginatedResponse[PlayerResponse])
async def get_players(
    name: Optional[str] = Query(
        None, description="Filter by player name (partial match)"
    ),
    team: Optional[str] = Query(None, description="Filter by team"),
    player_type: Optional[str] = Query(
        None, description="Filter by player type (BAT, BOWL, ALL, WK)"
    ),
    limit: int = Query(
        10, ge=1, le=100, description="Maximum number of players to return"
    ),
    offset: int = Query(0, ge=0, description="Number of players to skip"),
    db: AsyncSession = Depends(get_session),
):
    """
    Get a paginated list of players with optional filtering.

    Args:
        name: Optional filter by player name (partial match)
        team: Optional filter by team
        player_type: Optional filter by player type (BAT, BOWL, ALL, WK)
        limit: Maximum number of players to return
        offset: Number of players to skip

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

    player_dicts, total = await player_service.get_players(limit, offset, filters)

    return {
        "items": [
            PlayerResponseFactory.create_response(player) for player in player_dicts
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{player_id}", response_model=PlayerResponse)
async def get_player(
    player_id: int,
    db: AsyncSession = Depends(get_session),
):
    """
    Get a player by ID.

    Args:
        player_id: Player ID

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
async def update_player(
    player_id: int,
    player_data: PlayerUpdate,
    admin_user_id: int = Query(
        ..., description="ID of the admin user updating the player"
    ),
    db: AsyncSession = Depends(get_session),
):
    """
    Update a player by ID.

    Args:
        player_id: Player ID
        player_data: Player data to update
        admin_user_id: ID of the admin user updating the player

    Returns:
        PlayerResponse: Updated player details

    Raises:
        NotFoundException: If player not found
        HTTPException: If update fails or user is not an admin
    """
    player_service = PlayerService(db)

    # Check if user is an admin
    is_admin = await player_service.is_system_admin(admin_user_id)
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update players",
        )

    try:
        player_dict = await player_service.update_player(
            player_id, player_data.dict(exclude_unset=True)
        )
        if not player_dict:
            raise NotFoundException(resource_type="Player", resource_id=player_id)

        return PlayerResponseFactory.create_response(player_dict)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_player(
    player_id: int,
    admin_user_id: int = Query(
        ..., description="ID of the admin user deleting the player"
    ),
    db: AsyncSession = Depends(get_session),
):
    """
    Delete a player by ID.

    Args:
        player_id: Player ID
        admin_user_id: ID of the admin user deleting the player

    Returns:
        None

    Raises:
        NotFoundException: If player not found
        HTTPException: If deletion fails or user is not an admin
    """
    player_service = PlayerService(db)

    # Check if user is an admin
    is_admin = await player_service.is_system_admin(admin_user_id)
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete players",
        )

    deleted = await player_service.delete_player(player_id)
    if not deleted:
        raise NotFoundException(resource_type="Player", resource_id=player_id)

    return None


@router.get("/{player_id}/stats", response_model=PlayerStatsResponse)
async def get_player_stats(
    player_id: int,
    db: AsyncSession = Depends(get_session),
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
