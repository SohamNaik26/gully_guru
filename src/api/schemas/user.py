"""
Schemas for user-related data.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from pydantic import field_validator

# Forward reference for PlayerResponse to avoid circular imports
from src.api.schemas.player import PlayerResponse


# User API Models
class UserBase(BaseModel):
    """Base schema for User model."""

    telegram_id: int = Field(..., description="Telegram user ID")
    username: str = Field(..., description="Telegram username")
    full_name: str = Field(..., description="User's full name")


class UserCreate(UserBase):
    """Schema for creating a new user."""

    pass


class UserResponse(UserBase):
    """Schema for user response."""

    id: int = Field(..., description="User ID")
    created_at: datetime = Field(..., description="When the user was created")
    updated_at: datetime = Field(..., description="When the user was last updated")
    gully_ids: Optional[List[int]] = Field(
        None, description="IDs of gullies the user is part of"
    )

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


# ParticipantPlayer API Models
class ParticipantPlayerBase(BaseModel):
    """Base model for participant player data."""

    gully_participant_id: int
    player_id: int
    purchase_price: Decimal = Decimal("0.0")
    is_captain: bool = False
    is_vice_captain: bool = False
    is_playing_xi: bool = False
    status: str = "draft"


class ParticipantPlayerCreate(ParticipantPlayerBase):
    """Create model for participant player data."""

    pass


class ParticipantPlayerResponse(ParticipantPlayerBase):
    """Response model for participant player data."""

    id: int
    purchase_date: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("purchase_price")
    @classmethod
    def validate_purchase_price(cls, v):
        """Validate that purchase price is non-negative."""
        if v < 0:
            raise ValueError("Purchase price must be non-negative")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """Validate that status is one of the allowed values."""
        allowed_values = ["draft", "locked", "contested", "owned"]
        if v not in allowed_values:
            raise ValueError(f"Status must be one of {allowed_values}")
        return v


class UserWithPlayers(UserResponse):
    """User model with owned players."""

    owned_players: List["PlayerResponse"] = []

    model_config = ConfigDict(from_attributes=True)


# No need to rebuild the model, Pydantic will handle the string type annotation
# UserWithPlayers.model_rebuild()


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    username: Optional[str] = Field(None, description="Telegram username")
    full_name: Optional[str] = Field(None, description="User's full name")

    class Config:
        """Pydantic config."""

        extra = "forbid"  # Forbid extra fields
