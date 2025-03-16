"""
API schema models for GullyGuru
"""

# User schemas
from src.api.schemas.user import (
    UserBase,
    UserCreate,
    UserResponse,
    UserResponseWithGullies,
    UserWithPlayers,
    ParticipantPlayerBase,
    ParticipantPlayerCreate,
    ParticipantPlayerResponse,
    UserUpdate,
)

# Player schemas
from src.api.schemas.player import (
    PlayerBase,
    PlayerCreate,
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

# Gully schemas
from src.api.schemas.gully import (
    GullyBase,
    GullyCreate,
    GullyResponse,
    GullyUpdate,
    SuccessResponse,
)

# Participant schemas
from src.api.schemas.participant import (
    ParticipantBase,
    ParticipantCreate,
    ParticipantResponse,
    ParticipantUpdate,
)

# Game mechanics schemas
from src.api.schemas.fantasy import (
    DraftPlayerBase,
    DraftPlayerCreate,
    DraftPlayerResponse,
    DraftSelectionBase,
    DraftSelectionCreate,
    DraftSelectionResponse,
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
    "UserResponseWithGullies",
    "UserWithPlayers",
    "ParticipantPlayerBase",
    "ParticipantPlayerCreate",
    "ParticipantPlayerResponse",
    "UserUpdate",
    # Player schemas
    "PlayerBase",
    "PlayerCreate",
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
    "GullyUpdate",
    "SuccessResponse",
    # Participant schemas
    "ParticipantBase",
    "ParticipantCreate",
    "ParticipantResponse",
    "ParticipantUpdate",
    # Game mechanics schemas
    "DraftPlayerBase",
    "DraftPlayerCreate",
    "DraftPlayerResponse",
    "DraftSelectionBase",
    "DraftSelectionCreate",
    "DraftSelectionResponse",
    "SquadResponse",
    # Admin schemas
    "AdminPermissionBase",
    "AdminPermissionCreate",
    "AdminPermissionResponse",
    "AdminRoleBase",
    "AdminRoleCreate",
    "AdminRoleResponse",
    "AdminUserResponse",
]
