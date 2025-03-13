"""
Services package for the GullyGuru API.
This package contains service modules that implement the business logic for the API.
"""

from src.api.services.base import BaseService, BaseServiceClient
from src.api.services.fantasy import FantasyService, FantasyServiceClient
from src.api.services.admin import AdminService, AdminServiceClient
from src.api.services.gully import GullyService, GullyServiceClient
from src.api.services.player import PlayerService, PlayerServiceClient
from src.api.services.user import UserService, UserServiceClient

__all__ = [
    "BaseService",
    "BaseServiceClient",
    "FantasyService",
    "FantasyServiceClient",
    "AdminService",
    "AdminServiceClient",
    "GullyService",
    "GullyServiceClient",
    "PlayerService",
    "PlayerServiceClient",
    "UserService",
    "UserServiceClient",
]
