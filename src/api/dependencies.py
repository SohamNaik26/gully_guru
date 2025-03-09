from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from typing import Optional

from src.db.session import get_session
from src.db.models import User

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
            telegram_id=12345,
        )
        session.add(default_user)
        session.commit()
        session.refresh(default_user)
        return default_user

    # If token is provided, use a simple token-to-user_id mapping for development
    # In a real app, you would verify the token properly
    try:
        # Simple development implementation - assume token is the user_id
        user_id = int(token)
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


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
async def get_admin_user(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> User:
    """
    Get the current user and verify they have admin privileges in any gully.
    For development, this will always succeed.

    Args:
        current_user: The authenticated user
        session: Database session

    Returns:
        User: The authenticated admin user

    Raises:
        HTTPException: If the user is not an admin in any gully
    """
    # For development, always allow admin access
    return current_user

    # Uncomment this for production
    # # Check if user is an admin in any gully
    # admin_participation = session.exec(
    #     select(GullyParticipant).where(
    #         (GullyParticipant.user_id == current_user.id) &
    #         (GullyParticipant.role == "admin")
    #     )
    # ).first()
    #
    # if not admin_participation:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Admin privileges required",
    #     )
    # return current_user


# Gully admin user dependency
async def get_gully_admin_user(
    gully_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> User:
    """
    Get the current user and verify they have admin privileges in the specified gully.
    For development, this will always succeed.

    Args:
        gully_id: The ID of the gully to check admin privileges for
        current_user: The authenticated user
        session: Database session

    Returns:
        User: The authenticated admin user

    Raises:
        HTTPException: If the user is not an admin in the specified gully
    """
    # For development, always allow admin access
    return current_user

    # Uncomment this for production
    # # Check if user is an admin in the specified gully
    # admin_participation = session.exec(
    #     select(GullyParticipant).where(
    #         (GullyParticipant.user_id == current_user.id) &
    #         (GullyParticipant.gully_id == gully_id) &
    #         (GullyParticipant.role.in_(["admin", "owner"]))
    #     )
    # ).first()
    #
    # if not admin_participation:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail=f"Admin privileges required for gully {gully_id}",
    #     )
    # return current_user
