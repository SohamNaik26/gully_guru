"""
Schemas for admin-related data.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, field_validator, ConfigDict

from src.api.schemas.user import UserResponse


# Admin Permission Models
class AdminPermissionBase(BaseModel):
    """Base model for admin permission data."""

    user_id: int
    gully_id: int
    permission_type: str  # e.g., "manage_users", "manage_players", "manage_settings"


class AdminPermissionCreate(AdminPermissionBase):
    """Create model for admin permission."""

    pass


class AdminPermissionResponse(AdminPermissionBase):
    """Response model for admin permission data."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("permission_type")
    @classmethod
    def validate_permission_type(cls, v):
        """Validate that permission_type is one of the allowed values."""
        valid_permissions = [
            "manage_users",
            "manage_players",
            "manage_settings",
            "full_access",
        ]
        if v not in valid_permissions:
            raise ValueError(f"Permission type must be one of {valid_permissions}")
        return v


# Admin Role Models
class AdminRoleBase(BaseModel):
    """Base model for admin role data."""

    user_id: int
    gully_id: int
    role: str  # "admin" or "owner"


class AdminRoleCreate(AdminRoleBase):
    """Create model for admin role."""

    pass


class AdminRoleResponse(AdminRoleBase):
    """Response model for admin role data."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        """Validate that role is one of the allowed values."""
        valid_roles = ["admin", "owner"]
        if v not in valid_roles:
            raise ValueError(f"Role must be one of {valid_roles}")
        return v


# Admin User Response
class AdminUserResponse(UserResponse):
    """Response model for admin user data with permissions."""

    permissions: List[str] = []
    role: str

    model_config = ConfigDict(from_attributes=True)
