"""
Database dependencies for the GullyGuru API.
This module provides dependencies for database access.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_session


async def get_db() -> AsyncSession:
    """
    Get a database session.

    Returns:
        Database session
    """
    async with get_session() as session:
        yield session
