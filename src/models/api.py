from datetime import datetime
from typing import List, Optional, Dict, Any
from decimal import Decimal

from pydantic import BaseModel, Field, validator

from src.models.base import TimeStampedBase, validate_non_negative, validate_status


# User API Models
class UserBase(BaseModel):
    """Base model for user data."""
    telegram_id: int
    username: str
    full_name: str


class UserCreate(UserBase):
    """Model for creating a new user."""
    pass


class UserResponse(UserBase, TimeStampedBase):
    """Response model for user data."""
    id: int
    budget: Decimal
    total_points: float

    @validator("budget", "total_points")
    def validate_non_negative_values(cls, v):
        return validate_non_negative(v)


# Player API Models
class PlayerBase(BaseModel):
    """Base model for player data."""
    name: str
    team: str
    player_type: str  # BAT, BOWL, ALL, WK
    base_price: Optional[Decimal] = None


class PlayerCreate(PlayerBase):
    """Model for creating a new player."""
    pass


class PlayerResponse(PlayerBase, TimeStampedBase):
    """Response model for player data."""
    id: int
    sold_price: Optional[Decimal] = None


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


class MatchResponse(MatchBase, TimeStampedBase):
    """Response model for match data."""
    id: int
    team1_score: Optional[str] = None
    team2_score: Optional[str] = None
    match_winner: Optional[str] = None
    player_of_the_match: Optional[str] = None


# Stats API Models
class PlayerStatsResponse(TimeStampedBase):
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


class MatchPerformanceResponse(TimeStampedBase):
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


# Game Mechanics API Models
class UserSquadResponse(BaseModel):
    """Response model for user squad data."""
    user_id: int
    username: str  # Joined from User
    players: List[PlayerResponse]
    captain: Optional[PlayerResponse] = None
    vice_captain: Optional[PlayerResponse] = None
    total_points: float

    class Config:
        from_attributes = True


class AuctionBidCreate(BaseModel):
    """Model for creating a new auction bid."""
    player_id: int
    bid_amount: Decimal

    @validator("bid_amount")
    def validate_bid_amount(cls, v):
        return validate_non_negative(v)


class AuctionBidResponse(TimeStampedBase):
    """Response model for auction bid data."""
    id: int
    user_id: int
    username: str  # Joined from User
    player_id: int
    player_name: str  # Joined from Player
    auction_round_id: int
    bid_amount: Decimal
    status: str

    @validator("status")
    def validate_bid_status(cls, v):
        valid_statuses = ["pending", "accepted", "rejected"]
        return validate_status(v, valid_statuses)


# Leaderboard API Models
class LeaderboardEntry(BaseModel):
    """Entry in the leaderboard."""
    rank: int
    user_id: int
    username: str
    total_points: float

    class Config:
        from_attributes = True


class LeaderboardResponse(BaseModel):
    """Response model for leaderboard data."""
    leaderboard: List[LeaderboardEntry]
    total_users: int
    updated_at: datetime 