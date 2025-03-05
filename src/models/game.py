from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, Relationship
from src.models.auction import Auction
from src.models.base import TimeStampedModel


class Gully(TimeStampedModel, table=True):
    """Model for gully instances (fantasy cricket leagues)."""

    __tablename__ = "gullies"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field()
    telegram_group_id: int = Field(unique=True)
    status: str = Field(default="pending")  # pending, active, completed
    start_date: datetime = Field()
    end_date: datetime = Field()

    # Relationships
    auctions: List["Auction"] = Relationship(back_populates="gully")
    transfer_windows: List["TransferWindow"] = Relationship(back_populates="gully")
    participants: List["GullyParticipant"] = Relationship(back_populates="gully")
