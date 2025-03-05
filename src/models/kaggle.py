from decimal import Decimal
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field, validator

from src.models.base import validate_non_negative


class KagglePlayer(BaseModel):
    """
    Pydantic model for IPL player auction data from Kaggle.

    Attributes:
        player: Player's name
        team: IPL team name (e.g., RCB, MI)
        type: Player type (BAT, BOWL, ALL)
        base: Base price in crores (optional)
        sold: Final sold price in crores
    """

    player: str = Field(..., description="Player's name")
    team: str = Field(..., description="Team name")
    type: str = Field(..., description="Player type (BAT/BOWL/ALL)")
    base: Optional[Decimal] = Field(None, description="Base price in crores")
    sold: Decimal = Field(..., description="Sold price in crores")

    @validator("sold")
    def validate_sold_price(cls, v):
        return validate_non_negative(v)

    @validator("type")
    def validate_player_type(cls, v):
        valid_types = ["BAT", "BOWL", "ALL", "WK"]
        if v not in valid_types:
            raise ValueError(f"Player type must be one of {valid_types}")
        return v

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "player": "Virat Kohli",
                "team": "RCB",
                "type": "BAT",
                "base": None,
                "sold": Decimal("21.00"),
            }
        }
    
    def to_db_model(self) -> Dict[str, Any]:
        """Convert Kaggle model to database model format."""
        return {
            "name": self.player,
            "team": self.team,
            "player_type": self.type,
            "base_price": self.base,
            "sold_price": self.sold
        }
