from typing import Optional
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator
from sqlalchemy import TypeDecorator, DateTime, BigInteger, event
import sqlalchemy


# Enum Classes
class PlayerType(str, Enum):
    """Enum for player types."""

    BATSMAN = "BAT"
    BOWLER = "BOWL"
    ALL_ROUNDER = "AR"
    WICKET_KEEPER = "WK"


class ParticipantRole(str, Enum):
    """Enum for participant roles in a Gully."""

    MEMBER = "member"
    ADMIN = "admin"


class AuctionType(str, Enum):
    """Enum for auction types."""

    NEW_PLAYER = "new_player"  # Initial auction for new players
    TRANSFER = "transfer"  # Weekly transfer window auction


class AuctionStatus(str, Enum):
    """Enum for auction status."""

    PENDING = "pending"  # Waiting for auction to start
    BIDDING = "bidding"  # Active bidding phase
    COMPLETED = "completed"  # Auction has concluded


class GullyStatus(str, Enum):
    """Enum for Gully (league) status."""

    DRAFT = "draft"  # Round 0 in progress, participants picking initial squads
    AUCTION = "auction"  # Auction round is live for contested players from Round 0
    TRANSFERS = "transfers"  # Mid-season transfer window is open
    COMPLETED = "completed"  # League is finished, no further actions allowed


class UserPlayerStatus(str, Enum):
    """Enum for UserPlayer (player ownership) status."""

    LOCKED = "locked"  # User submitted Round 0 squad, player is uncontested
    CONTESTED = (
        "contested"  # User submitted Round 0 squad, player is contested by others
    )
    OWNED = "owned"  # User definitively owns this player (won auction or uncontested)


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
        if v not in [pt.value for pt in PlayerType]:
            raise ValueError(
                f"Player type must be one of {[pt.value for pt in PlayerType]}"
            )
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
        has_submitted_squad: Whether user has submitted their initial squad
        submission_time: When the user submitted their squad
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
        default=ParticipantRole.MEMBER.value,
        description="User's role in this Gully (member, admin)",
    )
    has_submitted_squad: bool = Field(
        default=False, description="Whether user has submitted their initial squad"
    )
    submission_time: Optional[datetime] = Field(
        default=None,
        sa_type=sqlalchemy.DateTime(timezone=True),
        description="When the user submitted their squad",
    )

    # Define unique constraint for user_id and gully_id
    __table_args__ = (
        sqlalchemy.UniqueConstraint("user_id", "gully_id", name="uq_user_gully"),
    )

    # Relationships will be defined after all classes are defined

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        """Validate that role is one of the allowed values."""
        if v not in [role.value for role in ParticipantRole]:
            raise ValueError(
                f"Role must be one of {[role.value for role in ParticipantRole]}"
            )
        return v

    @field_validator("budget")
    @classmethod
    def validate_budget(cls, v):
        """Validate that budget is non-negative."""
        if v < 0:
            raise ValueError("Budget must be non-negative")
        return v

    @field_validator("points")
    @classmethod
    def validate_points(cls, v):
        """Validate that points is non-negative."""
        if v < 0:
            raise ValueError("Points must be non-negative")
        return v


