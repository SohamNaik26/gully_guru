"""
Player schemas for the GullyGuru API.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum


class PlayerType(str, Enum):
    """Enum for player types."""

    BAT = "BAT"
    BOWL = "BOWL"
    AR = "AR"
    WK = "WK"


class PlayerBase(BaseModel):
    """Base model for player data."""

    name: str = Field(..., description="Name of the player")
    team: str = Field(..., description="Team of the player")
    player_type: PlayerType = Field(..., description="Type of player (BAT, BOWL, AR)")
    base_price: float = Field(..., ge=0, description="Base price of the player")
    season: int = Field(..., ge=2000, le=2100, description="Season year")


class PlayerCreate(PlayerBase):
    """Model for creating a new player."""

    sold_price: Optional[float] = Field(
        None, ge=0, description="Sold price of the player"
    )


class PlayerUpdate(BaseModel):
    """Model for updating a player."""

    name: Optional[str] = Field(None, description="Name of the player")
    team: Optional[str] = Field(None, description="Team of the player")
    player_type: Optional[PlayerType] = Field(
        None, description="Type of player (BAT, BOWL, AR)"
    )
    base_price: Optional[float] = Field(
        None, ge=0, description="Base price of the player"
    )
    sold_price: Optional[float] = Field(
        None, ge=0, description="Sold price of the player"
    )
    season: Optional[int] = Field(None, ge=2000, le=2100, description="Season year")


class PlayerResponse(PlayerBase):
    """Model for player response."""

    id: int = Field(..., description="ID of the player")
    sold_price: Optional[float] = Field(
        None, ge=0, description="Sold price of the player"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class PlayerStatsResponse(BaseModel):
    """Model for player statistics response."""

    player_id: int = Field(..., description="ID of the player")
    name: str = Field(..., description="Name of the player")
    team: str = Field(..., description="Team of the player")
    player_type: PlayerType = Field(..., description="Type of player")
    matches_played: int = Field(..., ge=0, description="Number of matches played")
    runs_scored: int = Field(..., ge=0, description="Number of runs scored")
    wickets_taken: int = Field(..., ge=0, description="Number of wickets taken")
    average: float = Field(..., ge=0, description="Batting/bowling average")
    strike_rate: float = Field(..., ge=0, description="Strike rate")
    economy: Optional[float] = Field(
        None, ge=0, description="Economy rate (for bowlers)"
    )

    model_config = ConfigDict(from_attributes=True)
