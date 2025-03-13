from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.db.session import get_session
from src.db.models import Player
from src.api.schemas.player import PlayerCreate, PlayerResponse, PlayerStatsResponse
from src.api.dependencies import get_admin_user
from src.api.exceptions import NotFoundException
from src.api.factories import PlayerFactory
from src.api.services import PlayerServiceClient

router = APIRouter()


@router.post("/", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
async def create_player(
    player_data: PlayerCreate,
    session: AsyncSession = Depends(get_session),
    _: Player = Depends(get_admin_user),  # Only admins can create players
):
    """Create a new player (admin only)."""
    player_service = PlayerServiceClient(session)
    player = await player_service.create_player(player_data.dict())
    return PlayerFactory.create_response(player)


@router.get("/{player_id}", response_model=PlayerResponse)
async def get_player(player_id: int, session: AsyncSession = Depends(get_session)):
    """Get a player by ID."""
    player_service = PlayerServiceClient(session)
    player = await player_service.get_player(player_id)
    if not player:
        raise NotFoundException(resource_type="Player", resource_id=player_id)

    return PlayerFactory.create_response(player)


@router.get("/", response_model=List[PlayerResponse])
async def get_players(
    skip: int = 0,
    limit: int = 100,
    team: Optional[str] = None,
    player_type: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
):
    """Get all players with optional filtering."""
    player_service = PlayerServiceClient(session)
    players = await player_service.get_players(
        skip=skip, limit=limit, team=team, player_type=player_type
    )
    return [PlayerFactory.create_response(player) for player in players]


@router.get("/{player_id}/stats", response_model=PlayerStatsResponse)
async def get_player_stats(
    player_id: int, session: AsyncSession = Depends(get_session)
):
    """
    Get stats for a player.

    Args:
        player_id: The player ID
        session: Database session

    Returns:
        The player stats
    """
    player_service = PlayerServiceClient(session)
    stats = await player_service.get_player_stats(player_id)
    if not stats:
        raise NotFoundException(resource_type="Player", resource_id=player_id)

    return PlayerFactory.create_stats_response(stats)


@router.put("/{player_id}", response_model=PlayerResponse)
async def update_player(
    player_id: int,
    player_data: PlayerCreate,
    session: AsyncSession = Depends(get_session),
    _: Player = Depends(get_admin_user),  # Only admins can update players
):
    """Update a player (admin only)."""
    player_service = PlayerServiceClient(session)
    player = await player_service.update_player(player_id, player_data.dict())
    if not player:
        raise NotFoundException(resource_type="Player", resource_id=player_id)

    return PlayerFactory.create_response(player)


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_player(
    player_id: int,
    session: AsyncSession = Depends(get_session),
    _: Player = Depends(get_admin_user),  # Only admins can delete players
):
    """Delete a player (admin only)."""
    player_service = PlayerServiceClient(session)
    success = await player_service.delete_player(player_id)
    if not success:
        raise NotFoundException(resource_type="Player", resource_id=player_id)

    return None
