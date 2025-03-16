"""
Base API client for GullyGuru.
Handles authentication, request formatting, and response parsing.
"""

import logging
import httpx
import json
import time
from typing import Dict, Any, Optional, List, Union

from src.utils.config import settings

# Configure logging
logger = logging.getLogger(__name__)


class APIClient:
    """Base API client for making requests to the GullyGuru API."""

    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize the API client.

        Args:
            base_url: The base URL for the API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )
        logger.info(f"Initialized API client with base URL: {base_url}")

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
        logger.info("Closed API client")

    async def get(self, endpoint: str, params: Dict[str, Any] = None) -> Any:
        """
        Make a GET request to the API.

        Args:
            endpoint: The API endpoint
            params: Query parameters

        Returns:
            The response data
        """
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"GET request to {url}")

        try:
            response = await self.client.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error in GET request to {url}: {str(e)}")
            raise

    async def post(self, endpoint: str, json: Dict[str, Any] = None) -> Any:
        """
        Make a POST request to the API.

        Args:
            endpoint: The API endpoint
            json: Request body

        Returns:
            The response data
        """
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"POST request to {url}")

        try:
            response = await self.client.post(endpoint, json=json)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error in POST request to {url}: {str(e)}")
            raise

    async def put(self, endpoint: str, json: Dict[str, Any] = None) -> Any:
        """
        Make a PUT request to the API.

        Args:
            endpoint: The API endpoint
            json: Request body

        Returns:
            The response data
        """
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"PUT request to {url}")

        try:
            response = await self.client.put(endpoint, json=json)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error in PUT request to {url}: {str(e)}")
            raise

    async def delete(self, endpoint: str) -> Any:
        """
        Make a DELETE request to the API.

        Args:
            endpoint: The API endpoint

        Returns:
            The response data
        """
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"DELETE request to {url}")

        try:
            response = await self.client.delete(endpoint)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error in DELETE request to {url}: {str(e)}")
            raise


# Global API client instance
_api_client = None


async def initialize_api_client() -> APIClient:
    """
    Initialize the global API client.

    Returns:
        The initialized API client
    """
    global _api_client

    if _api_client is None:
        base_url = settings.API_BASE_URL
        logger.info(f"Initializing API client with base URL: {base_url}")
        _api_client = APIClient(base_url)

    return _api_client


async def get_api_client() -> APIClient:
    """
    Get the global API client instance, initializing it if necessary.

    Returns:
        The API client instance
    """
    global _api_client

    if _api_client is None:
        return await initialize_api_client()

    return _api_client


async def get_api_client_with_key(api_key: str) -> APIClient:
    """
    Get the API client with a specific API key.

    Args:
        api_key: The API key

    Returns:
        The API client instance
    """
    global _api_client

    if _api_client is None:
        base_url = settings.API_BASE_URL
        logger.info(f"Initializing API client with base URL: {base_url}")
        _api_client = APIClient(base_url)
        _api_client.client.headers["Authorization"] = f"Bearer {api_key}"

    return _api_client


# Add the missing initialize_api_client function
async def initialize_api_client_with_key(api_key: str) -> None:
    """
    Initialize the API client with a specific API key.
    This function is called at application startup to ensure the API client is ready.

    Args:
        api_key: The API key
    """
    logger.info("Initializing API client with a specific API key...")
    await get_api_client_with_key(api_key)
    logger.info("API client initialized successfully with a specific API key")
