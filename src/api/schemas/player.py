"""
Schemas for player-related data.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal


# Player API Models
class PlayerBase(BaseModel):
    """Base schema for Player model."""

    name: str = Field(..., description="Player name")
    team: str = Field(..., description="Team name")
    player_type: str = Field(..., description="Player type (BAT, BOWL, ALL, WK)")
    base_price: Optional[Decimal] = Field(default=None, description="Player base price")
    sold_price: Optional[Decimal] = Field(default=None, description="Player sold price")
    season: int = Field(default=2025, description="IPL season year")


class PlayerCreate(PlayerBase):
    """Schema for creating a new player."""

    pass


class PlayerUpdate(BaseModel):
    """Schema for updating a player."""

    name: Optional[str] = Field(None, description="Player name")
    team: Optional[str] = Field(None, description="Team name")
    player_type: Optional[str] = Field(None, description="Player type")
    base_price: Optional[Decimal] = Field(None, description="Player base price")
    sold_price: Optional[Decimal] = Field(None, description="Player sold price")
    season: Optional[int] = Field(None, description="IPL season year")

    model_config = ConfigDict(extra="forbid")


class PlayerResponse(PlayerBase):
    """Schema for player response."""

    id: int = Field(..., description="Player ID")
    created_at: datetime = Field(..., description="When the player was created")
    updated_at: datetime = Field(..., description="When the player was last updated")

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
