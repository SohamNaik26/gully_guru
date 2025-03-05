from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, Relationship
from src.models.base import TimeStampedModel

class Auction(TimeStampedModel, table=True):
    """Model for auction rounds."""
    __tablename__ = "auctions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    gully_id: int = Field(foreign_key="gullies.id")  # Changed from game_id
    status: str = Field(default="pending")  # pending, active, completed
    current_player_id: Optional[int] = Field(default=None, foreign_key="players.id")
    start_time: Optional[datetime] = Field(default=None)
    end_time: Optional[datetime] = Field(default=None)
    
    # Relationships
    gully: Optional["Gully"] = Relationship(back_populates="auctions")
    current_player: Optional["Player"] = Relationship()
    bids: List["AuctionBid"] = Relationship(back_populates="auction") 