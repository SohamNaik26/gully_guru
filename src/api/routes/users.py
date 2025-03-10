from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.db.session import get_session
from src.db.models import User
from src.api.schemas.user import (
    UserCreate,
    UserResponse,
)
from src.api.dependencies import get_current_user
from src.api.exceptions import NotFoundException

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate, session: AsyncSession = Depends(get_session)
):
    """Create a new user."""
    # Check if user with telegram_id already exists
    result = await session.execute(
        select(User).where(User.telegram_id == user_data.telegram_id)
    )
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with telegram_id {user_data.telegram_id} already exists",
        )

    # Create new user
    user = User(
        telegram_id=user_data.telegram_id,
        username=user_data.username,
        full_name=user_data.full_name,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.get("/telegram/{telegram_id}", response_model=UserResponse)
async def get_user_by_telegram_id(
    telegram_id: int, session: AsyncSession = Depends(get_session)
):
    """Get a user by Telegram ID."""
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with telegram_id {telegram_id} not found",
        )
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, session: AsyncSession = Depends(get_session)):
    """Get a user by ID."""
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    return user


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    telegram_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
):
    """Get all users with optional filtering."""
    query = select(User)

    if telegram_id:
        query = query.where(User.telegram_id == telegram_id)

    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    users = result.scalars().all()
    return users


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Delete a user (can only delete yourself or admin can delete anyone)."""
    # Check if user exists
    user = await session.get(User, user_id)
    if not user:
        raise NotFoundException(resource_type="User", resource_id=user_id)

    # Check permissions - only allow users to delete themselves
    # Admin check is removed since we no longer have is_admin field
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account",
        )

    # Delete user
    await session.delete(user)
    await session.commit()

    return None


@router.delete("/telegram/{telegram_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_telegram_id(
    telegram_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Delete a user by Telegram ID (can only delete yourself or admin can delete anyone)."""
    # Check if user exists
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalars().first()
    if not user:
        raise NotFoundException(resource_type="User", resource_id=telegram_id)

    # Check permissions - only allow users to delete themselves
    if user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account",
        )

    # Delete user
    await session.delete(user)
    await session.commit()

    return None
