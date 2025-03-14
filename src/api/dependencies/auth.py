"""
Authentication dependencies for the GullyGuru API.
This module provides simplified dependencies for authentication during development.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.database import get_db
from src.db.models.models import User


async def get_current_user(db: AsyncSession = Depends(get_db)) -> User:
    """
    Get a mock current user for development.
    In a production environment, this would validate JWT tokens.

    Args:
        db: Database session

    Returns:
        Mock user object
    """
    # Create a mock user object
    mock_user = User(
        id=1, telegram_id=123456789, username="dev_user", full_name="Development User"
    )

    return mock_user
