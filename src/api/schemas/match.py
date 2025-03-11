"""
Schemas for match-related data.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


# Match API Models
class MatchBase(BaseModel):
    """Base model for match data."""

    match_id: str
    home_team: str
    away_team: str
    match_date: datetime
    venue: str
    match_type: str = "T20"  # T20, ODI, Test


class MatchCreate(MatchBase):
    """Create model for match data."""

    pass


class MatchResponse(MatchBase):
    """Response model for match data."""

    id: int
    created_at: datetime
    updated_at: datetime
    status: str = "scheduled"  # scheduled, live, completed, abandoned

    model_config = ConfigDict(from_attributes=True)


# Match Performance API Models
class MatchPerformanceResponse(BaseModel):
    """Response model for player performance in a match."""

    player_id: int
    player_name: str
    match_id: int
    runs_scored: int = 0
    balls_faced: int = 0
    fours: int = 0
    sixes: int = 0
    wickets_taken: int = 0
    overs_bowled: float = 0.0
    runs_conceded: int = 0
    catches: int = 0
    stumpings: int = 0
    run_outs: int = 0
    fantasy_points: float = 0.0

    model_config = ConfigDict(from_attributes=True)
