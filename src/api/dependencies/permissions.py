"""
Permission dependencies for the GullyGuru API.
This module provides dependencies for checking user permissions.
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from src.api.dependencies.database import get_db
from src.api.services.participant import ParticipantService
from src.api.exceptions import AuthorizationException


async def check_is_admin(
    user_id: int, gully_id: int, db: AsyncSession = Depends(get_db)
) -> bool:
    """
    Check if a user is an admin for a gully.

    Args:
        user_id: User ID to check
        gully_id: Gully ID to check against
        db: Database session

    Returns:
        True if user is an admin, False otherwise

    Raises:
        AuthorizationException: If user is not an admin
    """
    participant_service = ParticipantService(db)
    is_admin = await participant_service.is_admin(user_id, gully_id)

    if not is_admin:
        raise AuthorizationException("Only gully admins can perform this action")

    return True


async def check_is_system_admin(
    user_id: int, db: AsyncSession = Depends(get_db)
) -> bool:
    """
    Check if a user is a system admin.

    Args:
        user_id: User ID to check
        db: Database session

    Returns:
        True if user is a system admin, False otherwise

    Raises:
        AuthorizationException: If user is not a system admin
    """
    # For now, we'll consider user with ID 1 as system admin
    # In a real system, this would check against a proper admin table
    if user_id != 1:
        raise AuthorizationException("Only system admins can perform this action")

    return True


async def check_is_participant(
    user_id: int, gully_id: int, db: AsyncSession = Depends(get_db)
) -> bool:
    """
    Check if a user is a participant in a gully.

    Args:
        user_id: User ID to check
        gully_id: Gully ID to check against
        db: Database session

    Returns:
        True if user is a participant, False otherwise

    Raises:
        AuthorizationException: If user is not a participant
    """
    participant_service = ParticipantService(db)
    participant = await participant_service.get_participant(gully_id, user_id)

    if not participant:
        raise AuthorizationException("User is not a participant in this gully")

    return True
