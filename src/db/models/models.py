from typing import Optional, List
from datetime import datetime, timezone
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator
from sqlalchemy import TypeDecorator, DateTime, BigInteger
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


# Helper function to get current UTC time as ISO string
def _get_utc_now_str():
    return datetime.now(timezone.utc).isoformat()


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


# User Models
class User(TimeStampedModel, table=True):
    """User model for fantasy cricket managers."""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    telegram_id: int = Field(unique=True, index=True, sa_type=BigInteger)
    username: str = Field(index=True)
    full_name: str

    # Relationships
    owned_players: List["UserPlayer"] = Relationship(back_populates="user")
    bids: List["AuctionBid"] = Relationship(back_populates="user")
    transfer_listings: List["TransferListing"] = Relationship(back_populates="seller")
    transfer_bids: List["TransferBid"] = Relationship(back_populates="bidder")
    gully_participations: List["GullyParticipant"] = Relationship(back_populates="user")


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

    # Relationships
    user_player: Optional["UserPlayer"] = Relationship(
        back_populates="player", sa_relationship_kwargs={"lazy": "selectin"}
    )
    stats: List["PlayerStats"] = Relationship(
        back_populates="player", sa_relationship_kwargs={"lazy": "selectin"}
    )
    performances: List["MatchPerformance"] = Relationship(
        back_populates="player", sa_relationship_kwargs={"lazy": "selectin"}
    )

    @field_validator("player_type")
    @classmethod
    def validate_player_type(cls, v):
        """Validate that player_type is one of the allowed values."""
        valid_types = ["BAT", "BOWL", "ALL", "WK"]
        if v not in valid_types:
            raise ValueError(f"Player type must be one of {valid_types}")
        return v


class UserPlayer(TimeStampedModel, table=True):
    """
    Model for players owned by users.

    Represents the ownership relationship between a user and a player
    in a specific Gully context, including purchase details and
    team role information.

    Attributes:
        id: Primary key
        user_id: Reference to the User
        player_id: Reference to the Player
        gully_id: Reference to the Gully context
        purchase_price: Price paid for this player
        purchase_date: When the player was purchased
        is_captain: Whether this player is the team captain
        is_vice_captain: Whether this player is the team vice-captain
        is_playing_xi: Whether this player is in the playing XI
    """

    __tablename__ = "user_players"

    id: Optional[int] = Field(default=None, primary_key=True, description="Primary key")
    user_id: int = Field(
        foreign_key="users.id", index=True, description="Reference to the User"
    )
    player_id: int = Field(
        foreign_key="players.id",
        index=True,
        unique=True,  # Unique constraint ensures 1-to-1
        description="Reference to the Player",
    )
    gully_id: int = Field(
        foreign_key="gullies.id",
        index=True,
        description="Reference to the Gully context",
    )
    purchase_price: Decimal = Field(
        default=0.0, description="Price paid for this player"
    )
    purchase_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=sqlalchemy.DateTime(timezone=True),
        description="When the player was purchased",
    )
    is_captain: bool = Field(
        default=False, description="Whether this player is the team captain"
    )
    is_vice_captain: bool = Field(
        default=False, description="Whether this player is the team vice-captain"
    )
    is_playing_xi: bool = Field(
        default=False, description="Whether this player is in the playing XI"
    )

    # Relationships
    user: "User" = Relationship(
        back_populates="owned_players", sa_relationship_kwargs={"lazy": "selectin"}
    )
    player: Player = Relationship(
        back_populates="user_player", sa_relationship_kwargs={"lazy": "selectin"}
    )
    gully: "Gully" = Relationship(
        back_populates="user_players", sa_relationship_kwargs={"lazy": "selectin"}
    )

    @field_validator("purchase_price")
    @classmethod
    def validate_purchase_price(cls, v):
        """Ensure purchase price is non-negative."""
        if v < 0:
            raise ValueError("Purchase price cannot be negative")
        return v


class PlayerStats(TimeStampedModel, table=True):
    """Cumulative player statistics."""

    __tablename__ = "player_stats"

    id: Optional[int] = Field(default=None, primary_key=True)
    player_id: int = Field(foreign_key="players.id")
    matches_played: int = Field(default=0)
    runs: int = Field(default=0)
    wickets: int = Field(default=0)
    highest_score: int = Field(default=0)
    best_bowling: str = Field(default="0/0")  # Format like "5/24"
    fantasy_points: float = Field(default=0.0)

    # Relationships
    player: Player = Relationship(back_populates="stats")


