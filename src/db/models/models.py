from typing import Optional, TYPE_CHECKING, ForwardRef
from datetime import datetime, timezone
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator
from sqlalchemy import TypeDecorator, DateTime, BigInteger, event
import sqlalchemy


# Custom DateTime type that ensures timezone awareness
class TZDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None and value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value

    def process_result_value(self, value, dialect):
        if value is not None and value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value


# Base Models
class TimeStampedModel(SQLModel):
    """Base model with created and updated timestamps."""

    # Use timezone-aware datetime objects with explicit SQLAlchemy type
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=sqlalchemy.DateTime(timezone=True),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=sqlalchemy.DateTime(timezone=True),
    )


# Player Models
class Player(TimeStampedModel, table=True):
    """
    Player model for IPL cricketers.

    Represents a cricket player in the IPL with their basic information,
    team affiliation, and role.

    Attributes:
        id: Primary key
        name: Player's full name
        team: IPL team name
        player_type: Type of player (BAT, BOWL, ALL, WK)
        base_price: Base auction price
        sold_price: Final auction price
        season: IPL season year
    """

    __tablename__ = "players"

    id: Optional[int] = Field(default=None, primary_key=True, description="Primary key")
    name: str = Field(index=True, description="Player's full name")
    team: str = Field(index=True, description="IPL team name")
    player_type: str = Field(
        index=True, description="Type of player (BAT, BOWL, ALL, WK)"
    )
    base_price: Optional[Decimal] = Field(
        default=None, description="Base auction price"
    )
    sold_price: Optional[Decimal] = Field(
        default=None, description="Final auction price"
    )
    season: int = Field(default=2025, index=True, description="IPL season year")

    # Relationships will be defined after all classes are defined

    @field_validator("player_type")
    @classmethod
    def validate_player_type(cls, v):
        """Validate that player_type is one of the allowed values."""
        valid_types = ["BAT", "BOWL", "ALL", "WK"]
        if v not in valid_types:
            raise ValueError(f"Player type must be one of {valid_types}")
        return v


# User Models
class User(TimeStampedModel, table=True):
    """User model for fantasy cricket managers."""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    telegram_id: int = Field(unique=True, index=True, sa_type=BigInteger)
    username: str = Field(index=True)
    full_name: str

    # Relationships will be defined after all classes are defined


# Forward declarations for relationship references
class GullyParticipant(TimeStampedModel, table=True):
    """
    Model for game participants in a Gully.

    Represents a user's participation in a specific Gully (fantasy cricket league),
    including their team name, budget, and points.

    Attributes:
        id: Primary key
        gully_id: Reference to the Gully
        user_id: Reference to the User
        team_name: Name of the user's team in this Gully
        budget: Available budget for this Gully
        points: Total points earned in this Gully
        role: User's role in this Gully (member, admin, owner)
    """

    __tablename__ = "gully_participants"

    id: Optional[int] = Field(default=None, primary_key=True, description="Primary key")
    gully_id: int = Field(
        foreign_key="gullies.id", description="Reference to the Gully"
    )
    user_id: int = Field(foreign_key="users.id", description="Reference to the User")
    team_name: str = Field(description="Name of the user's team in this Gully")
    budget: Decimal = Field(
        default=120.0, description="Available budget for this Gully"
    )
    points: int = Field(default=0, description="Total points earned in this Gully")
    role: str = Field(
        default="member", description="User's role in this Gully (member, admin)"
    )

    # Define unique constraint for user_id and gully_id
    __table_args__ = (
        sqlalchemy.UniqueConstraint("user_id", "gully_id", name="uq_user_gully"),
    )

    # Relationships will be defined after all classes are defined


class Gully(TimeStampedModel, table=True):
    """
    Model for fantasy cricket leagues (called 'Gullies').

    Represents a fantasy cricket league where users can participate,
    draft players, and compete against each other.

    Attributes:
        id: Primary key
        name: Name of the Gully
        telegram_group_id: Telegram group ID associated with this Gully
    """

    __tablename__ = "gullies"

    id: Optional[int] = Field(default=None, primary_key=True, description="Primary key")
    name: str = Field(index=True, description="Name of the Gully")
    telegram_group_id: int = Field(
        unique=True,
        sa_type=BigInteger,
        description="Telegram group ID associated with this Gully",
    )

    # Relationships will be defined after all classes are defined


# Define relationships after all classes are defined to avoid circular references
# Add this at the end of the file, after all model classes are defined

# User relationships
User.gully_participations = Relationship(
    sa_relationship_kwargs={"lazy": "selectin"}, back_populates="user"
)
User.gullies = Relationship(
    link_model=GullyParticipant,
    sa_relationship_kwargs={"lazy": "selectin"},
    back_populates="users",
)
User.user_players = Relationship(
    sa_relationship_kwargs={"lazy": "selectin"}, back_populates="user"
)


# Add property to User model for easy access to gully IDs
def get_gully_ids(self) -> list[int]:
    """Return a list of gully IDs that the user is a part of."""
    return [participation.gully_id for participation in self.gully_participations]


# Attach the property to the User class
User.gully_ids = property(get_gully_ids)

# GullyParticipant relationships
GullyParticipant.user = Relationship(back_populates="gully_participations")
GullyParticipant.gully = Relationship(back_populates="participants")

# Gully relationships
Gully.participants = Relationship(
    sa_relationship_kwargs={"lazy": "selectin"}, back_populates="gully"
)
Gully.user_players = Relationship(
    sa_relationship_kwargs={"lazy": "selectin"}, back_populates="gully"
)
Gully.users = Relationship(
    link_model=GullyParticipant,
    sa_relationship_kwargs={"lazy": "selectin"},
    back_populates="gullies",
)

# Player relationships
Player.user_player = Relationship(
    sa_relationship_kwargs={"lazy": "selectin"}, back_populates="player"
)


# Event listener to update the updated_at field when a record is modified
@event.listens_for(SQLModel, "before_update", propagate=True)
def receive_before_update(mapper, connection, target):
    """Update the updated_at field when a record is modified."""
    target.updated_at = datetime.now(timezone.utc)


# Use TYPE_CHECKING for forward references to avoid circular imports
if TYPE_CHECKING:
    from src.db.models.models import UserPlayer
else:
    UserPlayer = ForwardRef("UserPlayer")
