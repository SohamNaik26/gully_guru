from typing import Optional
from decimal import Decimal
from sqlmodel import Field

from src.db.models.models import TimeStampedModel


class KagglePlayer(TimeStampedModel, table=True):
    """Model for cricket players from Kaggle datasets."""

    __tablename__ = "kaggle_players"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    team: Optional[str] = Field(default=None)
    player_type: Optional[str] = Field(default=None)
    base_price: Optional[Decimal] = Field(default=None)
    sold_price: Optional[Decimal] = Field(default=None)
    season: Optional[int] = Field(default=None, index=True)
    processed: Optional[bool] = Field(default=False)