class Gully(TimeStampedModel, table=True):
    """
    Model for fantasy cricket leagues (called 'Gullies').

    Represents a fantasy cricket league where users can participate,
    draft players, and compete against each other.

    Attributes:
        id: Primary key
        name: Name of the Gully
        telegram_group_id: Telegram group ID associated with this Gully
        status: Current status of the Gully (draft, auction, transfers, completed)
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
        default=GullyStatus.DRAFT.value,
        index=True,
        description="Current status of the Gully (draft, auction, transfers, completed)",
    )

    # Relationships will be defined after all classes are defined

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """Validate that status is one of the allowed values."""
        if v not in [status.value for status in GullyStatus]:
            raise ValueError(
                f"Status must be one of {[status.value for status in GullyStatus]}"
            )
        return v


# Add this new model after the existing models
class DraftSelection(TimeStampedModel, table=True):
    """
    Model for tracking player selections during the draft phase.
    Once draft is complete, successful selections are converted to ParticipantPlayer records.
    """

    __tablename__ = "draft_selections"

    id: Optional[int] = Field(default=None, primary_key=True)
    gully_participant_id: int = Field(foreign_key="gully_participants.id", index=True)
    player_id: int = Field(foreign_key="players.id", index=True)
    selected_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=sqlalchemy.DateTime(timezone=True),
    )

    # Add composite index for efficient querying
    __table_args__ = (
        sqlalchemy.Index(
            "ix_draft_selections_gully_player", "gully_participant_id", "player_id"
        ),
    )

    # Relationships will be defined after all classes are defined


class ParticipantPlayer(TimeStampedModel, table=True):
    """
    Model for player ownership by participants after the draft phase.
    """

    __tablename__ = "participant_players"

    id: Optional[int] = Field(default=None, primary_key=True)
    gully_participant_id: int = Field(foreign_key="gully_participants.id", index=True)
    player_id: int = Field(foreign_key="players.id", index=True)
    purchase_price: Decimal = Field(description="Price paid for this player")
    purchase_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=sqlalchemy.DateTime(timezone=True),
    )
    is_captain: bool = Field(default=False)
    is_vice_captain: bool = Field(default=False)
    is_playing_xi: bool = Field(default=True)
    status: str = Field(
        default=UserPlayerStatus.LOCKED.value,  # Changed default from DRAFT to LOCKED
        index=True,
        description="Current status of player ownership (locked, contested, owned)",
    )

    # Define unique constraint for player_id and gully_participant_id
    __table_args__ = (
        sqlalchemy.UniqueConstraint(
            "player_id", "gully_participant_id", name="uq_player_participant"
        ),
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """Validate that status is one of the allowed values."""
        allowed_values = [
            UserPlayerStatus.LOCKED.value,
            UserPlayerStatus.CONTESTED.value,
            UserPlayerStatus.OWNED.value,
        ]
        if v not in allowed_values:
            raise ValueError(f"Status must be one of {allowed_values}")
        return v


class AuctionQueue(TimeStampedModel, table=True):
    """
    Model for tracking players in auction queue.

    Represents players that are queued for auction or transfer in a specific Gully,
    including auction type, status, and when they were listed.

    Attributes:
        id: Primary key
        gully_id: Reference to the Gully
        player_id: Reference to the Player
        seller_participant_id: Reference to the GullyParticipant who is selling the player (for transfer auctions)
        auction_type: Type of auction (new_player or transfer)
        status: Current status of the auction (pending, bidding, completed)
        listed_at: When the player was listed for auction
    """

    __tablename__ = "auction_queue"

    id: Optional[int] = Field(default=None, primary_key=True)
    gully_id: int = Field(foreign_key="gullies.id", index=True)
    player_id: int = Field(foreign_key="players.id", index=True)
    seller_participant_id: Optional[int] = Field(
        default=None,
        foreign_key="gully_participants.id",
        index=True,
        description="Seller of the player (for transfer auctions)",
    )
    auction_type: str = Field(
        default=AuctionType.TRANSFER.value,
        description="Type of auction (new_player or transfer)",
    )
    status: str = Field(
        default=AuctionStatus.PENDING.value,
        description="Status of auction (pending, bidding, completed)",
    )
    listed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=sqlalchemy.DateTime(timezone=True),
    )

    # Add composite index for gully_id and status
    __table_args__ = (
        sqlalchemy.Index("ix_auction_queue_gully_status", "gully_id", "status"),
        # Add CHECK constraint to ensure auction_type is valid
        sqlalchemy.CheckConstraint(
            f"auction_type IN {tuple(t.value for t in AuctionType)}",
            name="ck_auction_type",
        ),
        # Add CHECK constraint to ensure status is valid
        sqlalchemy.CheckConstraint(
            f"status IN {tuple(s.value for s in AuctionStatus)}",
            name="ck_auction_status",
        ),
    )

    # Relationships will be defined after all classes are defined

    @field_validator("auction_type")
    @classmethod
    def validate_auction_type(cls, v):
        """Validate that auction_type is one of the allowed values."""
        if v not in [t.value for t in AuctionType]:
            raise ValueError(
                f"Auction type must be one of {[t.value for t in AuctionType]}"
            )
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """Validate that status is one of the allowed values."""
        if v not in [s.value for s in AuctionStatus]:
            raise ValueError(
                f"Status must be one of {[s.value for s in AuctionStatus]}"
            )
        return v


class TransferMarket(TimeStampedModel, table=True):
    """
    Model for tracking players in transfer market.

    Represents players available for purchase in the transfer market for a specific Gully,
    including their fair price and when they were listed.

    Attributes:
        id: Primary key
        gully_id: Reference to the Gully
        player_id: Reference to the Player
        fair_price: Fair price for the player
        listed_at: When the player was listed in the transfer market
    """

    __tablename__ = "transfer_market"

    id: Optional[int] = Field(default=None, primary_key=True)
    gully_id: int = Field(foreign_key="gullies.id", index=True)
    player_id: int = Field(foreign_key="players.id", index=True)
    fair_price: Decimal = Field(description="Fair price for the player")
    listed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=sqlalchemy.DateTime(timezone=True),
    )

    # Add composite index for gully_id and listed_at
    __table_args__ = (
        sqlalchemy.Index("ix_transfer_market_gully_listed", "gully_id", "listed_at"),
    )

    # Relationships will be defined after all classes are defined

    @field_validator("fair_price")
    @classmethod
    def validate_fair_price(cls, v):
        """Validate that fair_price is non-negative."""
        if v < 0:
            raise ValueError("Fair price must be non-negative")
        return v


class BankTransaction(TimeStampedModel, table=True):
    """
    Model for tracking financial transactions.

    Represents financial transactions related to player transfers in a specific Gully,
    including the seller, player, and sale details.

    Attributes:
        id: Primary key
        gully_id: Reference to the Gully
        player_id: Reference to the Player
        seller_participant_id: Reference to the GullyParticipant who sold the player
        sale_price: Price at which the player was sold
        sale_time: When the transaction occurred
    """

    __tablename__ = "bank_transactions"

    id: Optional[int] = Field(default=None, primary_key=True)
    gully_id: int = Field(foreign_key="gullies.id", index=True)
    player_id: int = Field(foreign_key="players.id", index=True)
    seller_participant_id: int = Field(foreign_key="gully_participants.id", index=True)
    sale_price: Decimal = Field(description="Sale price of the player")
    sale_time: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=sqlalchemy.DateTime(timezone=True),
    )

    # Add composite index for gully_id and sale_time
    __table_args__ = (
        sqlalchemy.Index("ix_bank_transactions_gully_time", "gully_id", "sale_time"),
    )

    # Relationships will be defined after all classes are defined

    @field_validator("sale_price")
    @classmethod
    def validate_sale_price(cls, v):
        """Validate that sale_price is non-negative."""
        if v < 0:
            raise ValueError("Sale price must be non-negative")
        return v


class Bid(TimeStampedModel, table=True):
    """
    Model for tracking bids on auction items.

    Represents a bid placed by a user on a player in the auction queue,
    including the bid amount and when it was placed.

    Attributes:
        id: Primary key
        auction_queue_id: Reference to the AuctionQueue item
        gully_participant_id: Reference to the GullyParticipant who placed the bid
        bid_amount: Amount of the bid
        bid_time: When the bid was placed
    """

    __tablename__ = "bids"

    id: Optional[int] = Field(default=None, primary_key=True)
    auction_queue_id: int = Field(foreign_key="auction_queue.id", index=True)
    gully_participant_id: int = Field(foreign_key="gully_participants.id", index=True)
    bid_amount: Decimal = Field(description="Bid amount")
    bid_time: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=sqlalchemy.DateTime(timezone=True),
    )

    # Define unique constraint and composite index
    __table_args__ = (
        sqlalchemy.UniqueConstraint(
            "auction_queue_id",
            "gully_participant_id",
            name="uq_bid_auction_participant",
        ),
        sqlalchemy.Index("ix_bids_auction_amount", "auction_queue_id", "bid_amount"),
        # Note: PostgreSQL doesn't support subqueries in CHECK constraints
        # The security check to prevent users from bidding on their own listed players
        # will be implemented at the application level
    )

    # Relationships will be defined after all classes are defined

    @field_validator("bid_amount")
    @classmethod
    def validate_bid_amount(cls, v):
        """Validate that bid_amount is positive."""
        if v <= 0:
            raise ValueError("Bid amount must be positive")
        return v


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


# Add property to User model for easy access to gully IDs
def get_gully_ids(self) -> list[int]:
    """Return a list of gully IDs that the user is a part of."""
    return [participation.gully_id for participation in self.gully_participations]


# Attach the property to the User class
User.gully_ids = property(get_gully_ids)

# GullyParticipant relationships
GullyParticipant.user = Relationship(back_populates="gully_participations")
GullyParticipant.gully = Relationship(back_populates="participants")
GullyParticipant.bank_transactions = Relationship(
    sa_relationship_kwargs={"lazy": "selectin"}, back_populates="seller_participant"
)
GullyParticipant.participant_players = Relationship(
    sa_relationship_kwargs={"lazy": "selectin"}, back_populates="gully_participant"
)
GullyParticipant.draft_selections = Relationship(
    sa_relationship_kwargs={"lazy": "selectin"}, back_populates="gully_participant"
)

# Gully relationships
Gully.participants = Relationship(
    sa_relationship_kwargs={"lazy": "selectin"}, back_populates="gully"
)
Gully.users = Relationship(
    link_model=GullyParticipant,
    sa_relationship_kwargs={"lazy": "selectin"},
    back_populates="gullies",
)
Gully.auction_queue_items = Relationship(
    sa_relationship_kwargs={"lazy": "selectin"}, back_populates="gully"
)
Gully.transfer_market_items = Relationship(
    sa_relationship_kwargs={"lazy": "selectin"}, back_populates="gully"
)
Gully.bank_transactions = Relationship(
    sa_relationship_kwargs={"lazy": "selectin"}, back_populates="gully"
)

# Player relationships
Player.participant_player = Relationship(
    sa_relationship_kwargs={"lazy": "selectin"}, back_populates="player"
)
Player.draft_selections = Relationship(
    sa_relationship_kwargs={"lazy": "selectin"}, back_populates="player"
)

# ParticipantPlayer relationships
ParticipantPlayer.gully_participant = Relationship(back_populates="participant_players")
ParticipantPlayer.player = Relationship(back_populates="participant_player")

# DraftSelection relationships
DraftSelection.gully_participant = Relationship(back_populates="draft_selections")
DraftSelection.player = Relationship(back_populates="draft_selections")

# AuctionQueue relationships
AuctionQueue.gully = Relationship(back_populates="auction_queue_items")
AuctionQueue.player = Relationship()
AuctionQueue.seller_participant = Relationship()
AuctionQueue.bids = Relationship(back_populates="auction_queue_item")

# TransferMarket relationships
TransferMarket.gully = Relationship(back_populates="transfer_market_items")
TransferMarket.player = Relationship()

# BankTransaction relationships
BankTransaction.gully = Relationship(back_populates="bank_transactions")
BankTransaction.player = Relationship()
BankTransaction.seller_participant = Relationship(back_populates="bank_transactions")

# Bid relationships
Bid.auction_queue_item = Relationship(back_populates="bids")
Bid.gully_participant = Relationship()


# Add computed properties
def get_highest_bid(self) -> Optional["Bid"]:
    """Return the highest bid for this auction item."""
    if not self.bids:
        return None
    return max(self.bids, key=lambda bid: (bid.bid_amount, -bid.bid_time.timestamp()))


AuctionQueue.highest_bid = property(get_highest_bid)


def get_current_owner_in_gully(self, gully_id: int) -> Optional["User"]:
    """Return the current owner of this player in the specified gully."""
    if not hasattr(self, "participant_player") or self.participant_player is None:
        return None

    for pp in self.participant_players:
        # Get the gully_id from the participant
        participant_gully_id = pp.gully_participant.gully_id
        if participant_gully_id == gully_id:
            return pp.gully_participant.user
    return None


# Attach the method to the Player class
Player.get_current_owner_in_gully = get_current_owner_in_gully


# Event listener to update the updated_at field when a record is modified
@event.listens_for(SQLModel, "before_update", propagate=True)
def receive_before_update(mapper, connection, target):
    """Update the updated_at field when a record is modified."""
    target.updated_at = datetime.now(timezone.utc)
