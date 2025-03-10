from datetime import datetime
from typing import Dict, List, Optional, Any
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import DECIMAL
from pydantic import BaseModel, field_validator, ConfigDict

from src.db.models.models import TimeStampedModel


# Define the link table using SQLModel's approach
class CricsheetPlayerMatch(SQLModel, table=True):
    """Link table for players and matches."""

    __tablename__ = "cricsheet_player_matches"

    # Define foreign keys with proper references
    player_id: int = Field(foreign_key="cricsheet_players.id", primary_key=True)
    match_id: int = Field(foreign_key="cricsheet_matches.id", primary_key=True)
    team_name: str = Field(description="Team name in this match")


class CricsheetPlayer(TimeStampedModel, table=True):
    """Model for cricket players."""

    __tablename__ = "cricsheet_players"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, description="Player's full name")
    registry_id: Optional[str] = Field(
        default=None, index=True, unique=True, description="Registry ID from Cricsheet"
    )
    team_name: Optional[str] = Field(
        default=None, index=True, description="Primary team name"
    )

    # Relationships
    matches: List["CricsheetMatch"] = Relationship(
        back_populates="players", link_model=CricsheetPlayerMatch
    )


class CricsheetMatch(TimeStampedModel, table=True):
    """Model for cricket match information."""

    __tablename__ = "cricsheet_matches"

    # Add model_config to allow arbitrary types
    model_config = {"arbitrary_types_allowed": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: str = Field(
        index=True, unique=True, description="Unique match identifier"
    )
    season: int = Field(index=True, description="Season/year of the match")
    date: datetime = Field(index=True, description="Date of the match")
    venue: str = Field(description="Match venue")
    city: Optional[str] = Field(default=None, description="City where match was played")
    event: str = Field(description="Tournament/event name (e.g., IPL)")
    gender: str = Field(description="Gender of players (male/female)")

    # Teams
    team1: str = Field(description="First team name")
    team2: str = Field(description="Second team name")

    # Toss information
    toss_winner: str = Field(description="Team that won the toss")
    toss_decision: str = Field(description="Toss decision (bat/field)")

    # Result information
    winner: Optional[str] = Field(default=None, description="Winning team name")
    winner_runs: Optional[int] = Field(
        default=None, description="Winning margin in runs"
    )
    winner_wickets: Optional[int] = Field(
        default=None, description="Winning margin in wickets"
    )
    player_of_match: Optional[str] = Field(
        default=None, description="Player of the match"
    )

    # Officials
    umpire1: Optional[str] = Field(default=None, description="First umpire")
    umpire2: Optional[str] = Field(default=None, description="Second umpire")
    tv_umpire: Optional[str] = Field(default=None, description="TV umpire")
    reserve_umpire: Optional[str] = Field(default=None, description="Reserve umpire")
    match_referee: Optional[str] = Field(default=None, description="Match referee")

    # Relationships
    players: List[CricsheetPlayer] = Relationship(
        back_populates="matches", link_model=CricsheetPlayerMatch
    )
    deliveries: List["CricsheetDelivery"] = Relationship(back_populates="match")

    @field_validator("toss_decision")
    @classmethod
    def validate_toss_decision(cls, v):
        valid_decisions = ["bat", "field"]
        if v not in valid_decisions:
            raise ValueError(f"Toss decision must be one of {valid_decisions}")
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        valid_genders = ["male", "female"]
        if v not in valid_genders:
            raise ValueError(f"Gender must be one of {valid_genders}")
        return v


class CricsheetDelivery(TimeStampedModel, table=True):
    """Model for ball-by-ball data in cricket matches."""

    __tablename__ = "cricsheet_deliveries"

    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: str = Field(
        foreign_key="cricsheet_matches.match_id",
        index=True,
        description="Reference to match",
    )
    innings: int = Field(index=True, description="Innings number (1 or 2)")
    ball: Decimal = Field(
        description="Ball number (over.ball)",
        sa_column=Column(DECIMAL(precision=3, scale=1), index=True),
    )

    # Teams
    batting_team: str = Field(description="Batting team name")
    bowling_team: str = Field(description="Bowling team name")

    # Players
    striker: str = Field(description="Batsman on strike")
    non_striker: str = Field(description="Batsman at non-striker's end")
    bowler: str = Field(description="Bowler")

    # Runs
    runs_off_bat: int = Field(default=0, description="Runs scored by batsman")
    extras: int = Field(default=0, description="Total extras")

    # Extras breakdown
    wides: Optional[int] = Field(default=None, description="Wide balls")
    noballs: Optional[int] = Field(default=None, description="No balls")
    byes: Optional[int] = Field(default=None, description="Byes")
    legbyes: Optional[int] = Field(default=None, description="Leg byes")
    penalty: Optional[int] = Field(default=None, description="Penalty runs")

    # Wicket information
    wicket_type: Optional[str] = Field(default=None, description="Type of dismissal")
    player_dismissed: Optional[str] = Field(
        default=None, description="Player who was dismissed"
    )
    other_wicket_type: Optional[str] = Field(
        default=None, description="Secondary wicket type"
    )
    other_player_dismissed: Optional[str] = Field(
        default=None, description="Secondary player dismissed"
    )

    # Relationships
    match: CricsheetMatch = Relationship(back_populates="deliveries")

    @property
    def total_runs(self) -> int:
        """Calculate total runs from this delivery."""
        return self.runs_off_bat + self.extras

    @property
    def over_number(self) -> int:
        """Extract over number from ball."""
        return int(self.ball)

    @property
    def ball_in_over(self) -> int:
        """Extract ball number within the over."""
        return int((self.ball % 1) * 10)


# Pydantic models for API responses and data processing
class CricsheetMatchModel(BaseModel):
    """
    Pydantic model for match data from Cricsheet.

    Attributes:
        key: Unique identifier for the match
        date: Date of the match
        venue: Match venue
        city: City where match was played
        competition: Competition name (e.g., "IPL")
        match_type: Type of match (e.g., "T20")
        team1: First team
        team2: Second team
        toss_winner: Team that won the toss
        toss_decision: Decision after winning toss (bat/field)
        winner: Match winner
        result: Result type (e.g., "runs", "wickets")
        result_margin: Margin of victory
    """

    key: str = Field(..., description="Unique match identifier")
    date: datetime = Field(..., description="Match date")
    venue: str = Field(..., description="Match venue")
    city: Optional[str] = Field(None, description="City")
    competition: str = Field(..., description="Competition name")
    match_type: str = Field(..., description="Type of match")
    team1: str = Field(..., description="First team")
    team2: str = Field(..., description="Second team")
    toss_winner: str = Field(..., description="Toss winner")
    toss_decision: str = Field(..., description="Toss decision")
    winner: Optional[str] = Field(None, description="Match winner")
    result: Optional[str] = Field(None, description="Result type")
    result_margin: Optional[int] = Field(None, description="Margin of victory")

    @field_validator("toss_decision")
    @classmethod
    def validate_toss_decision(cls, v):
        valid_decisions = ["bat", "field"]
        if v not in valid_decisions:
            raise ValueError(f"Toss decision must be one of {valid_decisions}")
        return v

    @field_validator("match_type")
    @classmethod
    def validate_match_type(cls, v):
        valid_types = ["Test", "ODI", "T20", "IT20"]
        if v not in valid_types:
            raise ValueError(f"Match type must be one of {valid_types}")
        return v

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "key": "ipl_2020_01",
                "date": "2020-09-19T00:00:00",
                "venue": "Dubai International Cricket Stadium",
                "city": "Dubai",
                "competition": "IPL",
                "match_type": "T20",
                "team1": "Mumbai Indians",
                "team2": "Chennai Super Kings",
                "toss_winner": "Mumbai Indians",
                "toss_decision": "bat",
                "winner": "Chennai Super Kings",
                "result": "runs",
                "result_margin": 5,
            }
        },
    )

    def to_db_model(self) -> Dict[str, Any]:
        """Convert Cricsheet match to database model format."""
        return {
            "match_id": self.key,
            "date": self.date.date(),
            "venue": self.venue,
            "city": self.city,
            "event": self.competition,
            "team1": self.team1,
            "team2": self.team2,
            "toss_winner": self.toss_winner,
            "toss_decision": self.toss_decision,
            "winner": self.winner,
            "winner_runs": self.result_margin if self.result == "runs" else None,
            "winner_wickets": self.result_margin if self.result == "wickets" else None,
        }


