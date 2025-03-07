from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel, field_validator

from src.db.models.base import validate_non_negative, validate_status
from src.api.schemas.player import PlayerResponse


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

    @field_validator("bid_amount")
    @classmethod
    def validate_bid_amount(cls, v):
        return validate_non_negative(v)


class AuctionBidResponse(BaseModel):
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


# UserPlayer API Models
class UserPlayerBase(BaseModel):
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
    player: PlayerResponse

    class Config:
        from_attributes = True
