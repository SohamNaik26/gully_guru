from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from src.db.session import get_session
from src.db.models import User
from src.models.api import UserCreate, UserResponse
from src.api.dependencies import get_current_user, get_admin_user
from src.api.exceptions import NotFoundException

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, session: Session = Depends(get_session)):
    """Create a new user."""
    # Check if user with telegram_id already exists
    existing_user = session.exec(
        select(User).where(User.telegram_id == user_data.telegram_id)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with telegram_id {user_data.telegram_id} already exists",
        )

    # Create new user
    user = User(**user_data.dict())
    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get information about the current authenticated user."""
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, session: Session = Depends(get_session)):
    """Get a user by ID."""
    user = session.get(User, user_id)
    if not user:
        raise NotFoundException(resource_type="User", resource_id=user_id)

    return user


@router.get("/", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    _: User = Depends(get_admin_user),  # Only admins can list all users
):
    """Get all users (admin only)."""
    users = session.exec(select(User).offset(skip).limit(limit)).all()
    return users


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Delete a user (can only delete yourself or admin can delete anyone)."""
    # Check if user exists
    user = session.get(User, user_id)
    if not user:
        raise NotFoundException(resource_type="User", resource_id=user_id)

    # Check permissions
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account",
        )

    # Delete user
    session.delete(user)
    session.commit()

    return None
