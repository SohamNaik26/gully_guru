"""
Base API client for GullyGuru.
Handles request formatting and response parsing.
"""

import logging
import httpx
import json
from typing import Dict, Any, Optional
import os

from src.utils.config import settings

# Configure logging
logger = logging.getLogger(__name__)


class BaseApiClient:
    """Base class for all API clients."""

    def __init__(self, base_url: str = None):
        """Initialize the API client with the base URL."""
        self.base_url = base_url or os.getenv("API_BASE_URL", "http://localhost:8000")
        logger.info(f"Initialized BaseApiClient with base URL: {self.base_url}")
        self._api_client = None

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            data: Request body data (for POST/PUT)
            params: Query parameters
            headers: Request headers

        Returns:
            Response data as dictionary
        """
        # Debug log to help diagnose issues
        logger.debug(f"_make_request called with method={method}, endpoint={endpoint}")
        logger.debug(f"self.base_url={self.base_url}, type={type(self.base_url)}")

        # Ensure base_url is a string
        if not isinstance(self.base_url, str):
            logger.error(
                f"Invalid base_url type: {type(self.base_url)}, value: {self.base_url}"
            )
            self.base_url = settings.API_BASE_URL  # Use default from settings
            logger.info(f"Reset base_url to: {self.base_url}")

        # Ensure endpoint starts with /api
        if not endpoint.startswith("/api"):
            # Add /api prefix if not already present
            endpoint = f"/api{endpoint}"
            logger.debug(f"Added /api prefix to endpoint: {endpoint}")

        url = f"{self.base_url}{endpoint}"
        logger.debug(f"Full URL: {url}")

        default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if headers:
            default_headers.update(headers)

        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=30) as client:
                logger.debug(f"Making {method} request to {url}")

                if method.upper() == "GET":
                    response = await client.get(
                        endpoint, params=params, headers=default_headers
                    )
                elif method.upper() == "POST":
                    response = await client.post(
                        endpoint, json=data, params=params, headers=default_headers
                    )
                elif method.upper() == "PUT":
                    response = await client.put(
                        endpoint, json=data, params=params, headers=default_headers
                    )
                elif method.upper() == "DELETE":
                    response = await client.delete(
                        endpoint, params=params, headers=default_headers
                    )
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()
                return await self._handle_response(response)
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "error": e.response.text,
                "status": e.response.status_code,
            }
        except Exception as e:
            logger.error(f"Error in API request to {url}: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """
        Handle the API response.

        Args:
            response: httpx response object

        Returns:
            Response data as dictionary
        """
        try:
            # Try to parse JSON response
            data = response.json()
            return {"success": True, "data": data}
        except json.JSONDecodeError:
            # If not JSON, get text
            text = response.text
            logger.warning(f"Non-JSON response: {text[:100]}...")
            return {"success": True, "data": {"text": text}}


class APIClient:
    """API client for making requests to the GullyGuru API."""

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


async def get_api_client_with_base_url(base_url: str = None) -> BaseApiClient:
    """
    Get an instance of the base API client.

    Args:
        base_url: Optional base URL override

    Returns:
        BaseApiClient instance
    """
    return BaseApiClient(base_url)


def debug_api_client():
    """
    Print debug information about the API client.
    """
    logger.info("=== API Client Debug Information ===")
    logger.info(f"Global _api_client: {_api_client}")
    if _api_client:
        logger.info(f"_api_client.base_url: {_api_client.base_url}")
    logger.info("===================================")
