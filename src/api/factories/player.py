"""Factory classes for creating Player-related response objects."""

from src.api.factories.base import ResponseFactory
from src.api.schemas import PlayerResponse
from src.db.models import Player


class PlayerFactory(ResponseFactory[Player, PlayerResponse]):
    """Factory for creating Player response objects."""

    response_model = PlayerResponse
