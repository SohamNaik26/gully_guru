"""
DEPRECATED: API models have been moved to src/api/schemas/

This file contains the old API models and should not be used for new development.
The Pydantic API models have been moved to:
- src/api/schemas/user.py
- src/api/schemas/player.py
- src/api/schemas/match.py
- src/api/schemas/game.py

The External API Integration Models at the bottom of this file are still here
but are not currently used in the database.
"""

from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_validator

from src.db.models.models import TimeStampedModel
from src.db.models.base import validate_non_negative, validate_status


# User API Models
class UserBase(SQLModel):
    """Base model for user data."""

    telegram_id: int
    username: str
    full_name: str
    budget: Decimal = Decimal("100.0")
    total_points: float = 0.0
    is_admin: bool = False
    free_bids_used: int = 0


class UserCreate(UserBase):
    """Model for creating a new user."""

    pass


class UserResponse(UserBase):
    """Response model for user data."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Player API Models
class PlayerBase(SQLModel):
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
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlayerResponse(PlayerBase):
    """Response model for player data."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Match API Models
class MatchBase(SQLModel):
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

    class Config:
        from_attributes = True


# Stats API Models
class PlayerStatsResponse(SQLModel):
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

    class Config:
        from_attributes = True


class MatchPerformanceResponse(SQLModel):
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

    class Config:
        from_attributes = True


# Game Mechanics API Models
class UserSquadResponse(SQLModel):
    """Response model for user squad data."""

    user_id: int
    username: str  # Joined from User
    players: List[PlayerResponse]
    captain: Optional[PlayerResponse] = None
    vice_captain: Optional[PlayerResponse] = None
    total_points: float

    class Config:
        from_attributes = True


class AuctionBidCreate(SQLModel):
    """Model for creating a new auction bid."""

    player_id: int
    bid_amount: Decimal

    @field_validator("bid_amount")
    @classmethod
    def validate_bid_amount(cls, v):
        return validate_non_negative(v)


class AuctionBidResponse(SQLModel):
    """Response model for auction bid data."""

    id: int
    user_id: int
    username: str  # Joined from User
    player_id: int
    player_name: str  # Joined from Player
    auction_round_id: int
    bid_amount: Decimal
    status: str
    created_at: datetime
    updated_at: datetime

    @field_validator("status")
    @classmethod
    def validate_bid_status(cls, v):
        valid_statuses = ["pending", "accepted", "rejected"]
        return validate_status(v, valid_statuses)

    class Config:
        from_attributes = True


# Leaderboard API Models
class LeaderboardEntry(SQLModel):
    """Entry in the leaderboard."""

    rank: int
    user_id: int
    username: str
    total_points: float

    class Config:
        from_attributes = True


class LeaderboardResponse(SQLModel):
    """Response model for leaderboard data."""

    leaderboard: List[LeaderboardEntry]
    total_users: int
    updated_at: datetime


# UserPlayer API Models
class UserPlayerBase(SQLModel):
    user_id: int
    player_id: int
    gully_id: int
    purchase_price: Decimal
    purchase_date: datetime


class UserPlayerCreate(UserPlayerBase):
    pass


class UserPlayerRead(UserPlayerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserPlayerWithDetails(UserPlayerRead):
    player: PlayerRead

    class Config:
        from_attributes = True


class UserWithPlayers(UserResponse):
    owned_players: List[UserPlayerWithDetails] = []

    class Config:
        from_attributes = True


# External API Integration Models
# NOTE: These models are currently not used in the database. They are kept here for future reference
# and potential future use. They have been removed from the all_models list in __init__.py to prevent
# table creation in PostgreSQL. If needed in the future, uncomment them in __init__.py.
class ApiTeam(TimeStampedModel, table=True):
    """Model for cricket teams from external APIs."""

    __tablename__ = "api_teams"

    id: Optional[int] = Field(default=None, primary_key=True)
    api_id: str = Field(index=True)
    name: str = Field(index=True)
    short_name: str
    logo_url: Optional[str] = Field(default=None)

    # Relationships
    players: List["ApiPlayer"] = Relationship(back_populates="team")
    home_matches: List["ApiMatch"] = Relationship(
        back_populates="home_team",
        sa_relationship_kwargs={"foreign_keys": "ApiMatch.home_team_id"},
    )
    away_matches: List["ApiMatch"] = Relationship(
        back_populates="away_team",
        sa_relationship_kwargs={"foreign_keys": "ApiMatch.away_team_id"},
    )


class ApiPlayer(TimeStampedModel, table=True):
    """Model for cricket players from external APIs."""

    __tablename__ = "api_players"

    id: Optional[int] = Field(default=None, primary_key=True)
    api_id: str = Field(index=True)
    name: str = Field(index=True)
    team_id: Optional[int] = Field(default=None, foreign_key="api_teams.id")
    role: str  # batsman, bowler, all-rounder, wicket-keeper
    batting_style: Optional[str] = Field(default=None)
    bowling_style: Optional[str] = Field(default=None)
    image_url: Optional[str] = Field(default=None)

    # Relationships
    team: Optional[ApiTeam] = Relationship(back_populates="players")
    stats: List["ApiPlayerStats"] = Relationship(back_populates="player")


class ApiMatch(TimeStampedModel, table=True):
    """Model for cricket matches from external APIs."""

    __tablename__ = "api_matches"

    id: Optional[int] = Field(default=None, primary_key=True)
    api_id: str = Field(index=True)
    home_team_id: int = Field(foreign_key="api_teams.id")
    away_team_id: int = Field(foreign_key="api_teams.id")
    venue: str
    date: datetime = Field(index=True)
    format: str  # T20, ODI, Test
    status: str  # scheduled, live, completed, cancelled
    result: Optional[str] = Field(default=None)

    # Relationships
    home_team: ApiTeam = Relationship(
        back_populates="home_matches",
        sa_relationship_kwargs={"foreign_keys": "ApiMatch.home_team_id"},
    )
    away_team: ApiTeam = Relationship(
        back_populates="away_matches",
        sa_relationship_kwargs={"foreign_keys": "ApiMatch.away_team_id"},
    )
    player_stats: List["ApiPlayerStats"] = Relationship(back_populates="match")


class ApiPlayerStats(TimeStampedModel, table=True):
    """Model for player statistics from external APIs."""

    __tablename__ = "api_player_stats"

    id: Optional[int] = Field(default=None, primary_key=True)
    player_id: int = Field(foreign_key="api_players.id")
    match_id: int = Field(foreign_key="api_matches.id")

    # Batting stats
    runs: int = Field(default=0)
    balls_faced: int = Field(default=0)
    fours: int = Field(default=0)
    sixes: int = Field(default=0)
    strike_rate: float = Field(default=0.0)

    # Bowling stats
    overs: float = Field(default=0.0)
    maidens: int = Field(default=0)
    runs_conceded: int = Field(default=0)
    wickets: int = Field(default=0)
    economy: float = Field(default=0.0)

    # Fielding stats
    catches: int = Field(default=0)
    stumpings: int = Field(default=0)
    run_outs: int = Field(default=0)

    # Fantasy points
    fantasy_points: float = Field(default=0.0)

    # Relationships
    player: "ApiPlayer" = Relationship(back_populates="stats")
    match: "ApiMatch" = Relationship(back_populates="player_stats")

    @field_validator(
        "runs",
        "balls_faced",
        "fours",
        "sixes",
        "maidens",
        "runs_conceded",
        "wickets",
        "catches",
        "stumpings",
        "run_outs",
    )
    @classmethod
    def validate_non_negative_stats(cls, v):
        return validate_non_negative(v)
