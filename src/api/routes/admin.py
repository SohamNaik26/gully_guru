"""
Admin API routes for GullyGuru
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_session
from src.api.schemas.admin import (
    AdminRoleResponse,
    AdminUserResponse,
)
from src.api.services.admin.client import AdminServiceClient
from src.api.factories import AdminFactory

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/gully/{gully_id}/admins", response_model=List[AdminUserResponse])
async def get_gully_admins(
    gully_id: int,
    db: AsyncSession = Depends(get_session),
):
    """Get all admins for a gully."""
    try:
        admin_service = AdminServiceClient(db)
        admins = await admin_service.get_gully_admins(gully_id)
        return admins
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
    gully_id: int, user_id: int, db: AsyncSession = Depends(get_session)
):
    """Assign admin role to a user."""
    try:
        admin_service = AdminServiceClient(db)

        # Assign admin role
        admin_role = await admin_service.assign_admin_role(user_id, gully_id)
        return admin_role
    except Exception as e:
        logger.error(f"Error assigning admin role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error assigning admin role",
        )
