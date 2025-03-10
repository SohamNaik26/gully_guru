from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


# Player API Models
class PlayerBase(BaseModel):
    """Base model for player data."""

    name: str
    team: str
    player_type: str  # BAT, BOWL, ALL, WK
    base_price: Optional[Decimal] = None
    sold_price: Optional[Decimal] = None
    season: int = 2025


class PlayerCreate(PlayerBase):
    """Model for creating a new player."""

    pass


class PlayerRead(PlayerBase):
    """Model for reading player data."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlayerResponse(PlayerBase):
    """Response model for player data."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Stats API Models
class PlayerStatsResponse(BaseModel):
    """Response model for player statistics."""

    id: int
    player_id: int
    player_name: str  # Joined from Player
    matches_played: int
    runs: int
    wickets: int
    highest_score: int
    best_bowling: str
    fantasy_points: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
