from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Dict, List, Any
from datetime import datetime

from src.db.session import get_session
from src.db.models import User, GullyParticipant
from src.api.dependencies import get_current_user
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


async def assign_admin_role(
    user_id: int, gully_id: int, session: Session
) -> Dict[str, Any]:
    """
    Assign admin role to a user in a specific gully.

    Args:
        user_id: The user's ID
        gully_id: The gully ID
        session: Database session

    Returns:
        Result of the operation
    """
    # Find the user's participation in this gully
    participant = session.exec(
        select(GullyParticipant).where(
            (GullyParticipant.user_id == user_id)
            & (GullyParticipant.gully_id == gully_id)
        )
    ).first()

    if not participant:
        return {
            "success": False,
            "error": f"User {user_id} is not a participant in gully {gully_id}",
        }

    # Update the role to admin
    participant.role = "admin"
    session.add(participant)
    session.commit()
    session.refresh(participant)

    return {
        "success": True,
        "message": f"User {user_id} is now an admin in gully {gully_id}",
    }


async def get_gully_admins(gully_id: int, session: Session) -> List[Dict[str, Any]]:
    """
    Get all admins for a specific gully.

    Args:
        gully_id: The ID of the gully
        session: Database session

    Returns:
        List of admin users
    """
    # Find all participants with admin role in this gully
    admin_participants = session.exec(
        select(GullyParticipant).where(
            (GullyParticipant.gully_id == gully_id)
            & (GullyParticipant.role.in_(["admin", "owner"]))
        )
    ).all()

    # Get the user details for each admin
    admins = []
    for participant in admin_participants:
        user = session.get(User, participant.user_id)
        if user:
            admins.append(
                {
                    "user_id": user.id,
                    "telegram_id": user.telegram_id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "role": participant.role,
                }
            )

    return admins


async def remove_admin_role(
    user_id: int, gully_id: int, session: Session
) -> Dict[str, Any]:
    """
    Remove admin role from a user in a specific gully.

    Args:
        user_id: The user's ID
        gully_id: The gully ID
        session: Database session

    Returns:
        Result of the operation
    """
    # Find the user's participation in this gully
    participant = session.exec(
        select(GullyParticipant).where(
            (GullyParticipant.user_id == user_id)
            & (GullyParticipant.gully_id == gully_id)
        )
    ).first()

    if not participant:
        return {
            "success": False,
            "error": f"User {user_id} is not a participant in gully {gully_id}",
        }

    # Check if the user is actually an admin
    if participant.role != "admin":
        return {
            "success": False,
            "error": f"User {user_id} is not an admin in gully {gully_id}",
        }

    # Update the role to member
    participant.role = "member"
    session.add(participant)
    session.commit()
    session.refresh(participant)

    return {
        "success": True,
        "message": f"Admin role removed from user {user_id} in gully {gully_id}",
    }


@router.post("/roles/{gully_id}/{user_id}")
async def assign_admin_role_endpoint(
    gully_id: int,
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Assign admin role to a user in a gully."""
    # Check if current user is an admin in this gully
    admins = await get_gully_admins(gully_id, session)

    # Get the current user's role
    current_user_admin = next(
        (admin for admin in admins if admin["user_id"] == current_user.id), None
    )

    if not current_user_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can assign admin roles",
        )

    # Check if the target user exists
    target_user = session.get(User, user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    # Check if the target user is already an admin
    is_already_admin = any(admin["user_id"] == user_id for admin in admins)
    if is_already_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {user_id} is already an admin in this gully",
        )

    # Log the admin assignment for audit purposes
    logger.info(
        f"Admin role assignment: User {current_user.id} ({current_user.username}) "
        f"assigned admin role to User {user_id} in Gully {gully_id}"
    )

    # Assign the admin role
    result = await assign_admin_role(user_id, gully_id, session)

    # Return the result with additional audit information
    if result["success"]:
        return {
            **result,
            "assigned_by": {
                "user_id": current_user.id,
                "username": current_user.username,
            },
            "timestamp": datetime.now().isoformat(),
        }
    return result


@router.get("/admins/{gully_id}")
async def get_gully_admins_endpoint(
    gully_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get all admins for a gully."""
    # Check if current user is in this gully
    participant = session.exec(
        select(GullyParticipant).where(
            (GullyParticipant.user_id == current_user.id)
            & (GullyParticipant.gully_id == gully_id)
        )
    ).first()

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this gully",
        )

    return await get_gully_admins(gully_id, session)


@router.delete("/roles/{gully_id}/{user_id}")
async def remove_admin_role_endpoint(
    gully_id: int,
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Remove admin role from a user in a gully."""
    # Check if current user is an admin in this gully
    admins = await get_gully_admins(gully_id, session)

    # Get the current user's role
    current_user_admin = next(
        (admin for admin in admins if admin["user_id"] == current_user.id), None
    )

    if not current_user_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can remove admin roles",
        )

    # Check if the target user exists
    target_user = session.get(User, user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    # Check if the target user is an admin
    target_admin = next(
        (admin for admin in admins if admin["user_id"] == user_id), None
    )
    if not target_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {user_id} is not an admin in this gully",
        )

    # Prevent removing the group owner's admin role
    if target_admin.get("role") == "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot remove admin role from the group owner",
        )

    # Log the admin removal for audit purposes
    logger.info(
        f"Admin role removal: User {current_user.id} ({current_user.username}) "
        f"removed admin role from User {user_id} in Gully {gully_id}"
    )

    # Remove the admin role
    result = await remove_admin_role(user_id, gully_id, session)

    # Return the result with additional audit information
    if result["success"]:
        return {
            **result,
            "removed_by": {
                "user_id": current_user.id,
                "username": current_user.username,
            },
            "timestamp": datetime.now().isoformat(),
        }
    return result
