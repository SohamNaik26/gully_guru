"""Factory classes for creating User-related response objects."""

from typing import List, Dict, Any

from src.api.factories.base import ResponseFactory
from src.api.schemas.user import (
    UserResponse,
    UserResponseWithGullies,
    ParticipantPlayerResponse,
    GullyParticipantResponse,
)
from src.db.models import User, ParticipantPlayer


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


class ParticipantPlayerFactory(
    ResponseFactory[ParticipantPlayer, ParticipantPlayerResponse]
):
    """Factory for creating ParticipantPlayer response objects."""

    response_model = ParticipantPlayerResponse


class UserResponseFactory:
    """Factory for creating UserResponse objects."""

    @staticmethod
    def create_response(user_data: Dict[str, Any]) -> UserResponse:
        """
        Create a UserResponse from user data.

        Args:
            user_data: Dictionary containing user data

        Returns:
            UserResponse object
        """
        return UserResponse(
            id=user_data["id"],
            telegram_id=user_data["telegram_id"],
            username=user_data["username"],
            full_name=user_data["full_name"],
            created_at=user_data["created_at"],
            updated_at=user_data["updated_at"],
            gully_ids=[],  # Use empty list as default since we're not fetching gully_ids
        )

    @staticmethod
    def create_response_list(users_data: List[Dict[str, Any]]) -> List[UserResponse]:
        """
        Create a list of UserResponse objects from user data.

        Args:
            users_data: List of dictionaries containing user data

        Returns:
            List of UserResponse objects
        """
        return [UserResponseFactory.create_response(user) for user in users_data]


class GullyParticipantResponseFactory:
    """Factory for creating GullyParticipantResponse objects."""

    @staticmethod
    def create_response(participant_data: Dict[str, Any]) -> GullyParticipantResponse:
        """
        Create a GullyParticipantResponse from participant data.

        Args:
            participant_data: Dictionary containing participant data

        Returns:
            GullyParticipantResponse object
        """
        return GullyParticipantResponse(
            id=participant_data["id"],
            user_id=participant_data["user_id"],
            gully_id=participant_data["gully_id"],
            team_name=participant_data["team_name"],
            budget=participant_data["budget"],
            points=participant_data["points"],
            role=participant_data["role"],
            created_at=participant_data["created_at"],
            updated_at=participant_data["updated_at"],
        )

    @staticmethod
    def create_response_list(
        participants_data: List[Dict[str, Any]],
    ) -> List[GullyParticipantResponse]:
        """
        Create a list of GullyParticipantResponse objects from participant data.

        Args:
            participants_data: List of dictionaries containing participant data

        Returns:
            List of GullyParticipantResponse objects
        """
        return [
            GullyParticipantResponseFactory.create_response(participant)
            for participant in participants_data
        ]


class ParticipantPlayerResponseFactory:
    """Factory for creating ParticipantPlayerResponse objects."""

    @staticmethod
    def create_response(player_data: Dict[str, Any]) -> ParticipantPlayerResponse:
        """
        Create a ParticipantPlayerResponse from player data.

        Args:
            player_data: Dictionary containing participant player data

        Returns:
            ParticipantPlayerResponse object
        """
        return ParticipantPlayerResponse(
            id=player_data["id"],
            gully_participant_id=player_data["gully_participant_id"],
            player_id=player_data["player_id"],
            purchase_price=player_data["purchase_price"],
            purchase_date=player_data["purchase_date"],
            is_captain=player_data["is_captain"],
            is_vice_captain=player_data["is_vice_captain"],
            is_playing_xi=player_data["is_playing_xi"],
            status=player_data["status"],
            created_at=player_data["created_at"],
            updated_at=player_data["updated_at"],
        )

    @staticmethod
    def create_response_list(
        players_data: List[Dict[str, Any]],
    ) -> List[ParticipantPlayerResponse]:
        """
        Create a list of ParticipantPlayerResponse objects from player data.

        Args:
            players_data: List of dictionaries containing participant player data

        Returns:
            List of ParticipantPlayerResponse objects
        """
        return [
            ParticipantPlayerResponseFactory.create_response(player)
            for player in players_data
        ]
