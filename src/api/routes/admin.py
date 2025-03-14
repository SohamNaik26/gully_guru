"""
Admin API routes for GullyGuru
"""

import logging
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_session
from src.api.schemas.admin import (
    AdminRoleResponse,
    AdminUserResponse,
)
from src.api.services import AdminService
from src.api.factories import AdminFactory
from src.api.exceptions import NotFoundException

router = APIRouter(prefix="/admin", tags=["Admin"])
logger = logging.getLogger(__name__)


@router.get("/gully/{gully_id}/admins", response_model=List[AdminUserResponse])
async def get_gully_admins(
    gully_id: int,
    db: AsyncSession = Depends(get_session),
):
    """
    Get all admins for a gully.

    Args:
        gully_id: Gully ID

    Returns:
        List[AdminUserResponse]: List of admin users for the gully

    Raises:
        HTTPException: If an error occurs
    """
    try:
        admin_service = AdminService(db)
        admins = await admin_service.get_gully_admins(gully_id)
        return AdminFactory.create_response_list(admins)
    except Exception as e:
        logger.error(f"Error getting gully admins: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting gully admins",
        )


@router.post(
    "/gully/{gully_id}/admins/{user_id}",
    response_model=AdminRoleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def assign_admin_role(
    gully_id: int,
    user_id: int,
    admin_user_id: int = Query(
        ..., description="ID of the user assigning the admin role"
    ),
    db: AsyncSession = Depends(get_session),
):
    """
    Assign admin role to a user.

    Args:
        gully_id: Gully ID
        user_id: User ID to assign admin role to
        admin_user_id: ID of the user assigning the admin role

    Returns:
        AdminRoleResponse: Created admin role

    Raises:
        HTTPException: If an error occurs or user doesn't have permission
    """
    try:
        admin_service = AdminService(db)

        # Check if admin_user_id has permission to assign admin roles
        is_admin = await admin_service.is_gully_admin(admin_user_id, gully_id)
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only gully admins can assign admin roles",
            )

        # Assign admin role
        admin_role = await admin_service.assign_admin_role(user_id, gully_id)
        return AdminFactory.create_role_response(admin_role)
    except Exception as e:
        logger.error(f"Error assigning admin role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error assigning admin role",
        )


@router.delete(
    "/gully/{gully_id}/admins/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_admin_role(
    gully_id: int,
    user_id: int,
    admin_user_id: int = Query(
        ..., description="ID of the user removing the admin role"
    ),
    db: AsyncSession = Depends(get_session),
):
    """
    Remove admin role from a user.

    Args:
        gully_id: Gully ID
        user_id: User ID to remove admin role from
        admin_user_id: ID of the user removing the admin role

    Returns:
        None

    Raises:
        HTTPException: If an error occurs or user doesn't have permission
    """
    try:
        admin_service = AdminService(db)

        # Check if admin_user_id has permission to remove admin roles
        is_admin = await admin_service.is_gully_admin(admin_user_id, gully_id)
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only gully admins can remove admin roles",
            )

        # Remove admin role
        success = await admin_service.remove_admin_role(user_id, gully_id)
        if not success:
            raise NotFoundException(
                resource_type="Admin role",
                resource_id=f"user {user_id} in gully {gully_id}",
            )
        return None
    except Exception as e:
        logger.error(f"Error removing admin role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error removing admin role",
        )


@router.get(
    "/user/{user_id}/permissions",
    response_model=Dict[str, Any],
)
async def get_user_permissions(
    user_id: int,
    gully_id: int = Query(..., description="ID of the gully to check permissions for"),
    db: AsyncSession = Depends(get_session),
):
    """
    Get a user's permissions in a gully.

    Args:
        user_id: User ID
        gully_id: Gully ID

    Returns:
        Dict[str, Any]: User's permissions

    Raises:
        HTTPException: If an error occurs
    """
    try:
        admin_service = AdminService(db)
        permissions = await admin_service.get_user_permissions(user_id, gully_id)
        return permissions
    except Exception as e:
        logger.error(f"Error getting user permissions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting user permissions",
        )
