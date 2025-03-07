from typing import List, Optional, Dict, Any
from sqlmodel import Session, select
from fastapi import HTTPException, status

from src.db.models import User, Gully, GullyParticipant, AdminPermission


async def check_admin_permission(
    session: Session, user_id: int, gully_id: int, permission_type: Optional[str] = None
) -> bool:
    """
    Check if a user has admin permissions in a specific gully.

    Args:
        session: Database session
        user_id: ID of the user to check
        gully_id: ID of the gully to check permissions for
        permission_type: Specific permission to check (if None, checks for any admin role)

    Returns:
        bool: True if user has the required permission, False otherwise
    """
    # First check if user is a global admin
    user = session.get(User, user_id)
    if user and user.is_admin:
        return True

    # Check if user is an admin or owner in this gully
    participant = session.exec(
        select(GullyParticipant)
        .where(GullyParticipant.user_id == user_id)
        .where(GullyParticipant.gully_id == gully_id)
    ).first()

    if not participant:
        return False

    # If user is an owner, they have all permissions
    if participant.role == "owner":
        return True

    # If user is an admin, check specific permission if requested
    if participant.role == "admin":
        if permission_type is None:
            return True

        # Check for "all" permission
        all_permission = session.exec(
            select(AdminPermission)
            .where(AdminPermission.user_id == user_id)
            .where(AdminPermission.gully_id == gully_id)
            .where(AdminPermission.permission_type == "all")
            .where(AdminPermission.is_active)
        ).first()

        if all_permission:
            return True

        # Check for specific permission
        specific_permission = session.exec(
            select(AdminPermission)
            .where(AdminPermission.user_id == user_id)
            .where(AdminPermission.gully_id == gully_id)
            .where(AdminPermission.permission_type == permission_type)
            .where(AdminPermission.is_active)
        ).first()

        return specific_permission is not None

    return False


async def assign_admin_role(
    session: Session, assigner_id: int, user_id: int, gully_id: int, role: str = "admin"
) -> Dict[str, Any]:
    """
    Assign an admin role to a user in a specific gully.

    Args:
        session: Database session
        assigner_id: ID of the user assigning the role (must be owner or admin)
        user_id: ID of the user to assign the role to
        gully_id: ID of the gully
        role: Role to assign (admin or owner)

    Returns:
        Dict: Information about the assigned role

    Raises:
        HTTPException: If the assigner doesn't have permission or the user isn't in the gully
    """
    # Check if assigner has permission
    has_permission = await check_admin_permission(
        session, assigner_id, gully_id, "user_management"
    )

    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to assign admin roles",
        )

    # Check if user is in the gully
    participant = session.exec(
        select(GullyParticipant)
        .where(GullyParticipant.user_id == user_id)
        .where(GullyParticipant.gully_id == gully_id)
    ).first()

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not a participant in this gully",
        )

    # Update the role
    participant.role = role
    session.add(participant)
    session.commit()
    session.refresh(participant)

    return {"user_id": user_id, "gully_id": gully_id, "role": role, "success": True}


async def remove_admin_role(
    session: Session, remover_id: int, user_id: int, gully_id: int
) -> Dict[str, Any]:
    """
    Remove admin role from a user in a specific gully.

    Args:
        session: Database session
        remover_id: ID of the user removing the role (must be owner or admin)
        user_id: ID of the user to remove the role from
        gully_id: ID of the gully

    Returns:
        Dict: Information about the role removal

    Raises:
        HTTPException: If the remover doesn't have permission or other issues
    """
    # Check if remover has permission
    has_permission = await check_admin_permission(
        session, remover_id, gully_id, "user_management"
    )

    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to remove admin roles",
        )

    # Check if user is in the gully
    participant = session.exec(
        select(GullyParticipant)
        .where(GullyParticipant.user_id == user_id)
        .where(GullyParticipant.gully_id == gully_id)
    ).first()

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not a participant in this gully",
        )

    # Cannot remove role from owner
    if participant.role == "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot remove role from the gully owner",
        )

    # Update the role to member
    participant.role = "member"
    session.add(participant)

    # Remove all admin permissions
    permissions = session.exec(
        select(AdminPermission)
        .where(AdminPermission.user_id == user_id)
        .where(AdminPermission.gully_id == gully_id)
    ).all()

    for permission in permissions:
        session.delete(permission)

    session.commit()

    return {"user_id": user_id, "gully_id": gully_id, "success": True}