# Match Models
class Match(TimeStampedModel, table=True):
    """IPL match schedule and results."""

    __tablename__ = "matches"

    id: Optional[int] = Field(default=None, primary_key=True)
    date: str
    venue: str
    team1: str
    team2: str
    team1_score: Optional[str] = Field(default=None)  # Format like "164/8"
    team2_score: Optional[str] = Field(default=None)
    match_winner: Optional[str] = Field(default=None)
    player_of_the_match: Optional[str] = Field(default=None)

    # Relationships
    performances: List["MatchPerformance"] = Relationship(back_populates="match")


class MatchPerformance(TimeStampedModel, table=True):
    """Individual player performance in a match."""

    __tablename__ = "match_performances"

    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="matches.id")
    player_id: int = Field(foreign_key="players.id")
    runs: int = Field(default=0)
    balls_faced: int = Field(default=0)
    fours: int = Field(default=0)
    sixes: int = Field(default=0)
    wickets: int = Field(default=0)
    overs_bowled: float = Field(default=0.0)
    runs_conceded: int = Field(default=0)
    economy: float = Field(default=0.0)
    catches: int = Field(default=0)
    stumpings: int = Field(default=0)
    run_outs: int = Field(default=0)
    fantasy_points: float = Field(default=0.0)

    # Relationships
    match: Match = Relationship(back_populates="performances")
    player: Player = Relationship(back_populates="performances")


# Game Mechanics Models
class AuctionRound(TimeStampedModel, table=True):
    """Auction rounds for player bidding."""

    __tablename__ = "auction_rounds"

    id: Optional[int] = Field(default=None, primary_key=True)
    round_number: int = Field(unique=True, index=True)
    start_time: str
    end_time: str
    status: str = Field(default="pending")  # pending, active, completed

    # Relationships
    bids: List["AuctionBid"] = Relationship(back_populates="auction_round")


class AuctionBid(TimeStampedModel, table=True):
    """User bids for players in auction rounds."""

    __tablename__ = "auction_bids"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    player_id: int = Field(foreign_key="players.id")
    auction_round_id: int = Field(foreign_key="auction_rounds.id")
    bid_amount: Decimal
    status: str = Field(default="pending")  # pending, accepted, rejected

    # Relationships
    user: User = Relationship(back_populates="bids")
    player: Player = Relationship()
    auction_round: AuctionRound = Relationship(back_populates="bids")


class TransferWindow(TimeStampedModel, table=True):
    """Transfer windows for player trading."""

    __tablename__ = "transfer_windows"

    id: Optional[int] = Field(default=None, primary_key=True)
    start_time: str
    end_time: str
    status: str = Field(default="pending")  # pending, active, completed
    gully_id: int = Field(foreign_key="gullies.id")

    # Relationships
    listings: List["TransferListing"] = Relationship(back_populates="transfer_window")
    gully: "Gully" = Relationship(back_populates="transfer_windows")


class TransferListing(TimeStampedModel, table=True):
    """Player listings in transfer windows."""

    __tablename__ = "transfer_listings"

    id: Optional[int] = Field(default=None, primary_key=True)
    seller_id: int = Field(foreign_key="users.id")
    player_id: int = Field(foreign_key="players.id")
    transfer_window_id: int = Field(foreign_key="transfer_windows.id")
    asking_price: Decimal
    status: str = Field(default="active")  # active, sold, cancelled

    # Relationships
    seller: User = Relationship(back_populates="transfer_listings")
    player: Player = Relationship()
    transfer_window: TransferWindow = Relationship(back_populates="listings")
    bids: List["TransferBid"] = Relationship(back_populates="listing")


class TransferBid(TimeStampedModel, table=True):
    """Bids on transfer listings."""

    __tablename__ = "transfer_bids"

    id: Optional[int] = Field(default=None, primary_key=True)
    bidder_id: int = Field(foreign_key="users.id")
    listing_id: int = Field(foreign_key="transfer_listings.id")
    bid_amount: Decimal
    status: str = Field(default="pending")  # pending, accepted, rejected

    # Relationships
    bidder: User = Relationship(back_populates="transfer_bids")
    listing: TransferListing = Relationship(back_populates="bids")


