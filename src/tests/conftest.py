import os
import pytest
from typing import Any, Generator, Dict, Optional, Callable
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from src.app import app
from src.db.session import get_session
from src.api.dependencies import get_current_user
from src.tests.utils.mock_models import MockUser

# Ensure test environment variables are set
os.environ["TEST_MODE"] = "true"
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["API_BASE_URL"] = "http://testserver/api"


def create_mock_db_session(
    query_results: Dict[str, Any] = None,
    add_callback: Optional[Callable] = None,
    commit_callback: Optional[Callable] = None,
    refresh_callback: Optional[Callable] = None,
):
    """
    Creates a pre-configured mock DB session with common operations.

    Args:
        query_results: Dictionary mapping query strings to their results
        add_callback: Function to call when add() is called
        commit_callback: Function to call when commit() is called
        refresh_callback: Function to call when refresh() is called

    Returns:
        AsyncMock: Configured mock DB session
    """
    mock_db = AsyncMock()

    # Configure execute to return appropriate results based on the query
    if query_results:

        def execute_side_effect(query, *args, **kwargs):
            query_str = str(query)
            for key, result in query_results.items():
                if key in query_str:
                    mock_result = MagicMock()
                    mock_scalars = MagicMock()

                    # Configure for both list and single item results
                    if isinstance(result, list):
                        mock_scalars.all.return_value = result
                    else:
                        mock_scalars.first.return_value = result

                    mock_result.scalars.return_value = mock_scalars
                    return mock_result

            # Default empty result
            mock_result = MagicMock()
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = []
            mock_scalars.first.return_value = None
            mock_result.scalars.return_value = mock_scalars
            return mock_result

        mock_db.execute = AsyncMock(side_effect=execute_side_effect)
    else:
        # Default empty results
        execute_result = MagicMock()
        execute_result.scalars.return_value.all.return_value = []
        execute_result.scalars.return_value.first.return_value = None
        mock_db.execute = AsyncMock(return_value=execute_result)

    # Configure add, commit, and refresh
    if add_callback:
        mock_db.add = AsyncMock(side_effect=add_callback)
    else:
        mock_db.add = AsyncMock()

    if commit_callback:
        mock_db.commit = AsyncMock(side_effect=commit_callback)
    else:
        mock_db.commit = AsyncMock()

    if refresh_callback:
        mock_db.refresh = AsyncMock(side_effect=refresh_callback)
    else:
        mock_db.refresh = AsyncMock()

    return mock_db


@pytest.fixture
def mock_db():
    """
    Creates a mock DB session for testing.
    Replaces the need for actual database connections.
    """
    return create_mock_db_session()


@pytest.fixture
def mock_user():
    """
    Creates a mock user for testing endpoints that require authentication.
    As per requirements, we'll bypass actual auth.
    """
    return MockUser(
        id=1, telegram_id=12345678, username="test_user", full_name="Test User"
    )


@pytest.fixture
def test_client(mock_db, mock_user) -> Generator:
    """
    Creates a TestClient with mocked dependencies.
    """
    # Override the session and user dependencies
    app.dependency_overrides[get_session] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_user

    with TestClient(app) as client:
        yield client

    # Clear dependency overrides after test
    app.dependency_overrides.clear()


@pytest.fixture
def mock_response_factory():
    """
    Factory to create mock responses for database queries
    """

    def _factory(data: Any = None, scalar_first: bool = False):
        mock_response = AsyncMock()

        if scalar_first:
            # For single item responses
            mock_scalars = AsyncMock()
            mock_scalars.first.return_value = data
            mock_response.scalars.return_value = mock_scalars
        else:
            # For list responses
            mock_scalars = AsyncMock()
            mock_scalars.all.return_value = data
            mock_response.scalars.return_value = mock_scalars

        return mock_response

    return _factory
