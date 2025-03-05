from datetime import datetime
from typing import List, Optional, Union, Dict, Any
from decimal import Decimal

from pydantic import BaseModel, Field, validator
from sqlmodel import Field as SQLModelField, Relationship, SQLModel


# Base Models
class TimeStampedModel(SQLModel):
    """Base model with created and updated timestamps."""
    created_at: datetime = SQLModelField(default_factory=datetime.utcnow)
    updated_at: datetime = SQLModelField(default_factory=datetime.utcnow)


# Link Tables
class UserPlayerLink(SQLModel, table=True):
    """Link table for users and their selected players."""
    __tablename__ = "user_player_links"
    
    id: Optional[int] = SQLModelField(default=None, primary_key=True)
    user_id: int = SQLModelField(foreign_key="users.id")
    player_id: int = SQLModelField(foreign_key="players.id")
    is_captain: bool = SQLModelField(default=False)
    is_vice_captain: bool = SQLModelField(default=False)
    is_playing_xi: bool = SQLModelField(default=False)
    round_number: int = SQLModelField(default=0)
    
    # Relationships
    user: "User" = Relationship(back_populates="player_links")
    player: "Player" = Relationship(back_populates="user_links")


# Main Models
class User(TimeStampedModel, table=True):
    """User model for fantasy cricket managers."""
    __tablename__ = "users"
    
    id: Optional[int] = SQLModelField(default=None, primary_key=True)
    telegram_id: int = SQLModelField(unique=True, index=True)
    username: str = SQLModelField(index=True)
    full_name: str
    budget: Decimal = SQLModelField(default=100.0)
    total_points: float = SQLModelField(default=0.0)
    
    # Relationships
    player_links: List["UserPlayerLink"] = Relationship(back_populates="user")
    bids: List["AuctionBid"] = Relationship(back_populates="user")
    
    @validator("budget")
    def validate_budget(cls, v):
        if v < 0:
            raise ValueError("Budget cannot be negative")
        return v


class Player(TimeStampedModel, table=True):
    """Player model for IPL cricketers."""
    __tablename__ = "players"
    
    id: Optional[int] = SQLModelField(default=None, primary_key=True)
    name: str = SQLModelField(index=True)
    team: str = SQLModelField(index=True)
    player_type: str = SQLModelField(index=True)  # BAT, BOWL, ALL, WK
    base_price: Optional[Decimal] = SQLModelField(default=None)
    sold_price: Optional[Decimal] = SQLModelField(default=None)
    
    # Relationships
    user_links: List["UserPlayerLink"] = Relationship(back_populates="player")
    stats: List["PlayerStats"] = Relationship(back_populates="player")
    match_performances: List["MatchPerformance"] = Relationship(back_populates="player")
    
    @validator("player_type")
    def validate_player_type(cls, v):
        valid_types = ["BAT", "BOWL", "ALL", "WK"]
        if v not in valid_types:
            raise ValueError(f"Player type must be one of {valid_types}")
        return v


class PlayerStats(TimeStampedModel, table=True):
    """Cumulative player statistics for the season."""
    __tablename__ = "player_stats"
    
    id: Optional[int] = SQLModelField(default=None, primary_key=True)
    player_id: int = SQLModelField(foreign_key="players.id")
    matches_played: int = SQLModelField(default=0)
    runs: int = SQLModelField(default=0)
    wickets: int = SQLModelField(default=0)
    highest_score: int = SQLModelField(default=0)
    best_bowling: str = SQLModelField(default="0/0")
    fantasy_points: float = SQLModelField(default=0.0)
    
    # Relationships
    player: Player = Relationship(back_populates="stats")


class Match(TimeStampedModel, table=True):
    """IPL match schedule and results."""
    __tablename__ = "matches"
    
    id: Optional[int] = SQLModelField(default=None, primary_key=True)
    match_number: int = SQLModelField(index=True)
    team1: str
    team2: str
    venue: str
    date: datetime = SQLModelField(index=True)
    result: Optional[str] = SQLModelField(default=None)
    winner: Optional[str] = SQLModelField(default=None)
    player_of_match: Optional[str] = SQLModelField(default=None)
    
    # Relationships
    performances: List["MatchPerformance"] = Relationship(back_populates="match")


