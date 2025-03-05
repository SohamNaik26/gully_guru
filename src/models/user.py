from typing import Optional, List
from sqlmodel import Field, Relationship
from src.models.base import TimeStampedModel

class User(TimeStampedModel, table=True):
    """Model for users."""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    telegram_id: int = Field(unique=True)
    first_name: str = Field()
    last_name: Optional[str] = Field(default=None)
    username: Optional[str] = Field(default=None)
    active_game_id: Optional[int] = Field(default=None, foreign_key="games.id")
    
    # Relationships
    players: List["Player"] = Relationship(link_model="UserPlayerLink", back_populates="user")
    bids: List["AuctionBid"] = Relationship(back_populates="user")
    game_participations: List["GameParticipant"] = Relationship(back_populates="user")
    active_game: Optional["Game"] = Relationship() 