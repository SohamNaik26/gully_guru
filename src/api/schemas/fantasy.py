"""
Schemas for fantasy-related data.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class PlayerBase(BaseModel):
    """Base schema for player information."""

    id: int
    name: str
    team: str
    player_type: str
    base_price: Optional[float] = None


class DraftPlayerBase(BaseModel):
    """Base schema for draft player."""

    gully_participant_id: int = Field(..., description="Gully participant ID")
    player_id: int = Field(..., description="Player ID")
    status: str = Field(
        default="draft", description="Player status (draft, locked, contested, owned)"
    )


class DraftPlayerCreate(BaseModel):
    """Schema for adding a player to draft squad."""

    gully_id: int = Field(..., description="Gully ID")
    player_id: int = Field(..., description="Player ID")


class DraftPlayerResponse(DraftPlayerBase):
    """Schema for draft player response."""

    id: int = Field(..., description="Draft player ID")
    created_at: datetime = Field(..., description="When the draft player was created")
    updated_at: datetime = Field(
        ..., description="When the draft player was last updated"
    )
    player: Dict[str, Any] = Field(..., description="Player details")

    model_config = ConfigDict(from_attributes=True)


class SquadResponse(BaseModel):
    """Schema for squad response."""

    gully_participant_id: int = Field(..., description="Gully participant ID")
    gully_id: int = Field(..., description="Gully ID")
    user_id: int = Field(..., description="User ID")
    username: Optional[str] = Field(None, description="Username")
    players: List[DraftPlayerResponse] = Field(
        default_factory=list, description="Players in squad"
    )
    player_count: int = Field(default=0, description="Number of players in squad")

    model_config = ConfigDict(from_attributes=True)


class SubmitSquadResponse(BaseModel):
    """Schema for submit squad response."""

    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Success or error message")
    gully_participant_id: int = Field(..., description="Gully participant ID")
    player_count: int = Field(..., description="Number of players in squad")

    model_config = ConfigDict(from_attributes=True)


class SubmissionStatusResponse(BaseModel):
    """Schema for submission status response."""

    all_submitted: bool = Field(
        ..., description="Whether all participants have submitted"
    )
    total_participants: int = Field(..., description="Total number of participants")
    submitted_count: int = Field(
        ..., description="Number of participants who have submitted"
    )
    pending_users: List[Dict[str, Any]] = Field(
        default_factory=list, description="List of users who have not submitted"
    )

    model_config = ConfigDict(from_attributes=True)


class AuctionStartResponse(BaseModel):
    """Schema for auction start response."""

    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Success or error message")
    contested_count: int = Field(..., description="Number of contested players")
    uncontested_count: int = Field(..., description="Number of uncontested players")

    model_config = ConfigDict(from_attributes=True)


class ContestPlayerResponse(BaseModel):
    """Schema for contest player response."""

    players: List[Dict[str, Any]] = Field(
        default_factory=list, description="List of players"
    )

    model_config = ConfigDict(from_attributes=True)


class SuccessResponse(BaseModel):
    """Schema for success response."""

    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Success or error message")

    model_config = ConfigDict(from_attributes=True)
