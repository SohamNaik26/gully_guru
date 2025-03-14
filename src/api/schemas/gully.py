"""
Gully schemas for the GullyGuru API.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class GullyBase(BaseModel):
    """Base model for gully data."""

    name: str = Field(..., description="Name of the gully")
    telegram_group_id: Optional[int] = Field(None, description="Telegram group ID")


class GullyCreate(GullyBase):
    """Model for creating a new gully."""

    pass


class GullyUpdate(BaseModel):
    """Model for updating a gully."""

    name: Optional[str] = Field(None, description="Name of the gully")
    status: Optional[str] = Field(None, description="Status of the gully")
    telegram_group_id: Optional[int] = Field(None, description="Telegram group ID")


class GullyResponse(BaseModel):
    """Model for gully response."""

    id: int = Field(..., description="ID of the gully")
    name: str = Field(..., description="Name of the gully")
    status: str = Field(..., description="Status of the gully")
    telegram_group_id: int = Field(..., description="Telegram group ID")
    description: Optional[str] = Field(None, description="Description of the gully")
    created_by: Optional[int] = Field(None, description="ID of the creator")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic config."""

        from_attributes = True


class SuccessResponse(BaseModel):
    """Model for success response."""

    success: bool = Field(..., description="Success status")
    message: str = Field(..., description="Success message")
