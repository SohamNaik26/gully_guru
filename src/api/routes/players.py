from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session, select
from typing import List, Optional

from src.db.session import get_session
from src.db.models import Player, PlayerStats
from src.models.api import PlayerCreate, PlayerResponse, PlayerStatsResponse
from src.api.dependencies import get_admin_user
from src.api.exceptions import NotFoundException

router = APIRouter()


@router.post("/", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
def create_player(
    player_data: PlayerCreate,
    session: Session = Depends(get_session),
    _: Player = Depends(get_admin_user),  # Only admins can create players
):
    """Create a new player (admin only)."""
    player = Player(**player_data.dict())
    session.add(player)
    session.commit()
    session.refresh(player)

    return player


@router.get("/{player_id}", response_model=PlayerResponse)
def get_player(player_id: int, session: Session = Depends(get_session)):
    """Get a player by ID."""
    player = session.get(Player, player_id)
    if not player:
        raise NotFoundException(resource_type="Player", resource_id=player_id)

    return player


@router.get("/", response_model=List[PlayerResponse])
def get_players(
    skip: int = 0,
    limit: int = 100,
    team: Optional[str] = None,
    player_type: Optional[str] = None,
    session: Session = Depends(get_session),
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

    players = session.exec(query).all()
    return players


@router.get("/{player_id}/stats", response_model=PlayerStatsResponse)
def get_player_stats(player_id: int, session: Session = Depends(get_session)):
    """Get statistics for a player."""
    # Check if player exists
    player = session.get(Player, player_id)
    if not player:
        raise NotFoundException(resource_type="Player", resource_id=player_id)

    # Get player stats
    stats = session.exec(
        select(PlayerStats).where(PlayerStats.player_id == player_id)
    ).first()

    if not stats:
        raise NotFoundException(resource_type="PlayerStats", resource_id=player_id)

    # Combine player name with stats for response
    stats_dict = stats.dict()
    stats_dict["player_name"] = player.name

    return stats_dict


@router.put("/{player_id}", response_model=PlayerResponse)
def update_player(
    player_id: int,
    player_data: PlayerCreate,
    session: Session = Depends(get_session),
    _: Player = Depends(get_admin_user),  # Only admins can update players
):
    """Update a player (admin only)."""
    player = session.get(Player, player_id)
    if not player:
        raise NotFoundException(resource_type="Player", resource_id=player_id)

    # Update player attributes
    for key, value in player_data.dict().items():
        setattr(player, key, value)

    session.add(player)
    session.commit()
    session.refresh(player)

    return player


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_player(
    player_id: int,
    session: Session = Depends(get_session),
    _: Player = Depends(get_admin_user),  # Only admins can delete players
):
    """Delete a player (admin only)."""
    player = session.get(Player, player_id)
    if not player:
        raise NotFoundException(resource_type="Player", resource_id=player_id)

    session.delete(player)
    session.commit()

    return None
