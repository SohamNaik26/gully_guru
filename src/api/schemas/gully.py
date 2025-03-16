"""
Gully schemas for the GullyGuru API.
"""

from typing import Optional, List, Dict, Any
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


class SubmissionStatusResponse(BaseModel):
    """Schema for submission status response."""

    gully_id: int = Field(..., description="ID of the gully")
    gully_status: str = Field(..., description="Status of the gully")
    total_participants: int = Field(..., description="Total number of participants")
    submitted_participants: int = Field(
        ..., description="Number of participants who have submitted"
    )
    all_submitted: bool = Field(
        ..., description="Whether all participants have submitted"
    )

    # Details of participants who have submitted
    submitted_details: List[Dict[str, Any]] = Field(
        default_factory=list, description="Details of participants who have submitted"
    )

    # Details of participants who have not submitted
    not_submitted_details: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Details of participants who have not submitted",
    )

    class Config:
        """Pydantic config."""

        orm_mode = True
