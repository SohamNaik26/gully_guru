from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict


class PlayerBase(BaseModel):
    """Base schema for player information."""

    id: int
    name: str
    team: str
    player_type: str
    base_price: Optional[float] = None


class DraftPlayerCreate(BaseModel):
    """Schema for adding a player to draft squad."""

    player_id: int
    gully_id: int

    model_config = ConfigDict(from_attributes=True)


class DraftPlayerResponse(BaseModel):
    """Response schema for draft player operations."""

    success: bool
    message: str

    model_config = ConfigDict(from_attributes=True)


class DraftSquadResponse(BaseModel):
    """Response schema for draft squad."""

    players: List[PlayerBase] = []
    total_price: float = 0.0
    player_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class SquadSubmit(BaseModel):
    """Schema for submitting a squad."""

    gully_id: int

    model_config = ConfigDict(from_attributes=True)


class SubmissionStatusResponse(BaseModel):
    """Response schema for submission status."""

    all_submitted: bool
    total_participants: int
    submitted_count: int
    pending_users: List[Dict[str, Any]] = []

    model_config = ConfigDict(from_attributes=True)


class PendingUser(BaseModel):
    """Schema for pending user information."""

    id: int
    username: str
    telegram_id: int

    model_config = ConfigDict(from_attributes=True)


class AuctionStartResponse(BaseModel):
    """Response schema for starting an auction."""

    success: bool
    message: str
    contested_count: Optional[int] = None
    uncontested_count: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class ContestPlayerResponse(BaseModel):
    """Response schema for contested players."""

    players: List[PlayerBase] = []

    model_config = ConfigDict(from_attributes=True)
