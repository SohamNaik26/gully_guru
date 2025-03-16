"""
Schemas for fantasy-related data.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from enum import Enum

from src.api.schemas.player import PlayerType


class PlayerBase(BaseModel):
    """Base schema for player information."""

    id: int
    name: str
    team: str
    player_type: PlayerType
    base_price: Optional[float] = None


class DraftStatus(str, Enum):
    """Enum for draft status."""

    SELECTED = "selected"
    SUBMITTED = "submitted"
    CONTESTED = "contested"
    UNCONTESTED = "uncontested"
    AUCTIONED = "auctioned"


class DraftPlayerBase(BaseModel):
    """Base model for draft player data."""

    player_id: int = Field(..., description="ID of the player")
    participant_id: int = Field(..., description="ID of the participant")


class DraftPlayerCreate(DraftPlayerBase):
    """Model for creating a new draft player."""

    status: DraftStatus = Field(DraftStatus.SELECTED, description="Status of the draft")


class DraftPlayerResponse(DraftPlayerBase):
    """Model for draft player response."""

    id: int = Field(..., description="ID of the draft player")
    selected_at: datetime = Field(..., description="Selection timestamp")
    status: DraftStatus = Field(..., description="Status of the draft")

    model_config = ConfigDict(from_attributes=True)


class DraftSelectionBase(BaseModel):
    """Base model for draft selection data."""

    player_id: int = Field(..., description="ID of the player")
    participant_id: int = Field(..., description="ID of the participant")


class DraftSelectionCreate(DraftSelectionBase):
    """Model for creating a new draft selection."""

    pass


class DraftSelectionResponse(BaseModel):
    """Model for draft selection response."""

    id: int = Field(..., description="ID of the draft selection")
    player_id: int = Field(..., description="ID of the player")
    name: str = Field(..., description="Name of the player")
    team: str = Field(..., description="Team of the player")
    player_type: PlayerType = Field(..., description="Type of player")
    base_price: float = Field(..., description="Base price of the player")
    sold_price: Optional[float] = Field(None, description="Sold price of the player")
    season: int = Field(..., description="Season year")
    selected_at: datetime = Field(..., description="Selection timestamp")


class BulkPlayerAddRequest(BaseModel):
    """Model for bulk player add request."""

    player_ids: List[int] = Field(..., description="List of player IDs to add")


class BulkPlayerRemoveRequest(BaseModel):
    """Model for bulk player remove request."""

    player_ids: List[int] = Field(..., description="List of player IDs to remove")


class PlayerDetail(BaseModel):
    """Schema for player details."""

    id: int
    name: str
    team: str
    player_type: PlayerType
    base_price: Optional[float] = None


class ParticipantPlayerDetail(BaseModel):
    """Schema for participant player details."""

    id: int
    gully_participant_id: int
    player_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    player: PlayerDetail


class BulkDraftPlayerResponse(BaseModel):
    """Model for bulk draft player operation response."""

    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Operation message")
    added_count: int = Field(0, description="Number of players added")
    removed_count: int = Field(0, description="Number of players removed")
    failed_ids: List[int] = Field([], description="List of player IDs that failed")


class SubmissionStatusResponse(BaseModel):
    """Model for submission status response."""

    gully_id: int = Field(..., description="ID of the gully")
    gully_status: str = Field(..., description="Status of the gully")
    total_participants: int = Field(0, description="Total number of participants")
    submitted_participants: int = Field(
        0, description="Number of participants who have submitted"
    )
    all_submitted: bool = Field(
        False, description="Whether all participants have submitted"
    )
    submitted_details: List[Dict[str, Any]] = Field(
        [], description="Details of submitted participants"
    )
    not_submitted_details: List[Dict[str, Any]] = Field(
        [], description="Details of participants who haven't submitted"
    )


class AuctionStartResponse(BaseModel):
    """Model for auction start response."""

    gully_id: int = Field(..., description="ID of the gully")
    status: str = Field(..., description="Status of the auction")
    message: str = Field(..., description="Auction message")
    contested_count: int = Field(0, description="Number of contested players")
    uncontested_count: int = Field(0, description="Number of uncontested players")


class ContestPlayerResponse(BaseModel):
    """Model for contest player response."""

    player_id: int = Field(..., description="ID of the player")
    name: str = Field(..., description="Name of the player")
    team: str = Field(..., description="Team of the player")
    player_type: PlayerType = Field(..., description="Type of player")
    base_price: float = Field(..., description="Base price of the player")
    contested_by: List[Dict[str, Any]] = Field(
        [], description="List of participants contesting the player"
    )
    contest_count: int = Field(
        0, description="Number of participants contesting the player"
    )


class FinalizeDraftResponse(BaseModel):
    """Model for finalize draft response."""

    gully_id: int = Field(..., description="ID of the gully")
    status: str = Field(..., description="Status of the draft")
    message: str = Field(..., description="Draft message")
    success: bool = Field(
        False, description="Whether the draft was finalized successfully"
    )


class SuccessResponse(BaseModel):
    """Model for success response."""

    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Operation message")


class SquadResponse(BaseModel):
    """Model for squad response."""

    players: List[DraftSelectionResponse] = Field(
        [], description="List of players in the squad"
    )
    player_count: int = Field(0, description="Number of players in the squad")

    model_config = ConfigDict(from_attributes=True)
