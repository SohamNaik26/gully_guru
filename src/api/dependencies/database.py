"""
Database dependencies for the GullyGuru API.
This module provides dependencies for database access.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import AsyncSessionLocal


async def get_db() -> AsyncSession:
    """
    Get a database session.

    Returns:
        Database session
    """
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()


# Add an alias for backward compatibility
get_session = get_db
