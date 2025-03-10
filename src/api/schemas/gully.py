from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel, field_validator, ConfigDict

from src.db.models.base import validate_non_negative, validate_status
from src.api.schemas.player import PlayerResponse


# Gully (League) Models
class GullyBase(BaseModel):
    """Base model for gully (cricket league) data."""

    name: str
    telegram_group_id: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class GullyCreate(GullyBase):
    """Model for creating a new gully."""

    pass


class GullyResponse(GullyBase):
    """Response model for gully data."""

    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Gully Participant Models
class GullyParticipantBase(BaseModel):
    """Base model for gully participant data."""

    user_id: int
    team_name: str


class GullyParticipantCreate(GullyParticipantBase):
    """Model for creating a new gully participant."""

    pass


class GullyParticipantResponse(GullyParticipantBase):
    """Response model for gully participant data."""

    id: int
    gully_id: int
    budget: Decimal
    points: int
    role: str
    is_active: bool
    registration_complete: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ParticipantUpdate(BaseModel):
    """Model for updating a gully participant."""

    action: Optional[str] = None  # activate, complete_registration
    role: Optional[str] = None  # admin, member
    team_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# User Squad Models
class UserSquadResponse(BaseModel):
    """Response model for user squad data."""

    user_id: int
    username: str  # Joined from User
    players: List[PlayerResponse]
    captain: Optional[PlayerResponse] = None
    vice_captain: Optional[PlayerResponse] = None
    total_points: float

    model_config = ConfigDict(from_attributes=True)


# Auction Models
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

    model_config = ConfigDict(from_attributes=True)


# Leaderboard Models
class LeaderboardEntry(BaseModel):
    """Entry in the leaderboard."""

    rank: int
    user_id: int
    username: str
    total_points: float

    model_config = ConfigDict(from_attributes=True)


class LeaderboardResponse(BaseModel):
    """Response model for leaderboard data."""

    leaderboard: List[LeaderboardEntry]
    total_users: int
    updated_at: datetime


# UserPlayer Models
class UserPlayerBase(BaseModel):
    """Base model for user player data."""

    user_id: int
    player_id: int
    gully_id: int
    purchase_price: Decimal
    purchase_date: datetime


class UserPlayerCreate(UserPlayerBase):
    """Model for creating a new user player."""

    pass


class UserPlayerRead(UserPlayerBase):
    """Response model for user player data."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserPlayerWithDetails(UserPlayerRead):
    """Response model for user player data with player details."""

    player: PlayerResponse

    model_config = ConfigDict(from_attributes=True)
