from enum import Enum
from typing import Optional, List, Dict
from sqlmodel import Field, Relationship
from datetime import datetime
from pydantic import field_validator, BaseModel, computed_field
from sqlalchemy import Column, JSON, UniqueConstraint
from src.db.models.models import TimeStampedModel
from sqlalchemy import DateTime
import sqlalchemy


# Team Enumeration
class TeamEnum(str, Enum):
    CSK = "Chennai Super Kings"
    DC = "Delhi Capitals"
    GT = "Gujarat Titans"
    KKR = "Kolkata Knight Riders"
    LSG = "Lucknow Super Giants"
    MI = "Mumbai Indians"
    PBKS = "Punjab Kings"
    RCB = "Royal Challengers Bengaluru"
    RR = "Rajasthan Royals"
    SRH = "Sunrisers Hyderabad"

    @classmethod
    def get_short_code(cls, full_name: str) -> Optional[str]:
        """Get the short code for a team name"""
        for code, name in cls.__members__.items():
            if name.value == full_name:
                return code
        return None


# Pydantic Model for API Data
class MatchInput(BaseModel):
    MatchNumber: int
    RoundNumber: int
    DateUtc: datetime
    Location: str
    HomeTeam: str
    AwayTeam: str
    Group: Optional[str] = None
    HomeTeamScore: Optional[int] = None
    AwayTeamScore: Optional[int] = None

    @field_validator("DateUtc", mode="before")
    @classmethod
    def parse_datetime(cls, value):
        """Parse datetime string if needed"""
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value


# SQLModel for balanced rounds
class IPLRound(TimeStampedModel, table=True):
    """Model for optimized IPL match rounds with balanced team participation"""

    __tablename__ = "ipl_balanced_rounds"

    # Standard auto-incrementing primary key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Business identifiers with unique constraint
    round_number: int = Field(index=True)
    season: int = Field(default=2025, index=True)

    # Create a unique constraint on round_number + season
    __table_args__ = (
        UniqueConstraint("round_number", "season", name="uix_round_season"),
    )

    # Match boundary information - with more intuitive naming
    first_match: int = Field(nullable=False)  # First match in this round (inclusive)
    last_match: int = Field(nullable=False)  # Last match in this round (inclusive)
    matches_in_round: int = Field(nullable=False)

    # Balance metrics (converted to integers)
    min_team_matches: int = Field(nullable=False)
    max_team_matches: int = Field(nullable=False)
    is_balanced: bool = Field(nullable=False)

    # Replace individual team columns with a single JSON column
    team_matches: Dict[str, int] = Field(sa_column=Column(JSON), default_factory=dict)

    # Timestamps directly from matches - make these timezone-aware
    start_date_utc: Optional[datetime] = Field(
        nullable=True,
        sa_type=sqlalchemy.DateTime(timezone=True),
    )
    end_date_utc: Optional[datetime] = Field(
        nullable=True,
        sa_type=sqlalchemy.DateTime(timezone=True),
    )
    days_in_round: Optional[int] = Field(nullable=True)

    # Simplified relationship - use regular foreign key relationship
    matches: List["IPLMatch"] = Relationship(back_populates="round")

    @computed_field
    def match_range(self) -> str:
        """Return a string representation of the match range for this round"""
        return f"Match #{self.first_match}-{self.last_match}"

    def get_team_matches(self, team_code: str) -> Optional[int]:
        """Get the number of matches for a specific team in this round"""
        return self.team_matches.get(team_code)


# SQLModel for database
class IPLMatch(TimeStampedModel, table=True):
    """Model for IPL match fixtures"""

    __tablename__ = "ipl_matches_schedule"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    match_number: int = Field(nullable=False)
    round_number: int = Field(nullable=False)  # Original round from API
    date_utc: datetime = Field(
        nullable=False,
        sa_type=sqlalchemy.DateTime(timezone=True),
    )
    date_ist: datetime = Field(
        nullable=False,
        sa_type=sqlalchemy.DateTime(timezone=True),
    )
    location: str = Field(nullable=False)
    home_team: str = Field(nullable=False)
    away_team: str = Field(nullable=False)
    home_team_code: Optional[str] = Field(nullable=True)
    away_team_code: Optional[str] = Field(nullable=True)
    group: Optional[str] = Field(nullable=True)
    home_team_score: Optional[int] = Field(nullable=True)
    away_team_score: Optional[int] = Field(nullable=True)
    season: int = Field(default=2025, index=True)

    # Foreign key to IPLRound
    game_round_id: Optional[int] = Field(
        nullable=True, foreign_key="ipl_balanced_rounds.id"
    )

    # Simplified relationship
    round: Optional["IPLRound"] = Relationship(back_populates="matches")
