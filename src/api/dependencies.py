from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from typing import Optional

from src.db.session import get_session
from src.db.models import User
from src.services.auth import verify_token

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)


# Dependency for getting the current user
async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    """
    Get the current authenticated user.
    For development, this will return a default user if no token is provided.

    Args:
        token: JWT token (optional for development)
        session: Database session

    Returns:
        User: The authenticated user

    Raises:
        HTTPException: If authentication fails
    """
    # For development: if no token, try to get the first user
    if not token:
        # Try to get the first user in the database
        user = session.exec(select(User).limit(1)).first()
        if user:
            return user

        # If no users exist, create a default admin user
        default_user = User(
            username="admin",
            full_name="Admin User",
            email="admin@example.com",
            is_admin=True,
            telegram_id=12345,
        )
        session.add(default_user)
        session.commit()
        session.refresh(default_user)
        return default_user

    # If token is provided, verify it
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# Optional current user dependency (for endpoints that work with or without auth)
async def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> Optional[User]:
    """
    Get the current user if authenticated, otherwise None.

    Args:
        token: JWT token (optional)
        session: Database session

    Returns:
        Optional[User]: The authenticated user or None
    """
    if not token:
        return None

    try:
        return await get_current_user(token, session)
    except HTTPException:
        return None


# Admin user dependency
async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the current user and verify they have admin privileges.
    For development, this will always succeed.

    Args:
        current_user: The authenticated user

    Returns:
        User: The authenticated admin user

    Raises:
        HTTPException: If the user is not an admin (disabled for development)
    """
    # For development, always allow admin access
    return current_user

    # Uncomment this for production
    # if not current_user.is_admin:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Admin privileges required",
    #     )
    # return current_user
