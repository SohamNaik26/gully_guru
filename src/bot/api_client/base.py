"""
Base API client for GullyGuru.
Handles authentication, request formatting, and response parsing.
"""

import logging
import httpx
import json
import time
from typing import Dict, Any, Optional, List, Union

# Configure logging
logger = logging.getLogger(__name__)


class BaseApiClient:
    """Base API client for GullyGuru."""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize the API client.

        Args:
            base_url: Base URL for the API
            api_key: API key for authentication (optional)
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {}

        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

        # Set default headers
        self.headers["Content-Type"] = "application/json"
        self.headers["Accept"] = "application/json"

    async def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        """
        Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            **kwargs: Additional arguments to pass to httpx

        Returns:
            Response data as dictionary or list, or None if request failed
        """
        # Ensure endpoint doesn't have a leading slash but does have a trailing slash
        # This matches the API's expected format based on the redirects we're seeing
        endpoint = endpoint.lstrip("/")
        if not endpoint.endswith("/") and "/" not in endpoint:
            endpoint = f"{endpoint}/"

        url = f"{self.base_url}/api/{endpoint}"

        # Add headers to kwargs
        if "headers" not in kwargs:
            kwargs["headers"] = {}
        kwargs["headers"].update(self.headers)

        # Create a client with redirect following enabled
        client_kwargs = {
            "follow_redirects": True,
            "timeout": 30.0,  # Increase timeout to handle redirects
        }

        # Log request details
        request_id = f"{method}_{endpoint}_{id(kwargs)}"
        logger.debug(f"[{request_id}] Request details: {method} {url}")
        if "params" in kwargs:
            logger.debug(f"[{request_id}] Query params: {kwargs['params']}")
        if "json" in kwargs:
            logger.debug(f"[{request_id}] Request body: {kwargs['json']}")

        try:
            async with httpx.AsyncClient(**client_kwargs) as client:
                logger.debug(f"[{request_id}] Making {method} request to {url}")
                start_time = time.time()
                response = await client.request(method, url, **kwargs)
                execution_time = time.time() - start_time

                # Log the request and response status
                logger.info(
                    f"[{request_id}] API {method} request to {url} - Status: {response.status_code} - Time: {execution_time:.4f}"
                )

                # If we got redirected, log the final URL
                if response.url != url:
                    logger.info(f"Request was redirected to: {response.url}")

                # Check if the response is successful
                if response.status_code >= 400:
                    logger.error(
                        f"HTTP error: {response.status_code} - {response.text}"
                    )
                    logger.error(
                        f"Request details: {method} {url}, Headers: {kwargs.get('headers')}"
                    )
                    if "json" in kwargs:
                        logger.error(f"Request body: {kwargs['json']}")
                    return None

                # Try to parse the response as JSON
                try:
                    # First check if there's any content
                    if not response.text.strip():
                        logger.warning(f"Empty response from API: {url}")
                        return None

                    data = response.json()

                    # Handle paginated responses
                    if isinstance(data, dict) and "items" in data:
                        return data["items"]

                    return data
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON response from API: {url}")
                    logger.error(f"Response content: {response.text}")

                    # Try to handle HTML responses (which might happen with redirects)
                    if response.text.strip().startswith(
                        "<!DOCTYPE html>"
                    ) or response.text.strip().startswith("<html>"):
                        logger.error(
                            "Received HTML response instead of JSON. API endpoint might be incorrect."
                        )

                    return None

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
            )
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error occurred: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return None

    async def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        """
        Make a GET request to the API.

        Args:
            endpoint: API endpoint
            params: Query parameters (optional)

        Returns:
            Response data as dictionary or list, or None if request failed
        """
        return await self._make_request("GET", endpoint, params=params)

    async def post(
        self, endpoint: str, json: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Make a POST request to the API.

        Args:
            endpoint: API endpoint
            json: Request body (optional)

        Returns:
            Response data as dictionary, or None if request failed
        """
        return await self._make_request("POST", endpoint, json=json)

    async def put(
        self, endpoint: str, json: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Make a PUT request to the API.

        Args:
            endpoint: API endpoint
            json: Request body (optional)

        Returns:
            Response data as dictionary, or None if request failed
        """
        return await self._make_request("PUT", endpoint, json=json)

    async def delete(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Make a DELETE request to the API.

        Args:
            endpoint: API endpoint
            params: Query parameters (optional)

        Returns:
            Response data as dictionary, or None if request failed
        """
        return await self._make_request("DELETE", endpoint, params=params)


# Global API client instance
_api_client = None


async def get_api_client() -> BaseApiClient:
    """
    Get the global API client instance.

    Returns:
        BaseApiClient instance
    """
    global _api_client
    if _api_client is None:
        import os

        # Get API configuration from environment variables
        api_url = os.getenv("API_URL", "http://localhost:8000")
        api_key = os.getenv("API_KEY")

        _api_client = BaseApiClient(api_url, api_key)
        logger.info(f"Initialized API client with base URL: {api_url}")

    return _api_client


# Add the missing initialize_api_client function
async def initialize_api_client() -> None:
    """
    Initialize the API client.
    This function is called at application startup to ensure the API client is ready.
    """
    logger.info("Initializing API client...")
    await get_api_client()
    logger.info("API client initialized successfully")
