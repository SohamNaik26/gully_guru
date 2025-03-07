from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel


# User API Models
class UserBase(BaseModel):
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


# Note: We're using string type annotation to avoid circular imports
class UserWithPlayers(UserResponse):
    """User model with owned players."""

    owned_players: List["PlayerResponse"] = []

    class Config:
        from_attributes = True


# No need to rebuild the model, Pydantic will handle the string type annotation
# UserWithPlayers.model_rebuild()
