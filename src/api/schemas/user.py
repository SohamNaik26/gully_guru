"""
Schemas for user-related data.
"""

from datetime import datetime
from decimal import Decimal
from typing import List
from pydantic import BaseModel, ConfigDict, field_validator

# Forward reference for PlayerResponse to avoid circular imports
from src.api.schemas.player import PlayerResponse


# User API Models
class UserBase(BaseModel):
    """Base model for user data."""

    telegram_id: int
    username: str
    full_name: str


class UserCreate(UserBase):
    """Create model for user data."""

    pass


class UserResponse(UserBase):
    """Response model for user data."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserResponseWithGullies(UserResponse):
    """Response model for user data with gully IDs."""

    gully_ids: List[int] = []

    model_config = ConfigDict(from_attributes=True)


# GullyParticipant API Models
class GullyParticipantBase(BaseModel):
    """Base model for gully participant data."""

    user_id: int
    gully_id: int
    team_name: str
    budget: Decimal = Decimal("120.0")
    points: int = 0
    role: str = "member"


class GullyParticipantCreate(GullyParticipantBase):
    """Create model for gully participant data."""

    pass


class GullyParticipantResponse(GullyParticipantBase):
    """Response model for gully participant data."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        """Validate that the role is one of the allowed values."""
        allowed_roles = ["member", "admin"]
        if v not in allowed_roles:
            raise ValueError(f"Role must be one of: {', '.join(allowed_roles)}")
        return v

    @field_validator("budget")
    @classmethod
    def validate_budget(cls, v):
        """Ensure budget is non-negative."""
        if v < 0:
            raise ValueError("Budget cannot be negative")
        return v

    @field_validator("points")
    @classmethod
    def validate_points(cls, v):
        """Validate that points is a non-negative integer."""
        if v < 0:
            raise ValueError("Points must be a non-negative integer")
        return v


# UserPlayer API Models
class UserPlayerBase(BaseModel):
    """Base model for user player data."""

    user_id: int
    player_id: int
    gully_id: int
    purchase_price: Decimal = Decimal("0.0")
    is_captain: bool = False
    is_vice_captain: bool = False
    is_playing_xi: bool = False


class UserPlayerCreate(UserPlayerBase):
    """Create model for user player data."""

    pass


class UserPlayerResponse(UserPlayerBase):
    """Response model for user player data."""

    id: int
    purchase_date: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("purchase_price")
    @classmethod
    def validate_purchase_price(cls, v):
        """Ensure purchase price is non-negative."""
        if v < 0:
            raise ValueError("Purchase price cannot be negative")
        return v


# Note: We're using string type annotation to avoid circular imports
class UserWithPlayers(UserResponse):
    """User model with owned players."""

    owned_players: List["PlayerResponse"] = []

    model_config = ConfigDict(from_attributes=True)


# No need to rebuild the model, Pydantic will handle the string type annotation
# UserWithPlayers.model_rebuild()
