"""
Participant schemas for the GullyGuru API.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from src.db.models.models import ParticipantRole


class ParticipantBase(BaseModel):
    """Base model for participant data."""

    gully_id: int = Field(..., description="ID of the gully")
    user_id: int = Field(..., description="ID of the user")
    role: str = Field("participant", description="Role in the gully")
    team_name: Optional[str] = Field(None, description="Team name")

    @field_validator("role")
    def validate_role(cls, v):
        """Validate that role is one of the allowed values."""
        allowed_roles = [role.value for role in ParticipantRole]
        if v not in allowed_roles:
            raise ValueError(f"Role must be one of: {', '.join(allowed_roles)}")
        return v


class ParticipantCreate(ParticipantBase):
    """Model for creating a new participant."""

    pass


class ParticipantUpdate(BaseModel):
    """Model for updating a participant."""

    role: Optional[str] = Field(None, description="Role in the gully")
    team_name: Optional[str] = Field(None, description="Team name")

    @field_validator("role")
    def validate_role(cls, v):
        """Validate that role is one of the allowed values."""
        if v is None:
            return v

        allowed_roles = [role.value for role in ParticipantRole]
        if v not in allowed_roles:
            raise ValueError(f"Role must be one of: {', '.join(allowed_roles)}")
        return v


class ParticipantResponse(ParticipantBase):
    """Model for participant response."""

    id: int = Field(..., description="ID of the participant")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic configuration."""

        from_attributes = True
