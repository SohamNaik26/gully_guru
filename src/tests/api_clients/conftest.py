import pytest
import httpx
from unittest.mock import MagicMock


@pytest.fixture
def mock_httpx_client():
    """
    Create a mock httpx.AsyncClient for testing API clients.

    Returns:
        MagicMock: A mock httpx.AsyncClient instance
    """
    client = MagicMock(spec=httpx.AsyncClient)

    # Setup default response for successful requests
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}

    # Configure client methods to return the mock response by default
    client.get.return_value = mock_response
    client.post.return_value = mock_response
    client.put.return_value = mock_response
    client.delete.return_value = mock_response

    return client


@pytest.fixture
def mock_response_factory():
    """
    Create a factory function for generating mock responses.

    Returns:
        function: A factory function that creates mock responses
    """

    def _create_mock_response(status_code=200, json_data=None, text=None):
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = status_code

        if json_data is not None:
            mock_response.json.return_value = json_data

        if text is not None:
            mock_response.text = text

        return mock_response

    return _create_mock_response


@pytest.fixture
def base_url():
    """
    Provide a base URL for testing API clients.

    Returns:
        str: The base URL for API clients
    """
    return "http://testserver/api"
