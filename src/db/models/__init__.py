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
    # Transfer models removed
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
    # Transfer models removed
    # API models - Removed from database tables but kept in code for future use
    # ApiMatch,
    # ApiPlayer,
    # ApiPlayerStats,
    # ApiTeam,
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
