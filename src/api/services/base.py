"""
Base service for the GullyGuru API.
This module provides base classes for services.
"""

import logging
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)


class BaseService:
    """Base class for services."""

    def __init__(
        self, base_url: Optional[str] = None, client: Optional[httpx.AsyncClient] = None
    ):
        """
        Initialize the base service.

        Args:
            base_url: Base URL for API requests
            client: HTTP client for making requests
        """
        self.base_url = base_url
        self.client = client or httpx.AsyncClient()

    async def _make_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            url: URL to request
            params: Query parameters
            json: JSON body

        Returns:
            Response data
        """
        try:
            response = await self.client.request(
                method=method, url=url, params=params, json=json, timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            return {"error": str(e)}
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {"error": str(e)}


class BaseServiceClient:
    """Base class for service clients."""

    def __init__(self, base_url: str, client: Optional[httpx.AsyncClient] = None):
        """
        Initialize the base service client.

        Args:
            base_url: Base URL for API requests
            client: HTTP client for making requests
        """
        self.base_url = base_url
        self.client = client or httpx.AsyncClient()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            params: Query parameters
            json: JSON body

        Returns:
            Response data
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            response = await self.client.request(
                method=method, url=url, params=params, json=json, timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            return {"error": str(e)}
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {"error": str(e)}
