from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


# Match API Models
class MatchBase(BaseModel):
    """Base model for match data."""

    date: datetime
    venue: str
    team1: str
    team2: str


class MatchCreate(MatchBase):
    """Model for creating a new match."""

    pass


class MatchResponse(MatchBase):
    """Response model for match data."""

    id: int
    team1_score: Optional[str] = None
    team2_score: Optional[str] = None
    match_winner: Optional[str] = None
    player_of_the_match: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MatchPerformanceResponse(BaseModel):
    """Response model for player match performance."""

    id: int
    match_id: int
    player_id: int
    player_name: str  # Joined from Player
    runs: int
    balls_faced: int
    fours: int
    sixes: int
    wickets: int
    overs_bowled: float
    runs_conceded: int
    economy: float
    catches: int
    stumpings: int
    run_outs: int
    fantasy_points: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
