"""
API schema models for GullyGuru
"""

# User schemas
from src.api.schemas.user import (
    UserBase,
    UserCreate,
    UserResponse,
    UserWithPlayers,
    UserPlayerBase,
    UserPlayerCreate,
    UserPlayerResponse,
)

# Player schemas
from src.api.schemas.player import (
    PlayerBase,
    PlayerCreate,
    PlayerRead,
    PlayerResponse,
    PlayerStatsResponse,
)

# Match schemas
from src.api.schemas.match import (
    MatchBase,
    MatchCreate,
    MatchResponse,
    MatchPerformanceResponse,
)

# Gully and Game mechanics schemas
from src.api.schemas.gully import (
    # Gully schemas
    GullyBase,
    GullyCreate,
    GullyResponse,
    GullyParticipantBase,
    GullyParticipantCreate,
    GullyParticipantResponse,
    ParticipantUpdate,
    # Game mechanics schemas
    UserSquadResponse,
    AuctionBidCreate,
    AuctionBidResponse,
    LeaderboardEntry,
    LeaderboardResponse,
    UserPlayerWithDetails,
)

# Admin schemas
from src.api.schemas.admin import (
    AdminPermissionBase,
    AdminPermissionCreate,
    AdminPermissionResponse,
    AdminRoleBase,
    AdminRoleCreate,
    AdminRoleResponse,
    AdminUserResponse,
)

# Re-export all models
__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserResponse",
    "UserWithPlayers",
    "UserPlayerBase",
    "UserPlayerCreate",
    "UserPlayerResponse",
    # Player schemas
    "PlayerBase",
    "PlayerCreate",
    "PlayerRead",
    "PlayerResponse",
    "PlayerStatsResponse",
    # Match schemas
    "MatchBase",
    "MatchCreate",
    "MatchResponse",
    "MatchPerformanceResponse",
    # Gully schemas
    "GullyBase",
    "GullyCreate",
    "GullyResponse",
    "GullyParticipantBase",
    "GullyParticipantCreate",
    "GullyParticipantResponse",
    "ParticipantUpdate",
    # Game mechanics schemas
    "UserSquadResponse",
    "AuctionBidCreate",
    "AuctionBidResponse",
    "LeaderboardEntry",
    "LeaderboardResponse",
    "UserPlayerWithDetails",
    # Admin schemas
    "AdminPermissionBase",
    "AdminPermissionCreate",
    "AdminPermissionResponse",
    "AdminRoleBase",
    "AdminRoleCreate",
    "AdminRoleResponse",
    "AdminUserResponse",
]
