from fastapi import APIRouter, Depends, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.db.session import get_session
from src.db.models import Player, PlayerStats
from src.db.models.api import PlayerCreate, PlayerResponse, PlayerStatsResponse
from src.api.dependencies import get_admin_user
from src.api.exceptions import NotFoundException

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

    return player


@router.get("/{player_id}", response_model=PlayerResponse)
async def get_player(player_id: int, session: AsyncSession = Depends(get_session)):
    """Get a player by ID."""
    player = await session.get(Player, player_id)
    if not player:
        raise NotFoundException(resource_type="Player", resource_id=player_id)

    return player


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

    return players


@router.get("/{player_id}/stats", response_model=PlayerStatsResponse)
async def get_player_stats(
    player_id: int, session: AsyncSession = Depends(get_session)
):
    """Get stats for a player."""
    # Check if player exists
    player = await session.get(Player, player_id)
    if not player:
        raise NotFoundException(resource_type="Player", resource_id=player_id)

    # Get player stats
    result = await session.execute(
        select(PlayerStats).where(PlayerStats.player_id == player_id)
    )
    stats = result.scalars().first()

    if not stats:
        # Return empty stats if none exist
        return PlayerStatsResponse(
            player_id=player_id,
            matches_played=0,
            runs_scored=0,
            wickets_taken=0,
            catches=0,
            player=player,
        )

    return stats


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

    return player


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
