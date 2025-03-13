from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.db.session import get_session
from src.db.models import User
from src.api.schemas.user import (
    UserCreate,
    UserResponse,
    UserResponseWithGullies,
    UserPlayerCreate,
    UserPlayerResponse,
)
from src.api.dependencies import get_current_user
from src.api.exceptions import NotFoundException
from src.api.factories import UserFactory, UserPlayerFactory
from src.api.services import UserServiceClient

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate, session: AsyncSession = Depends(get_session)
):
    """Create a new user."""
    user_service = UserServiceClient(session)

    # Check if user with telegram_id already exists
    existing_user = await user_service.get_user_by_telegram_id(user_data.telegram_id)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with telegram_id {user_data.telegram_id} already exists",
        )

    # Create new user
    user = await user_service.create_user(user_data.dict())
    return UserFactory.create_response(user)


@router.get("/telegram/{telegram_id}", response_model=UserResponse)
async def get_user_by_telegram_id(
    telegram_id: int, session: AsyncSession = Depends(get_session)
):
    """Get a user by Telegram ID."""
    user_service = UserServiceClient(session)
    user = await user_service.get_user_by_telegram_id(telegram_id)
    if not user:
        raise NotFoundException(f"User with telegram_id {telegram_id} not found")
    return UserFactory.create_response(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, session: AsyncSession = Depends(get_session)):
    """Get a user by ID."""
    user_service = UserServiceClient(session)
    user = await user_service.get_user(user_id)
    if not user:
        raise NotFoundException(resource_type="User", resource_id=user_id)
    return UserFactory.create_response(user)


@router.get("/", response_model=List[UserResponseWithGullies])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    telegram_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
):
    """Get all users with optional filtering."""
    user_service = UserServiceClient(session)
    users_with_gullies = await user_service.get_users_with_gullies(
        skip=skip, limit=limit, telegram_id=telegram_id
    )
    return users_with_gullies


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Delete a user (can only delete yourself or admin can delete anyone)."""
    user_service = UserServiceClient(session)

    # Check if user exists
    user = await user_service.get_user(user_id)
    if not user:
        raise NotFoundException(resource_type="User", resource_id=user_id)

    # Check if user is trying to delete themselves or is an admin
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account unless you are an admin",
        )

    # Delete the user
    await user_service.delete_user(user_id)
    return None


@router.delete("/telegram/{telegram_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_telegram_id(
    telegram_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Delete a user by Telegram ID (can only delete yourself or admin can delete anyone)."""
    user_service = UserServiceClient(session)

    # Check if user exists
    user = await user_service.get_user_by_telegram_id(telegram_id)
    if not user:
        raise NotFoundException(resource_type="User", resource_id=telegram_id)

    # Check permissions - only allow users to delete themselves or admins to delete anyone
    if user.id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account unless you are an admin",
        )

    # Delete user
    await user_service.delete_user(user.id)
    return None


# User Player endpoints
@router.post(
    "/players", response_model=UserPlayerResponse, status_code=status.HTTP_201_CREATED
)
async def create_user_player(
    user_player_data: UserPlayerCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Create a new user player relationship."""
    user_service = UserServiceClient(session)

    # Check if user exists
    user = await user_service.get_user(user_player_data.user_id)
    if not user:
        raise NotFoundException(
            resource_type="User", resource_id=user_player_data.user_id
        )

    # Create new user player
    user_player = await user_service.create_user_player(user_player_data.dict())
    return UserPlayerFactory.create_response(user_player)


@router.get("/players/{user_id}", response_model=List[UserPlayerResponse])
async def get_user_players(
    user_id: int,
    gully_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
):
    """Get all players owned by a user, optionally filtered by gully."""
    user_service = UserServiceClient(session)
    user_players = await user_service.get_user_players(user_id, gully_id)
    return UserPlayerFactory.create_response_list(user_players)
