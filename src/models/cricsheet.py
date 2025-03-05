from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator

from src.models.base import validate_non_negative


class CricsheetPlayer(BaseModel):
    """
    Pydantic model for player data from Cricsheet.
    
    Attributes:
        key: Unique identifier for the player
        name: Player's full name
        known_as: Common name the player is known as
        dob: Date of birth (optional)
        gender: Player's gender (M/F)
        teams: List of teams the player has represented
        batting_style: Batting style (e.g., "Right-hand bat")
        bowling_style: Bowling style (e.g., "Right-arm fast-medium")
    """
    key: str = Field(..., description="Unique player identifier")
    name: str = Field(..., description="Player's full name")
    known_as: Optional[str] = Field(None, description="Common name")
    dob: Optional[datetime] = Field(None, description="Date of birth")
    gender: str = Field(..., description="Player's gender (M/F)")
    teams: List[str] = Field(default_factory=list, description="Teams represented")
    batting_style: Optional[str] = Field(None, description="Batting style")
    bowling_style: Optional[str] = Field(None, description="Bowling style")
    
    @validator("gender")
    def validate_gender(cls, v):
        if v not in ["M", "F"]:
            raise ValueError("Gender must be either 'M' or 'F'")
        return v
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "key": "kohli",
                "name": "Virat Kohli",
                "known_as": "Virat",
                "dob": "1988-11-05T00:00:00",
                "gender": "M",
                "teams": ["India", "RCB"],
                "batting_style": "Right-hand bat",
                "bowling_style": "Right-arm medium"
            }
        }
    
    def to_db_model(self) -> Dict[str, Any]:
        """Convert Cricsheet model to database model format."""
        return {
            "cricsheet_key": self.key,
            "name": self.name,
            "known_as": self.known_as,
            "dob": self.dob,
            "gender": self.gender,
            "teams": self.teams,
            "batting_style": self.batting_style,
            "bowling_style": self.bowling_style
        }


class CricsheetMatch(BaseModel):
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
    
    @validator("toss_decision")
    def validate_toss_decision(cls, v):
        valid_decisions = ["bat", "field"]
        if v not in valid_decisions:
            raise ValueError(f"Toss decision must be one of {valid_decisions}")
        return v
    
    @validator("match_type")
    def validate_match_type(cls, v):
        valid_types = ["Test", "ODI", "T20", "IT20"]
        if v not in valid_types:
            raise ValueError(f"Match type must be one of {valid_types}")
        return v
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "key": "ipl_2023_m01",
                "date": "2023-03-31T00:00:00",
                "venue": "M. Chinnaswamy Stadium",
                "city": "Bangalore",
                "competition": "IPL",
                "match_type": "T20",
                "team1": "RCB",
                "team2": "MI",
                "toss_winner": "MI",
                "toss_decision": "field",
                "winner": "RCB",
                "result": "runs",
                "result_margin": 8
            }
        }
    
    def to_db_model(self) -> Dict[str, Any]:
        """Convert Cricsheet match to database model format."""
        return {
            "cricsheet_key": self.key,
            "date": self.date,
            "venue": self.venue,
            "city": self.city,
            "competition": self.competition,
            "match_type": self.match_type,
            "team1": self.team1,
            "team2": self.team2,
            "toss_winner": self.toss_winner,
            "toss_decision": self.toss_decision,
            "winner": self.winner,
            "result": self.result,
            "result_margin": self.result_margin
        }


class CricsheetInnings(BaseModel):
    """
    Pydantic model for innings data from Cricsheet.
    
    Attributes:
        match_key: Reference to the match
        innings_number: Innings number (1, 2, 3, 4)
        team: Batting team
        overs: Number of overs
        runs: Total runs scored
        wickets: Total wickets fallen
        extras: Extra runs
    """
    match_key: str = Field(..., description="Match identifier")
    innings_number: int = Field(..., description="Innings number")
    team: str = Field(..., description="Batting team")
    overs: float = Field(..., description="Number of overs")
    runs: int = Field(..., description="Total runs")
    wickets: int = Field(..., description="Total wickets")
    extras: int = Field(..., description="Extra runs")
    
    @validator("innings_number")
    def validate_innings_number(cls, v):
        if v not in [1, 2, 3, 4]:
            raise ValueError("Innings number must be between 1 and 4")
        return v
    
    @validator("overs", "runs", "wickets", "extras")
    def validate_non_negative_values(cls, v):
        return validate_non_negative(v)
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "match_key": "ipl_2023_m01",
                "innings_number": 1,
                "team": "RCB",
                "overs": 20.0,
                "runs": 180,
                "wickets": 8,
                "extras": 12
            }
        }


class CricsheetPlayerPerformance(BaseModel):
    """
    Pydantic model for player performance in a match.
    
    Attributes:
        match_key: Reference to the match
        player_key: Reference to the player
        team: Player's team
        innings: Innings number
        batting_position: Batting position (if batted)
        runs_scored: Runs scored
        balls_faced: Balls faced
        fours: Number of fours
        sixes: Number of sixes
        overs_bowled: Overs bowled
        maidens: Maiden overs
        runs_conceded: Runs conceded while bowling
        wickets: Wickets taken
        catches: Catches taken
        stumpings: Stumpings made
        run_outs: Run outs effected
    """
    match_key: str = Field(..., description="Match identifier")
    player_key: str = Field(..., description="Player identifier")
    team: str = Field(..., description="Player's team")
    innings: int = Field(..., description="Innings number")
    batting_position: Optional[int] = Field(None, description="Batting position")
    runs_scored: int = Field(default=0, description="Runs scored")
    balls_faced: int = Field(default=0, description="Balls faced")
    fours: int = Field(default=0, description="Number of fours")
    sixes: int = Field(default=0, description="Number of sixes")
    overs_bowled: float = Field(default=0.0, description="Overs bowled")
    maidens: int = Field(default=0, description="Maiden overs")
    runs_conceded: int = Field(default=0, description="Runs conceded")
    wickets: int = Field(default=0, description="Wickets taken")
    catches: int = Field(default=0, description="Catches taken")
    stumpings: int = Field(default=0, description="Stumpings made")
    run_outs: int = Field(default=0, description="Run outs effected")
    
    @validator("innings")
    def validate_innings(cls, v):
        if v not in [1, 2, 3, 4]:
            raise ValueError("Innings must be between 1 and 4")
        return v
    
    @validator("batting_position")
    def validate_batting_position(cls, v):
        if v is not None and (v < 1 or v > 11):
            raise ValueError("Batting position must be between 1 and 11")
        return v
    
    @validator("runs_scored", "balls_faced", "fours", "sixes", "maidens", 
               "runs_conceded", "wickets", "catches", "stumpings", "run_outs")
    def validate_non_negative_integers(cls, v):
        return validate_non_negative(v)
    
    @validator("overs_bowled")
    def validate_overs_bowled(cls, v):
        if v < 0:
            raise ValueError("Overs bowled cannot be negative")
        return v
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "match_key": "ipl_2023_m01",
                "player_key": "kohli",
                "team": "RCB",
                "innings": 1,
                "batting_position": 3,
                "runs_scored": 82,
                "balls_faced": 49,
                "fours": 6,
                "sixes": 5,
                "overs_bowled": 0.0,
                "maidens": 0,
                "runs_conceded": 0,
                "wickets": 0,
                "catches": 1,
                "stumpings": 0,
                "run_outs": 0
            }
        } 