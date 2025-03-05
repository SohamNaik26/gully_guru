from typing import Optional, List
from decimal import Decimal
from sqlmodel import Field, Relationship
from src.models.base import TimeStampedModel

class GullyParticipant(TimeStampedModel, table=True):
    """Model for gully participants."""
    __tablename__ = "gully_participants"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    gully_id: int = Field(foreign_key="gullies.id")
    user_id: int = Field(foreign_key="users.id")
    team_name: str = Field()
    budget: Decimal = Field(default=100.0)
    points: int = Field(default=0)
    
    # Relationships
    gully: Optional["Gully"] = Relationship(back_populates="participants")
    user: Optional["User"] = Relationship(back_populates="gully_participations")
    players: List["Player"] = Relationship(link_model="UserPlayerLink") 