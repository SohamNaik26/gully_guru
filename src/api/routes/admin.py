from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Dict, Any

from src.db.session import get_session
from src.db.models import User
from src.api.dependencies import get_current_user
from src.services import admin as admin_service

router = APIRouter()


@router.post("/roles/{gully_id}/{user_id}")
async def assign_admin_role(
    gully_id: int,
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Assign admin role to a user in a gully."""
    return await admin_service.assign_admin_role(
        session, current_user.id, user_id, gully_id
    )


@router.delete("/roles/{gully_id}/{user_id}")
async def remove_admin_role(
    gully_id: int,
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Remove admin role from a user in a gully."""
    return await admin_service.remove_admin_role(
        session, current_user.id, user_id, gully_id
    )


@router.post("/permissions/{gully_id}/{user_id}/{permission_type}")
async def assign_admin_permission(
    gully_id: int,
    user_id: int,
    permission_type: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Assign a specific admin permission to a user."""
    return await admin_service.assign_admin_permission(
        session, current_user.id, user_id, gully_id, permission_type
    )


@router.delete("/permissions/{gully_id}/{user_id}/{permission_type}")
async def remove_admin_permission(
    gully_id: int,
    user_id: int,
    permission_type: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Remove a specific admin permission from a user."""
    return await admin_service.remove_admin_permission(
        session, current_user.id, user_id, gully_id, permission_type
    )


@router.get("/permissions/{gully_id}/{user_id}")
async def get_user_permissions(
    gully_id: int,
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get all admin permissions for a user in a gully."""
    # Check if current user has permission to view this
    has_permission = await admin_service.check_admin_permission(
        session, current_user.id, gully_id, "user_management"
    )

    if not has_permission and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this user's permissions",
        )

    return await admin_service.get_admin_permissions(session, user_id, gully_id)


@router.get("/admins/{gully_id}")
async def get_gully_admins(
    gully_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get all admins for a gully."""
    # Check if current user is in this gully
    has_permission = await admin_service.check_admin_permission(
        session, current_user.id, gully_id
    )

    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this gully's admins",
        )

    return await admin_service.get_gully_admins(session, gully_id)


@router.post("/nominate/{gully_id}/{user_id}")
async def nominate_admin(
    gully_id: int,
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Nominate a user to become an admin."""
    return await admin_service.nominate_admin(
        session, current_user.id, user_id, gully_id
    )


@router.post("/invite-link/{gully_id}")
async def generate_invite_link(
    gully_id: int,
    expiration_hours: int = 24,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Generate an invite link for a gully."""
    return await admin_service.generate_invite_link(
        session, current_user.id, gully_id, expiration_hours
    )
