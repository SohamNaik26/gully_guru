"""
Schemas for user-related data.
"""

from datetime import datetime
from decimal import Decimal
from typing import List
from pydantic import BaseModel, ConfigDict

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


# GullyParticipant API Models
class GullyParticipantBase(BaseModel):
    """Base model for gully participant data."""

    user_id: int
    gully_id: int
    team_name: str
    budget: Decimal = Decimal("120.0")
    points: int = 0
    role: str = "member"
    is_active: bool = False
    registration_complete: bool = False


class GullyParticipantCreate(GullyParticipantBase):
    """Create model for gully participant data."""

    pass


class GullyParticipantResponse(GullyParticipantBase):
    """Response model for gully participant data."""

    id: int
    created_at: datetime
    updated_at: datetime
    last_active_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Note: We're using string type annotation to avoid circular imports
class UserWithPlayers(UserResponse):
    """User model with owned players."""

    owned_players: List["PlayerResponse"] = []

    model_config = ConfigDict(from_attributes=True)


# No need to rebuild the model, Pydantic will handle the string type annotation
# UserWithPlayers.model_rebuild()
