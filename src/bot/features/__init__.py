"""
Features package for the GullyGuru bot.
"""

from src.bot.features.onboarding import get_handlers as get_onboarding_handlers
from src.bot.features.squad import get_handlers as get_squad_handlers
from src.bot.features.auction import get_handlers as get_auction_handlers
from src.bot.features.player_release import get_handlers as get_player_release_handlers

__all__ = [
    "get_onboarding_handlers",
    "get_squad_handlers",
    "get_auction_handlers",
    "get_player_release_handlers",
]
