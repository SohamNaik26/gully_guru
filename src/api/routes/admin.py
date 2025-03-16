"""
Admin API routes for GullyGuru
"""

import logging
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.database import get_db
from src.api.dependencies.permissions import check_is_admin
from src.api.schemas.admin import (
    AdminRoleResponse,
    AdminUserResponse,
)
from src.api.services.admin import AdminService
from src.api.factories.admin import AdminFactory
from src.api.exceptions import NotFoundException, handle_exceptions

router = APIRouter(prefix="/admin", tags=["Admin"])
logger = logging.getLogger(__name__)


@router.get("/gully/{gully_id}/admins", response_model=List[AdminUserResponse])
@handle_exceptions
async def get_gully_admins(
    gully_id: int = Path(..., description="ID of the gully"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all admins for a gully.

    Args:
        gully_id: Gully ID
        db: Database session

    Returns:
        List[AdminUserResponse]: List of admin users for the gully
    """
    admin_service = AdminService(db)
    admins = await admin_service.get_gully_admins(gully_id)
    return AdminFactory.create_response_list(admins)


@router.post(
    "/gully/{gully_id}/admins/{user_id}",
    response_model=AdminRoleResponse,
    status_code=status.HTTP_201_CREATED,
)
@handle_exceptions
async def assign_admin_role(
    gully_id: int = Path(..., description="ID of the gully"),
    user_id: int = Path(..., description="ID of the user to assign admin role to"),
    admin_user_id: int = Query(
        ..., description="ID of the user assigning the admin role"
    ),
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(lambda: check_is_admin(admin_user_id, gully_id, db)),
):
    """
    Assign admin role to a user.

    Args:
        gully_id: Gully ID
        user_id: User ID to assign admin role to
        admin_user_id: ID of the user assigning the admin role
        db: Database session
        _: Permission check dependency (hidden)

    Returns:
        AdminRoleResponse: Created admin role

    Raises:
        AuthorizationException: If user doesn't have permission
    """
    admin_service = AdminService(db)
    admin_role = await admin_service.assign_admin_role(user_id, gully_id)
    return AdminFactory.create_role_response(admin_role)


@router.delete(
    "/gully/{gully_id}/admins/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@handle_exceptions
async def remove_admin_role(
    gully_id: int = Path(..., description="ID of the gully"),
    user_id: int = Path(..., description="ID of the user to remove admin role from"),
    admin_user_id: int = Query(
        ..., description="ID of the user removing the admin role"
    ),
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(lambda: check_is_admin(admin_user_id, gully_id, db)),
):
    """
    Remove admin role from a user.

    Args:
        gully_id: Gully ID
        user_id: User ID to remove admin role from
        admin_user_id: ID of the user removing the admin role
        db: Database session
        _: Permission check dependency (hidden)

    Returns:
        None

    Raises:
        NotFoundException: If admin role not found
        AuthorizationException: If user doesn't have permission
    """
    admin_service = AdminService(db)
    success = await admin_service.remove_admin_role(user_id, gully_id)
    if not success:
        raise NotFoundException(
            resource_type="Admin role",
            resource_id=f"user {user_id} in gully {gully_id}",
        )
    return None


@router.get(
    "/user/{user_id}/permissions",
    response_model=Dict[str, Any],
)
@handle_exceptions
async def get_user_permissions(
    user_id: int = Path(..., description="ID of the user"),
    gully_id: int = Query(..., description="ID of the gully to check permissions for"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a user's permissions in a gully.

    Args:
        user_id: User ID
        gully_id: Gully ID
        db: Database session

    Returns:
        Dict[str, Any]: User's permissions
    """
    admin_service = AdminService(db)
    permissions = await admin_service.get_user_permissions(user_id, gully_id)
    return permissions