async def assign_admin_permission(
    session: Session,
    assigner_id: int,
    user_id: int,
    gully_id: int,
    permission_type: str,
) -> Dict[str, Any]:
    """
    Assign a specific admin permission to a user.

    Args:
        session: Database session
        assigner_id: ID of the user assigning the permission
        user_id: ID of the user to assign the permission to
        gully_id: ID of the gully
        permission_type: Type of permission to assign

    Returns:
        Dict: Information about the assigned permission

    Raises:
        HTTPException: If the assigner doesn't have permission or other issues
    """
    # Check if assigner has permission
    has_permission = await check_admin_permission(
        session, assigner_id, gully_id, "user_management"
    )

    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to assign admin permissions",
        )

    # Check if user is an admin in the gully
    participant = session.exec(
        select(GullyParticipant)
        .where(GullyParticipant.user_id == user_id)
        .where(GullyParticipant.gully_id == gully_id)
    ).first()

    if not participant or participant.role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be an admin or owner to assign permissions",
        )

    # Check if permission already exists
    existing_permission = session.exec(
        select(AdminPermission)
        .where(AdminPermission.user_id == user_id)
        .where(AdminPermission.gully_id == gully_id)
        .where(AdminPermission.permission_type == permission_type)
    ).first()

    if existing_permission:
        # Update existing permission
        existing_permission.is_active = True
        session.add(existing_permission)
        session.commit()
        session.refresh(existing_permission)
        permission = existing_permission
    else:
        # Create new permission
        permission = AdminPermission(
            user_id=user_id,
            gully_id=gully_id,
            permission_type=permission_type,
            is_active=True,
        )
        session.add(permission)
        session.commit()
        session.refresh(permission)

    return {
        "id": permission.id,
        "user_id": user_id,
        "gully_id": gully_id,
        "permission_type": permission_type,
        "is_active": permission.is_active,
        "success": True,
    }


async def remove_admin_permission(
    session: Session, remover_id: int, user_id: int, gully_id: int, permission_type: str
) -> Dict[str, Any]:
    """
    Remove a specific admin permission from a user.

    Args:
        session: Database session
        remover_id: ID of the user removing the permission
        user_id: ID of the user to remove the permission from
        gully_id: ID of the gully
        permission_type: Type of permission to remove

    Returns:
        Dict: Information about the removed permission

    Raises:
        HTTPException: If the remover doesn't have permission or other issues
    """
    # Check if remover has permission
    has_permission = await check_admin_permission(
        session, remover_id, gully_id, "user_management"
    )

    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to remove admin permissions",
        )

    # Find the permission
    permission = session.exec(
        select(AdminPermission)
        .where(AdminPermission.user_id == user_id)
        .where(AdminPermission.gully_id == gully_id)
        .where(AdminPermission.permission_type == permission_type)
    ).first()

    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission '{permission_type}' not found for this user",
        )

    # Deactivate the permission
    permission.is_active = False
    session.add(permission)
    session.commit()

    return {
        "user_id": user_id,
        "gully_id": gully_id,
        "permission_type": permission_type,
        "success": True,
    }


async def get_admin_permissions(
    session: Session, user_id: int, gully_id: int
) -> List[Dict[str, Any]]:
    """
    Get all admin permissions for a user in a gully.

    Args:
        session: Database session
        user_id: ID of the user
        gully_id: ID of the gully

    Returns:
        List[Dict]: List of permissions
    """
    permissions = session.exec(
        select(AdminPermission)
        .where(AdminPermission.user_id == user_id)
        .where(AdminPermission.gully_id == gully_id)
        .where(AdminPermission.is_active)
    ).all()

    return [
        {
            "id": p.id,
            "user_id": p.user_id,
            "gully_id": p.gully_id,
            "permission_type": p.permission_type,
            "is_active": p.is_active,
        }
        for p in permissions
    ]


