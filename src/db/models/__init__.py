"""
Model registry - imports all SQLModel models to ensure they're registered with SQLModel.metadata
"""

# Import main domain models from models.py
from src.db.models.models import (
    # Base models
    TimeStampedModel,
    # User models
    User,
    # Player models
    Player,
    ParticipantPlayer,
    # Gully models
    Gully,
    GullyParticipant,
    # Enum classes
    PlayerType,
    ParticipantRole,
    AuctionType,
    AuctionStatus,
    GullyStatus,
    UserPlayerStatus,
    # Auction & Transfer models
    AuctionQueue,
    TransferMarket,
    BankTransaction,
    Bid,
    DraftSelection,
)

# Import integration models
# API models - Commented out as they're not currently used in the database
# from src.db.models.api import ApiMatch, ApiPlayer, ApiPlayerStats, ApiTeam
from src.db.models.cricsheet import (
    CricsheetMatch,
    CricsheetPlayer,
    CricsheetPlayerMatch,
    CricsheetDelivery,
)
from src.db.models.kaggle import KagglePlayer

# Import IPL models
from src.db.models.ipl_fixures import IPLMatch, TeamEnum, MatchInput, IPLRound

# Create a list of all models for easy access
all_models = [
    # Base models
    TimeStampedModel,
    # Domain models
    User,
    Player,
    ParticipantPlayer,
    Gully,
    GullyParticipant,
    # Enum classes
    PlayerType,
    ParticipantRole,
    AuctionType,
    AuctionStatus,
    GullyStatus,
    UserPlayerStatus,
    # Auction & Transfer models
    AuctionQueue,
    TransferMarket,
    BankTransaction,
    Bid,
    DraftSelection,
    # Cricsheet models
    CricsheetMatch,
    CricsheetPlayer,
    CricsheetPlayerMatch,
    CricsheetDelivery,
    # Kaggle models
    KagglePlayer,
    # IPL Fixtures models
    IPLMatch,
    TeamEnum,
    MatchInput,
    IPLRound,
]


# Function to get all models (alternative to direct import)
def get_all_models():
    return all_models


# Export all models for easier imports elsewhere
__all__ = [
    # Models from models.py
    "Player",
    "User",
    "GullyParticipant",
    "Gully",
    "DraftSelection",
    "ParticipantPlayer",
    "AuctionQueue",
    "TransferMarket",
    "BankTransaction",
    "Bid",
    # Enums from models.py
    "PlayerType",
    "ParticipantRole",
    "AuctionType",
    "AuctionStatus",
    "GullyStatus",
    "UserPlayerStatus",
    # Base models
    "TimeStampedModel",
    # Kaggle models
    "KagglePlayer",
    # IPL Fixtures models
    "IPLMatch",
    "IPLRound",
    # Cricsheet models
    "CricsheetMatch",
    "CricsheetDelivery",
    "CricsheetPlayer",
    "CricsheetPlayerMatch",
]
