"""
Participant schemas for the GullyGuru API.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ParticipantBase(BaseModel):
    """Base model for participant data."""

    user_id: int = Field(..., description="ID of the user")
    gully_id: int = Field(..., description="ID of the gully")
    role: str = Field(
        default="participant", description="Role of the user in the gully"
    )
    team_name: Optional[str] = Field(None, description="Team name for the user")


class ParticipantCreate(ParticipantBase):
    """Model for creating a new participant."""

    pass


class ParticipantUpdate(BaseModel):
    """Model for updating a participant."""

    role: Optional[str] = Field(None, description="Role of the user in the gully")
    team_name: Optional[str] = Field(None, description="Team name for the user")


class ParticipantResponse(ParticipantBase):
    """Model for participant response."""

    id: int = Field(..., description="ID of the participant")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic config."""

        orm_mode = True
