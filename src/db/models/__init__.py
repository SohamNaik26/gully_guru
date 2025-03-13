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
    UserPlayer,
    # Gully models
    Gully,
    GullyParticipant,
    # Enum classes
    PlayerType,
    ParticipantRole,
    AuctionType,
    AuctionStatus,
    # Auction & Transfer models
    AuctionQueue,
    TransferMarket,
    BankTransaction,
    Bid,
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

# Create a list of all models for easy access
all_models = [
    # Base models
    TimeStampedModel,
    # Domain models
    User,
    Player,
    UserPlayer,
    Gully,
    GullyParticipant,
    # Enum classes
    PlayerType,
    ParticipantRole,
    AuctionType,
    AuctionStatus,
    # Auction & Transfer models
    AuctionQueue,
    TransferMarket,
    BankTransaction,
    Bid,
    # Cricsheet models
    CricsheetMatch,
    CricsheetPlayer,
    CricsheetPlayerMatch,
    CricsheetDelivery,
    # Kaggle models
    KagglePlayer,
]


# Function to get all models (alternative to direct import)
def get_all_models():
    return all_models
