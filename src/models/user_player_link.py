from typing import Optional
from decimal import Decimal
from sqlmodel import Field, Relationship
from src.models.base import TimeStampedModel

class UserPlayerLink(TimeStampedModel, table=True):
    """Model for linking users to players."""
    __tablename__ = "user_player_links"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    player_id: int = Field(foreign_key="players.id")
    gully_id: int = Field(foreign_key="gullies.id")  # Changed from game_id
    price: Decimal = Field()
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="players")
    player: Optional["Player"] = Relationship(back_populates="owners")
    gully: Optional["Gully"] = Relationship()  # Changed from game 