class CricsheetDeliveryModel(BaseModel):
    """
    Pydantic model for ball-by-ball data from Cricsheet.

    Attributes:
        match_id: Reference to the match
        innings: Innings number (1 or 2)
        ball: Ball number (over.ball)
        batting_team: Batting team name
        bowling_team: Bowling team name
        striker: Batsman on strike
        non_striker: Batsman at non-striker's end
        bowler: Bowler
        runs_off_bat: Runs scored by batsman
        extras: Total extras
        wicket_type: Type of dismissal
        player_dismissed: Player who was dismissed
    """

    match_id: str = Field(..., description="Match identifier")
    innings: int = Field(..., description="Innings number")
    ball: str = Field(..., description="Ball number (over.ball)")
    batting_team: str = Field(..., description="Batting team name")
    bowling_team: str = Field(..., description="Bowling team name")
    striker: str = Field(..., description="Batsman on strike")
    non_striker: str = Field(..., description="Batsman at non-striker's end")
    bowler: str = Field(..., description="Bowler")
    runs_off_bat: int = Field(default=0, description="Runs scored by batsman")
    extras: int = Field(default=0, description="Total extras")
    wides: Optional[int] = Field(default=None, description="Wide balls")
    noballs: Optional[int] = Field(default=None, description="No balls")
    byes: Optional[int] = Field(default=None, description="Byes")
    legbyes: Optional[int] = Field(default=None, description="Leg byes")
    wicket_type: Optional[str] = Field(default=None, description="Type of dismissal")
    player_dismissed: Optional[str] = Field(
        default=None, description="Player who was dismissed"
    )

    @field_validator("innings")
    @classmethod
    def validate_innings(cls, v):
        if v not in [1, 2]:
            raise ValueError("Innings must be 1 or 2")
        return v

    @field_validator("runs_off_bat", "extras")
    @classmethod
    def validate_non_negative_values(cls, v):
        if v < 0:
            raise ValueError("Value must be non-negative")
        return v

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "match_id": "ipl_2020_01",
                "innings": 1,
                "ball": "0.1",
                "batting_team": "Mumbai Indians",
                "bowling_team": "Chennai Super Kings",
                "striker": "Rohit Sharma",
                "non_striker": "Quinton de Kock",
                "bowler": "Deepak Chahar",
                "runs_off_bat": 4,
                "extras": 0,
                "wicket_type": None,
                "player_dismissed": None,
            }
        },
    )

    def to_db_model(self) -> Dict[str, Any]:
        """Convert to database model format."""
        return {
            "match_id": self.match_id,
            "innings": self.innings,
            "ball": Decimal(self.ball),
            "batting_team": self.batting_team,
            "bowling_team": self.bowling_team,
            "striker": self.striker,
            "non_striker": self.non_striker,
            "bowler": self.bowler,
            "runs_off_bat": self.runs_off_bat,
            "extras": self.extras,
            "wides": self.wides,
            "noballs": self.noballs,
            "byes": self.byes,
            "legbyes": self.legbyes,
            "wicket_type": self.wicket_type,
            "player_dismissed": self.player_dismissed,
        }
