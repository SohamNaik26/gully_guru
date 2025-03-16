"""
Schemas for auction-related data.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum

from src.api.schemas.player import PlayerType, PlayerResponse
from src.api.schemas.participant import ParticipantResponse
from src.db.models.models import AuctionStatus, AuctionType


class AuctionStatusEnum(str, Enum):
    """Enum for auction status."""

    PENDING = "pending"
    BIDDING = "bidding"
    COMPLETED = "completed"


class AuctionTypeEnum(str, Enum):
    """Enum for auction type."""

    NEW_PLAYER = "new_player"
    TRANSFER = "transfer"


class ParticipantInfo(BaseModel):
    """Schema for participant information in auction responses."""

    participant_id: int = Field(..., description="ID of the participant")
    user_id: int = Field(..., description="ID of the user")
    team_name: str = Field(..., description="Team name of the participant")


class ContestPlayerResponse(BaseModel):
    """Schema for contested player information."""

    player_id: int = Field(..., description="ID of the player")
    name: str = Field(..., description="Name of the player")
    team: str = Field(..., description="Team of the player")
    player_type: PlayerType = Field(..., description="Type of player")
    base_price: float = Field(..., description="Base price of the player")
    contested_by: List[ParticipantInfo] = Field(
        default_factory=list, description="List of participants contesting the player"
    )
    contest_count: int = Field(
        0, description="Number of participants contesting the player"
    )


class UncontestedPlayerResponse(BaseModel):
    """Schema for uncontested player information."""

    player_id: int = Field(..., description="ID of the player")
    player_name: str = Field(..., description="Name of the player")
    team: str = Field(..., description="Team of the player")
    role: str = Field(..., description="Role of the player")
    participants: List[ParticipantInfo] = Field(
        default_factory=list, description="List of participants who selected the player"
    )


class AuctionStartResponse(BaseModel):
    """Schema for auction start response."""

    gully_id: int = Field(..., description="ID of the gully")
    status: str = Field(..., description="Status of the auction")
    message: str = Field(..., description="Auction message")
    contested_count: int = Field(0, description="Number of contested players")
    uncontested_count: int = Field(0, description="Number of uncontested players")
    contested_players: Optional[List[ContestPlayerResponse]] = Field(
        None, description="List of contested players"
    )
    uncontested_players: Optional[List[UncontestedPlayerResponse]] = Field(
        None, description="List of uncontested players"
    )


class AuctionQueueBase(BaseModel):
    """Base schema for auction queue items."""

    gully_id: int = Field(..., description="ID of the gully")
    player_id: int = Field(..., description="ID of the player")
    seller_participant_id: Optional[int] = Field(
        None, description="ID of the seller participant (for transfers)"
    )
    auction_type: AuctionTypeEnum = Field(
        AuctionTypeEnum.NEW_PLAYER, description="Type of auction"
    )
    status: AuctionStatusEnum = Field(
        AuctionStatusEnum.PENDING, description="Status of the auction"
    )


class AuctionQueueCreate(AuctionQueueBase):
    """Schema for creating an auction queue item."""

    pass


class AuctionQueueResponse(BaseModel):
    """Schema for auction queue item response."""

    id: int = Field(..., description="ID of the auction queue item")
    gully_id: int = Field(..., description="ID of the gully")
    player_id: int = Field(..., description="ID of the player")
    player_name: str = Field(..., description="Name of the player")
    team: str = Field(..., description="Team of the player")
    player_type: str = Field(..., description="Type of player")
    base_price: float = Field(..., description="Base price of the player")
    seller_participant_id: Optional[int] = Field(
        None, description="ID of the seller participant (for transfers)"
    )
    auction_type: str = Field(
        AuctionTypeEnum.NEW_PLAYER.value, description="Type of auction"
    )
    status: str = Field(
        AuctionStatusEnum.PENDING.value, description="Status of the auction"
    )
    listed_at: datetime = Field(..., description="When the player was listed")

    model_config = ConfigDict(from_attributes=True)


class BidBase(BaseModel):
    """Base schema for bid information."""

    auction_queue_id: int = Field(..., description="ID of the auction queue item")
    gully_participant_id: int = Field(..., description="ID of the participant")
    bid_amount: float = Field(..., gt=0, description="Amount of the bid")


class BidCreate(BidBase):
    """Schema for creating a bid."""

    pass


class BidResponse(BidBase):
    """Schema for bid response."""

    id: int = Field(..., description="ID of the bid")
    bid_time: datetime = Field(..., description="When the bid was placed")
    participant: Optional[ParticipantInfo] = Field(
        None, description="Participant details"
    )

    model_config = ConfigDict(from_attributes=True)


class AuctionStatusUpdateRequest(BaseModel):
    """Schema for updating auction status."""

    status: AuctionStatusEnum = Field(..., description="New status for the auction")


class ResolveContestedPlayerRequest(BaseModel):
    """Schema for resolving contested player."""

    player_id: int = Field(..., description="ID of the player")
    winning_participant_id: int = Field(
        ..., description="ID of the winning participant"
    )


class ResolveContestedPlayerResponse(BaseModel):
    """Schema for contested player resolution response."""

    player_id: int = Field(..., description="ID of the player")
    player_name: str = Field(..., description="Name of the player")
    winning_participant_id: int = Field(
        ..., description="ID of the winning participant"
    )
    winning_team_name: str = Field(
        ..., description="Team name of the winning participant"
    )
    status: str = Field("resolved", description="Resolution status")
    message: str = Field(..., description="Resolution message")


class SubmissionStatusResponse(BaseModel):
    """Schema for submission status response."""

    gully_id: int = Field(..., description="ID of the gully")
    total_participants: int = Field(..., description="Total number of participants")
    submitted_count: int = Field(
        ..., description="Number of participants who submitted"
    )
    is_complete: bool = Field(
        ..., description="Whether all participants have submitted"
    )
    status: str = Field(..., description="Submission status")


class AuctionQueueListResponse(BaseModel):
    """Schema for listing auction queue items."""

    players: List[AuctionQueueResponse] = Field(
        ..., description="List of auction queue items"
    )


class ReleasePlayersRequest(BaseModel):
    """Schema for releasing players request."""
    player_ids: List[int] = Field(..., description="List of player IDs to release")
    participant_id: int = Field(..., description="ID of the participant releasing the players")


class ReleasePlayersResponse(BaseModel):
    """Schema for releasing players response."""
    released_count: int = Field(..., description="Number of players released")
    released_players: List[Dict[str, Any]] = Field(..., description="List of released players")
    message: str = Field(..., description="Release message")
