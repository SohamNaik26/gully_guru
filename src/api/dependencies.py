from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import Optional

from src.db.session import get_session
from src.db.models import User
from src.utils.logger import logger

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)


# Dependency for getting the current user
async def get_current_user(
    session: AsyncSession = Depends(get_session),
    token: str = Depends(oauth2_scheme),
) -> User:
    """
    Get the current user from the token.
    For development, this always returns a test user without authentication.

    Args:
        session: Database session
        token: JWT token (not used in development)

    Returns:
        User: Current user (test user in development)
    """
    try:
        # For development, always return a test user without authentication
        try:
            result = await session.execute(select(User).limit(1))
            user = result.scalars().first()
            if not user:
                # Create a test user if none exists
                user = User(
                    telegram_id=12345,
                    username="test_user",
                    full_name="Test User",
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)
            return user
        except Exception as e:
            logger.error(f"Error getting test user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


# Optional current user dependency (for endpoints that work with or without auth)
async def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> Optional[User]:
    """
    Get the current user if authenticated, otherwise None.
    For development, this always returns a test user.

    Args:
        token: JWT token (not used in development)
        session: Database session

    Returns:
        Optional[User]: The test user
    """
    # In development, always return a user
    return await get_current_user(session, token)


# Admin user dependency
async def get_admin_user(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> User:
    """
    Get the current user and verify they have admin privileges in any gully.
    For development, this always succeeds.

    Args:
        current_user: The authenticated user
        session: Database session

    Returns:
        User: The authenticated admin user
    """
    # For development, always allow admin access
    return current_user


# Gully admin user dependency
async def get_gully_admin_user(
    gully_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> User:
    """
    Get the current user and verify they have admin privileges in the specified gully.
    For development, this always succeeds.

    Args:
        gully_id: The ID of the gully to check admin privileges for
        current_user: The authenticated user
        session: Database session

    Returns:
        User: The authenticated admin user
    """
    # For development, always allow admin access
    return current_user

    # Uncomment this for production
    # # Check if user is an admin in the specified gully
    # result = await session.execute(
    #     select(GullyParticipant).where(
    #         (GullyParticipant.user_id == current_user.id) &
    #         (GullyParticipant.gully_id == gully_id) &
    #         (GullyParticipant.role.in_(["admin", "owner"]))
    #     )
    # )
    # admin_participation = result.scalars().first()
    #
    # if not admin_participation:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail=f"Admin privileges required for gully {gully_id}",
    #     )
    # return current_user
