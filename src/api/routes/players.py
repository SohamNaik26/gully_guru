from fastapi import APIRouter, Depends, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from src.db.session import get_session
from src.db.models import Player
from src.api.schemas.player import PlayerCreate, PlayerResponse, PlayerStatsResponse
from src.api.dependencies import get_admin_user
from src.api.exceptions import NotFoundException
from src.api.factories import PlayerFactory

router = APIRouter()


@router.post("/", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
async def create_player(
    player_data: PlayerCreate,
    session: AsyncSession = Depends(get_session),
    _: Player = Depends(get_admin_user),  # Only admins can create players
):
    """Create a new player (admin only)."""
    player = Player(**player_data.dict())
    session.add(player)
    await session.commit()
    await session.refresh(player)

    return PlayerFactory.create_response(player)


@router.get("/{player_id}", response_model=PlayerResponse)
async def get_player(player_id: int, session: AsyncSession = Depends(get_session)):
    """Get a player by ID."""
    player = await session.get(Player, player_id)
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
    query = select(Player)

    # Apply filters if provided
    if team:
        query = query.where(Player.team == team)
    if player_type:
        query = query.where(Player.player_type == player_type)

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute query
    result = await session.execute(query)
    players = result.scalars().all()

    return PlayerFactory.create_response_list(players)


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
    # First check if the player exists
    player = await session.get(Player, player_id)
    if not player:
        raise NotFoundException(f"Player with ID {player_id} not found")

    # For now, return mock stats since PlayerStats model has been removed
    return PlayerStatsResponse(
        id=1,  # Mock ID for stats
        player_id=player_id,
        player_name=player.name,
        matches_played=0,
        runs=0,
        wickets=0,
        highest_score=0,
        best_bowling="0/0",
        fantasy_points=0.0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@router.put("/{player_id}", response_model=PlayerResponse)
async def update_player(
    player_id: int,
    player_data: PlayerCreate,
    session: AsyncSession = Depends(get_session),
    _: Player = Depends(get_admin_user),  # Only admins can update players
):
    """Update a player (admin only)."""
    player = await session.get(Player, player_id)
    if not player:
        raise NotFoundException(resource_type="Player", resource_id=player_id)

    # Update player attributes
    for key, value in player_data.dict().items():
        setattr(player, key, value)

    session.add(player)
    await session.commit()
    await session.refresh(player)

    return PlayerFactory.create_response(player)


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_player(
    player_id: int,
    session: AsyncSession = Depends(get_session),
    _: Player = Depends(get_admin_user),  # Only admins can delete players
):
    """Delete a player (admin only)."""
    player = await session.get(Player, player_id)
    if not player:
        raise NotFoundException(resource_type="Player", resource_id=player_id)

    await session.delete(player)
    await session.commit()

    return None