class MatchPerformance(TimeStampedModel, table=True):
    """Individual player performance in a match."""
    __tablename__ = "match_performances"
    
    id: Optional[int] = SQLModelField(default=None, primary_key=True)
    match_id: int = SQLModelField(foreign_key="matches.id")
    player_id: int = SQLModelField(foreign_key="players.id")
    runs: int = SQLModelField(default=0)
    balls_faced: int = SQLModelField(default=0)
    fours: int = SQLModelField(default=0)
    sixes: int = SQLModelField(default=0)
    wickets: int = SQLModelField(default=0)
    overs_bowled: float = SQLModelField(default=0.0)
    runs_conceded: int = SQLModelField(default=0)
    economy: float = SQLModelField(default=0.0)
    catches: int = SQLModelField(default=0)
    stumpings: int = SQLModelField(default=0)
    run_outs: int = SQLModelField(default=0)
    fantasy_points: float = SQLModelField(default=0.0)
    
    # Relationships
    match: Match = Relationship(back_populates="performances")
    player: Player = Relationship(back_populates="match_performances")


class AuctionRound(TimeStampedModel, table=True):
    """Auction rounds for player bidding."""
    __tablename__ = "auction_rounds"
    
    id: Optional[int] = SQLModelField(default=None, primary_key=True)
    round_number: int = SQLModelField(unique=True, index=True)
    start_time: datetime
    end_time: datetime
    status: str = SQLModelField(default="pending")  # pending, active, completed
    
    # Relationships
    bids: List["AuctionBid"] = Relationship(back_populates="auction_round")
    
    @validator("status")
    def validate_status(cls, v):
        valid_statuses = ["pending", "active", "completed"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        return v


class AuctionBid(TimeStampedModel, table=True):
    """User bids for players in auction rounds."""
    __tablename__ = "auction_bids"
    
    id: Optional[int] = SQLModelField(default=None, primary_key=True)
    user_id: int = SQLModelField(foreign_key="users.id")
    player_id: int = SQLModelField(foreign_key="players.id")
    auction_round_id: int = SQLModelField(foreign_key="auction_rounds.id")
    bid_amount: Decimal
    status: str = SQLModelField(default="pending")  # pending, accepted, rejected
    
    # Relationships
    user: User = Relationship(back_populates="bids")
    auction_round: AuctionRound = Relationship(back_populates="bids")
    
    @validator("bid_amount")
    def validate_bid_amount(cls, v):
        if v <= 0:
            raise ValueError("Bid amount must be positive")
        return v
    
    @validator("status")
    def validate_status(cls, v):
        valid_statuses = ["pending", "accepted", "rejected"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        return v


class TransferWindow(TimeStampedModel, table=True):
    """Weekly transfer windows for team adjustments."""
    __tablename__ = "transfer_windows"
    
    id: Optional[int] = SQLModelField(default=None, primary_key=True)
    week_number: int = SQLModelField(unique=True, index=True)
    start_time: datetime
    end_time: datetime
    status: str = SQLModelField(default="pending")  # pending, active, completed
    
    # Relationships
    transfers: List["PlayerTransfer"] = Relationship(back_populates="transfer_window")
    
    @validator("status")
    def validate_status(cls, v):
        valid_statuses = ["pending", "active", "completed"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        return v


class PlayerTransfer(TimeStampedModel, table=True):
    """Player transfers during transfer windows."""
    __tablename__ = "player_transfers"
    
    id: Optional[int] = SQLModelField(default=None, primary_key=True)
    user_id: int = SQLModelField(foreign_key="users.id")
    transfer_window_id: int = SQLModelField(foreign_key="transfer_windows.id")
    player_out_id: int = SQLModelField(foreign_key="players.id")
    player_in_id: int = SQLModelField(foreign_key="players.id")
    
    # Relationships
    transfer_window: TransferWindow = Relationship(back_populates="transfers") 


# Base Pydantic models for validation and API responses
class TimeStampedBase(BaseModel):
    """Base model with timestamps for API responses."""
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Common validation functions
def validate_non_negative(value: float) -> float:
    """Validate that a value is non-negative."""
    if value < 0:
        raise ValueError("Value cannot be negative")
    return value


def validate_status(value: str, valid_statuses: List[str]) -> str:
    """Validate that a status is one of the valid options."""
    if value not in valid_statuses:
        raise ValueError(f"Status must be one of {valid_statuses}")
    return value 