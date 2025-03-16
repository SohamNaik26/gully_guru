"""
User routes for the GullyGuru API.
This module provides API endpoints for user-related operations.
"""

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.api.dependencies.database import get_db
from src.api.schemas.user import (
    UserCreate,
    UserResponse,
    UserResponseWithGullies,
    ParticipantPlayerCreate,
    ParticipantPlayerResponse,
    UserUpdate,
)
from src.api.exceptions import NotFoundException, handle_exceptions
from src.api.factories.user import UserResponseFactory
from src.api.services.user import UserService
from src.api.schemas.pagination import PaginatedResponse
from src.api.dependencies.pagination import pagination_params, PaginationParams

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@handle_exceptions
async def create_user(
    user: UserCreate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user.

    Args:
        user: User data including telegram_id, first_name, last_name, and username
        db: Database session

    Returns:
        UserResponse: Created user with ID and timestamps
    """
    user_service = UserService(db)
    user_data = await user_service.create_user(user.dict())
    return UserResponseFactory.create_response(user_data)


@router.get("/", response_model=PaginatedResponse[UserResponse])
@handle_exceptions
async def get_users(
    telegram_id: Optional[int] = Query(None, description="Filter by Telegram ID"),
    pagination: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a paginated list of users with optional filtering.

    Args:
        telegram_id: Optional filter by Telegram ID
        pagination: Pagination parameters
        db: Database session

    Returns:
        PaginatedResponse[UserResponse]: Paginated list of users
    """
    user_service = UserService(db)

    # Prioritize telegram_id filtering for bot integration
    if telegram_id is not None:
        users, total = await user_service.get_users_by_telegram_id(
            telegram_id=telegram_id,
            limit=pagination.limit,
            offset=pagination.offset,
        )
    else:
        users, total = await user_service.get_users(
            limit=pagination.limit,
            offset=pagination.offset,
        )

    return {
        "items": [UserResponseFactory.create_response(user) for user in users],
        "total": total,
        "limit": pagination.limit,
        "offset": pagination.offset,
    }


@router.get("/{user_id}", response_model=UserResponse)
@handle_exceptions
async def get_user(
    user_id: int = Path(..., description="ID of the user"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a user by ID.

    Args:
        user_id: User ID
        db: Database session

    Returns:
        UserResponse: User details

    Raises:
        NotFoundException: If user not found
    """
    user_service = UserService(db)
    user = await user_service.get_user(user_id)
    if not user:
        raise NotFoundException(resource_type="User", resource_id=user_id)
    return UserResponseFactory.create_response(user)


@router.put("/{user_id}", response_model=UserResponse)
@handle_exceptions
async def update_user(
    user_id: int = Path(..., description="ID of the user"),
    user_update: UserUpdate = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a user by ID.

    Args:
        user_id: User ID
        user_update: User data to update
        db: Database session

    Returns:
        UserResponse: Updated user details

    Raises:
        NotFoundException: If user not found
    """
    user_service = UserService(db)
    user = await user_service.update_user(user_id, user_update.dict(exclude_unset=True))
    if not user:
        raise NotFoundException(resource_type="User", resource_id=user_id)
    return UserResponseFactory.create_response(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_exceptions
async def delete_user(
    user_id: int = Path(..., description="ID of the user"),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a user by ID.

    Args:
        user_id: User ID
        db: Database session

    Returns:
        None

    Raises:
        NotFoundException: If user not found
    """
    user_service = UserService(db)
    success = await user_service.delete_user(user_id)
    if not success:
        raise NotFoundException(resource_type="User", resource_id=user_id)
    return None
