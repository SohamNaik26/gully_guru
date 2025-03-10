"""
Mock dependency utilities for tests
"""

from unittest.mock import AsyncMock, MagicMock
from typing import Any, Dict, List, Optional, Type, Union

from src.db.models import Gully, GullyParticipant, User, Player


class MockDBUtil:
    """
    Utility for mocking database operations and queries
    """

    @staticmethod
    def configure_get(
        mock_db: AsyncMock,
        model_class: Type,
        obj_data: Optional[Dict[str, Any]] = None,
    ):
        """
        Configure the mock database session's get method to return a mocked object

        Args:
            mock_db: The mock database session
            model_class: The model class to mock
            obj_data: The data to use for the mocked object (None for nonexistent)
        """

        async def side_effect(cls, id):
            if cls == model_class and obj_data is not None:
                # Convert dict to model instance
                return model_class(**obj_data)
            return None

        mock_db.get = AsyncMock(side_effect=side_effect)

    @staticmethod
    def configure_execute(
        mock_db: AsyncMock,
        data: Union[List[Dict[str, Any]], Dict[str, Any], None] = None,
        scalar_first: bool = False,
    ):
        """
        Configure the mock database session's execute method

        Args:
            mock_db: The mock database session
            data: Data to return (list for .all(), dict for .first(), None for empty)
            scalar_first: Whether to mock a single result or multiple results
        """
        # Create a mock result that will be returned directly (not as a coroutine)
        mock_result = MagicMock()
        mock_scalars = MagicMock()

        if scalar_first:
            if isinstance(data, dict):
                # Convert dict to model instance based on structure
                if "telegram_group_id" in data:
                    mock_model = Gully(**data)
                elif "team_name" in data:
                    mock_model = GullyParticipant(**data)
                elif "telegram_id" in data:
                    mock_model = User(**data)
                elif "player_type" in data:
                    mock_model = Player(**data)
                else:
                    mock_model = MagicMock(**data)

                mock_scalars.first.return_value = mock_model
            else:
                mock_scalars.first.return_value = data  # None or other
        else:
            if data and isinstance(data, list):
                mock_models = []
                for item in data:
                    if "telegram_group_id" in item:
                        mock_model = Gully(**item)
                    elif "team_name" in item:
                        mock_model = GullyParticipant(**item)
                    elif "telegram_id" in item:
                        mock_model = User(**item)
                    elif "player_type" in item:
                        mock_model = Player(**item)
                    else:
                        mock_model = MagicMock(**item)
                    mock_models.append(mock_model)

                mock_scalars.all.return_value = mock_models
            else:
                mock_scalars.all.return_value = data if data else []

        mock_result.scalars.return_value = mock_scalars

        # Set up the execute method to return the mock_result directly
        mock_db.execute = AsyncMock(return_value=mock_result)

    @staticmethod
    def configure_commit(mock_db: AsyncMock):
        """Configure the mock database's commit method"""
        mock_db.commit = AsyncMock()

    @staticmethod
    def configure_refresh(mock_db: AsyncMock):
        """Configure the mock database's refresh method"""
        mock_db.refresh = AsyncMock()

    @staticmethod
    def configure_add(mock_db: AsyncMock):
        """
        Configure the mock database's add method to properly handle awaitable coroutines

        This prevents "coroutine was never awaited" warnings in tests
        """
        # Use a synchronous method instead of an async method
        mock_db.add = MagicMock()
