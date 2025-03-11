from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.db.session import get_session
from src.db.models import User, UserPlayer, GullyParticipant
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
    return UserFactory.create_response(user)


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
    return UserFactory.create_response(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, session: AsyncSession = Depends(get_session)):
    """Get a user by ID."""
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    return UserFactory.create_response(user)


@router.get("/", response_model=List[UserResponseWithGullies])
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

    # Get gully_ids for each user and create responses
    user_responses = []
    for user in users:
        # Get the gully_ids for this user
        gully_query = select(GullyParticipant.gully_id).where(
            GullyParticipant.user_id == user.id
        )
        gully_result = await session.execute(gully_query)
        gully_ids = gully_result.scalars().all()

        # Create a response with the user data and gully_ids
        user_response = await UserFactory.create_response_with_gullies(user, gully_ids)
        user_responses.append(user_response)

    return user_responses


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
    # Check if user exists
    user = await session.get(User, user_player_data.user_id)
    if not user:
        raise NotFoundException(
            resource_type="User", resource_id=user_player_data.user_id
        )

    # Create new user player
    user_player = UserPlayer(
        user_id=user_player_data.user_id,
        player_id=user_player_data.player_id,
        gully_id=user_player_data.gully_id,
        purchase_price=user_player_data.purchase_price,
        is_captain=user_player_data.is_captain,
        is_vice_captain=user_player_data.is_vice_captain,
        is_playing_xi=user_player_data.is_playing_xi,
    )
    session.add(user_player)
    await session.commit()
    await session.refresh(user_player)
    return UserPlayerFactory.create_response(user_player)


@router.get("/players/{user_id}", response_model=List[UserPlayerResponse])
async def get_user_players(
    user_id: int,
    gully_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
):
    """Get all players owned by a user, optionally filtered by gully."""
    query = select(UserPlayer).where(UserPlayer.user_id == user_id)

    if gully_id:
        query = query.where(UserPlayer.gully_id == gully_id)

    result = await session.execute(query)
    user_players = result.scalars().all()
    return UserPlayerFactory.create_response_list(user_players)
