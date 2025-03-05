from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship


# Base Models
class TimeStampedModel(SQLModel):
    """Base model with created and updated timestamps."""

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# User Models
class User(TimeStampedModel, table=True):
    """User model for fantasy cricket managers."""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    telegram_id: int = Field(unique=True, index=True)
    username: str = Field(index=True)
    full_name: str
    budget: Decimal = Field(default=100.0)
    total_points: float = Field(default=0.0)
    is_admin: bool = Field(default=False)

    # Relationships
    player_links: List["UserPlayerLink"] = Relationship(back_populates="user")
    bids: List["AuctionBid"] = Relationship(back_populates="user")
    transfer_listings: List["TransferListing"] = Relationship(back_populates="seller")
    transfer_bids: List["TransferBid"] = Relationship(back_populates="bidder")

    # Add field to track free bids used in current window
    free_bids_used: int = Field(default=0)


# Player Models
class Player(TimeStampedModel, table=True):
    """Player model for IPL cricketers."""

    __tablename__ = "players"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    team: str = Field(index=True)
    player_type: str = Field(index=True)  # BAT, BOWL, ALL, WK
    base_price: Optional[Decimal] = Field(default=None)
    sold_price: Optional[Decimal] = Field(default=None)

    # Relationships
    user_links: List["UserPlayerLink"] = Relationship(back_populates="player")
    stats: List["PlayerStats"] = Relationship(back_populates="player")
    performances: List["MatchPerformance"] = Relationship(back_populates="player")


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
    date: datetime
    venue: str
    team1: str
    team2: str
    team1_score: Optional[str] = Field(default=None)  # Format like "164/8"
    team2_score: Optional[str] = Field(default=None)
    match_winner: Optional[str] = Field(default=None)
    player_of_the_match: Optional[str] = Field(default=None)

    # Relationships
    performances: List["MatchPerformance"] = Relationship(back_populates="match")
    polls: List["MatchPoll"] = Relationship(back_populates="match")


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
class UserPlayerLink(SQLModel, table=True):
    """Link table for users and their selected players."""

    __tablename__ = "user_player_links"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    player_id: int = Field(foreign_key="players.id")
    is_captain: bool = Field(default=False)
    is_vice_captain: bool = Field(default=False)
    is_playing_xi: bool = Field(default=False)
    round_number: int = Field(default=0)

    # Relationships
    user: User = Relationship(back_populates="player_links")
    player: Player = Relationship(back_populates="user_links")


class AuctionRound(TimeStampedModel, table=True):
    """Auction rounds for player bidding."""

    __tablename__ = "auction_rounds"

    id: Optional[int] = Field(default=None, primary_key=True)
    round_number: int = Field(unique=True, index=True)
    start_time: datetime
    end_time: datetime
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
    auction_round: AuctionRound = Relationship(back_populates="bids")


class TransferWindow(TimeStampedModel, table=True):
    """Model for weekly transfer windows."""

    __tablename__ = "transfer_windows"

    id: Optional[int] = Field(default=None, primary_key=True)
    week_number: int = Field(index=True)  # Week number in the IPL season
    start_time: datetime = Field()
    end_time: datetime = Field()
    status: str = Field(default="pending")  # pending, active, closed

    # Relationships
    transfer_listings: List["TransferListing"] = Relationship(
        back_populates="transfer_window"
    )


class TransferListing(TimeStampedModel, table=True):
    """Model for players listed for transfer."""

    __tablename__ = "transfer_listings"

    id: Optional[int] = Field(default=None, primary_key=True)
    transfer_window_id: int = Field(foreign_key="transfer_windows.id", index=True)
    player_id: int = Field(foreign_key="players.id", index=True)
    seller_id: int = Field(foreign_key="users.id", index=True)
    min_price: Decimal = Field(default=0.0)
    status: str = Field(default="available")  # available, sold, cancelled

    # Relationships
    transfer_window: Optional[TransferWindow] = Relationship(
        back_populates="transfer_listings"
    )
    player: Optional[Player] = Relationship()
    seller: Optional[User] = Relationship(back_populates="transfer_listings")
    bids: List["TransferBid"] = Relationship(back_populates="listing")


class TransferBid(TimeStampedModel, table=True):
    """Model for transfer bids."""

    __tablename__ = "transfer_bids"

    id: Optional[int] = Field(default=None, primary_key=True)
    transfer_listing_id: int = Field(foreign_key="transfer_listings.id", index=True)
    bidder_id: int = Field(foreign_key="users.id", index=True)
    bid_amount: Decimal = Field()
    status: str = Field(default="pending")  # pending, accepted, rejected
    is_free_bid: bool = Field(default=True)  # Whether this is a free bid or paid bid

    # Relationships
    listing: Optional[TransferListing] = Relationship(back_populates="bids")
    bidder: Optional[User] = Relationship(back_populates="transfer_bids")


# Additional Game Features
class MatchPoll(TimeStampedModel, table=True):
    """Polls for match predictions."""

    __tablename__ = "match_polls"

    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="matches.id")
    poll_question: str
    poll_options: str  # JSON string of options

    # Relationships
    match: Match = Relationship(back_populates="polls")
    results: List["PollResult"] = Relationship(back_populates="poll")


class PollResult(TimeStampedModel, table=True):
    """User responses to match polls."""

    __tablename__ = "poll_results"

    id: Optional[int] = Field(default=None, primary_key=True)
    poll_id: int = Field(foreign_key="match_polls.id")
    user_id: int = Field(foreign_key="users.id")
    selected_option: str

    # Relationships
    poll: MatchPoll = Relationship(back_populates="results")