async def get_gully_admins(session: Session, gully_id: int) -> List[Dict[str, Any]]:
    """
    Get all admins for a gully.

    Args:
        session: Database session
        gully_id: ID of the gully

    Returns:
        List[Dict]: List of admins with their permissions
    """
    admins = session.exec(
        select(GullyParticipant)
        .where(GullyParticipant.gully_id == gully_id)
        .where(GullyParticipant.role.in_(["admin", "owner"]))
    ).all()

    result = []
    for admin in admins:
        permissions = await get_admin_permissions(session, admin.user_id, gully_id)
        user = session.get(User, admin.user_id)

        result.append(
            {
                "user_id": admin.user_id,
                "username": user.username if user else None,
                "full_name": user.full_name if user else None,
                "role": admin.role,
                "permissions": permissions,
            }
        )

    return result


async def nominate_admin(
    session: Session, nominator_id: int, nominee_id: int, gully_id: int
) -> Dict[str, Any]:
    """
    Nominate a user to become an admin.
    This creates a pending nomination that the nominee must accept.

    Args:
        session: Database session
        nominator_id: ID of the user making the nomination
        nominee_id: ID of the user being nominated
        gully_id: ID of the gully

    Returns:
        Dict: Information about the nomination

    Raises:
        HTTPException: If the nominator doesn't have permission or other issues
    """
    # Check if nominator has permission
    has_permission = await check_admin_permission(
        session, nominator_id, gully_id, "user_management"
    )

    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to nominate admins",
        )

    # Check if nominee is in the gully
    nominee_participant = session.exec(
        select(GullyParticipant)
        .where(GullyParticipant.user_id == nominee_id)
        .where(GullyParticipant.gully_id == gully_id)
    ).first()

    if not nominee_participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nominee is not a participant in this gully",
        )

    # Check if nominee is already an admin
    if nominee_participant.role in ["admin", "owner"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already an admin or owner",
        )

    # For now, we'll directly assign the admin role
    # In a real implementation, you might want to create a nomination record
    # and require the nominee to accept it
    nominee_participant.role = "admin"
    session.add(nominee_participant)
    session.commit()

    # Grant basic permissions
    basic_permissions = ["user_management", "team_management"]
    for permission_type in basic_permissions:
        permission = AdminPermission(
            user_id=nominee_id,
            gully_id=gully_id,
            permission_type=permission_type,
            is_active=True,
        )
        session.add(permission)

    session.commit()

    return {
        "nominator_id": nominator_id,
        "nominee_id": nominee_id,
        "gully_id": gully_id,
        "success": True,
        "message": "User has been granted admin role",
    }


async def generate_invite_link(
    session: Session, user_id: int, gully_id: int, expiration_hours: int = 24
) -> Dict[str, Any]:
    """
    Generate an invite link for a gully.

    Args:
        session: Database session
        user_id: ID of the user generating the link
        gully_id: ID of the gully
        expiration_hours: Number of hours until the link expires

    Returns:
        Dict: Information about the invite link

    Raises:
        HTTPException: If the user doesn't have permission
    """
    # Check if user has permission
    has_permission = await check_admin_permission(
        session, user_id, gully_id, "user_management"
    )

    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to generate invite links",
        )

    # Get the gully
    gully = session.get(Gully, gully_id)
    if not gully:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Gully not found"
        )

    # In a real implementation, you would generate a unique token
    # and store it in the database with an expiration time
    # For now, we'll just return a dummy link

    return {
        "gully_id": gully_id,
        "gully_name": gully.name,
        "invite_link": f"https://t.me/GullyGuruBot?start=join_{gully_id}",
        "expires_in": f"{expiration_hours} hours",
        "created_by": user_id,
    }