class Gully(TimeStampedModel, table=True):
    """
    Model for fantasy cricket leagues (called 'Gullies').

    Represents a fantasy cricket league where users can participate,
    draft players, and compete against each other.

    Attributes:
        id: Primary key
        name: Name of the Gully
        telegram_group_id: Telegram group ID associated with this Gully
        status: Current status of the Gully (pending, active, completed)
    """

    __tablename__ = "gullies"

    id: Optional[int] = Field(default=None, primary_key=True, description="Primary key")
    name: str = Field(index=True, description="Name of the Gully")
    telegram_group_id: int = Field(
        unique=True,
        sa_type=BigInteger,
        description="Telegram group ID associated with this Gully",
    )
    status: str = Field(
        default="pending",
        description="Current status of the Gully (pending, active, completed)",
    )

    # Relationships
    participants: List["GullyParticipant"] = Relationship(
        back_populates="gully", sa_relationship_kwargs={"lazy": "selectin"}
    )
    user_players: List["UserPlayer"] = Relationship(
        back_populates="gully", sa_relationship_kwargs={"lazy": "selectin"}
    )
    transfer_windows: List["TransferWindow"] = Relationship(
        back_populates="gully", sa_relationship_kwargs={"lazy": "selectin"}
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """Validate that status is one of the allowed values."""
        valid_statuses = ["pending", "active", "completed"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        return v


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
        is_active: Whether this is the user's currently active gully
        last_active_at: When the user last interacted with this gully
        registration_complete: Whether the user has completed full registration
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
        default="member", description="User's role in this Gully (member, admin, owner)"
    )
    is_active: bool = Field(
        default=False, description="Whether this is the user's currently active gully"
    )
    last_active_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=sqlalchemy.DateTime(timezone=True),
        description="When the user last interacted with this gully",
    )
    registration_complete: bool = Field(
        default=False, description="Whether the user has completed full registration"
    )

    # Relationships
    gully: Optional["Gully"] = Relationship(
        back_populates="participants", sa_relationship_kwargs={"lazy": "selectin"}
    )
    user: Optional["User"] = Relationship(
        back_populates="gully_participations",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        """Validate that the role is one of the allowed values."""
        allowed_roles = ["member", "admin", "owner"]
        if v not in allowed_roles:
            raise ValueError(f"Role must be one of: {', '.join(allowed_roles)}")
        return v

    @field_validator("budget")
    @classmethod
    def validate_budget(cls, v):
        """Ensure budget is non-negative."""
        if v < 0:
            raise ValueError("Budget cannot be negative")
        return v

    @field_validator("points")
    @classmethod
    def validate_points(cls, v):
        """Validate that points is a non-negative integer."""
        if v < 0:
            raise ValueError("Points must be a non-negative integer")
        return v


class AdminPermission(TimeStampedModel, table=True):
    """
    Model for granular admin permissions.

    Defines specific permissions that can be assigned to admin users
    within a gully context.

    Attributes:
        id: Primary key
        gully_id: Reference to the Gully
        user_id: Reference to the User
        permission_type: Type of permission (user_mgmt, team_mgmt, auction_mgmt, etc.)
        is_active: Whether this permission is active
    """

    __tablename__ = "admin_permissions"

    id: Optional[int] = Field(default=None, primary_key=True, description="Primary key")
    gully_id: int = Field(
        foreign_key="gullies.id", description="Reference to the Gully"
    )
    user_id: int = Field(foreign_key="users.id", description="Reference to the User")
    permission_type: str = Field(description="Type of permission")
    is_active: bool = Field(
        default=True, description="Whether this permission is active"
    )

    # Relationships
    gully: Optional["Gully"] = Relationship(sa_relationship_kwargs={"lazy": "selectin"})
    user: Optional["User"] = Relationship(sa_relationship_kwargs={"lazy": "selectin"})

    @field_validator("permission_type")
    @classmethod
    def validate_permission_type(cls, v):
        """Validate that the permission type is one of the allowed values."""
        allowed_types = [
            "user_management",
            "team_management",
            "auction_management",
            "match_management",
            "settings_management",
            "all",  # Special permission that grants all access
        ]
        if v not in allowed_types:
            raise ValueError(
                f"Permission type must be one of: {', '.join(allowed_types)}"
            )
        return v
