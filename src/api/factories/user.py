"""Factory classes for creating User-related response objects."""

from typing import List

from src.api.factories.base import ResponseFactory
from src.api.schemas.user import (
    UserResponse,
    UserResponseWithGullies,
    UserPlayerResponse,
)
from src.db.models import User, UserPlayer


class UserFactory(ResponseFactory[User, UserResponse]):
    """Factory for creating User response objects."""

    response_model = UserResponse

    @classmethod
    async def create_response_with_gullies(
        cls, user: User, gully_ids: List[int]
    ) -> UserResponseWithGullies:
        """
        Create a UserResponseWithGullies object from a User model and a list of gully IDs.

        Args:
            user: The user model
            gully_ids: List of gully IDs the user is part of

        Returns:
            A UserResponseWithGullies instance
        """
        return UserResponseWithGullies(
            id=user.id,
            telegram_id=user.telegram_id,
            username=user.username,
            full_name=user.full_name,
            created_at=user.created_at,
            updated_at=user.updated_at,
            gully_ids=gully_ids,
        )


class UserPlayerFactory(ResponseFactory[UserPlayer, UserPlayerResponse]):
    """Factory for creating UserPlayer response objects."""

    response_model = UserPlayerResponse
