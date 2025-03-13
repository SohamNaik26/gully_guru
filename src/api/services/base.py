import logging
import httpx
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class BaseService:
    """Base class for all API service clients."""

    def __init__(self, base_url: str, client: httpx.AsyncClient = None):
        """Initialize the service client.

        Args:
            base_url: The base URL for the API
            client: An optional httpx AsyncClient instance
        """
        self.base_url = base_url
        self.client = client or httpx.AsyncClient(timeout=30.0, follow_redirects=True)

    async def close(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()

    async def _make_request(
        self,
        method: str,
        url: str,
        json: Dict[str, Any] = None,
        params: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            url: URL to request
            json: JSON data to send
            params: Query parameters

        Returns:
            Response data as dictionary

        Raises:
            Exception: If the request fails
        """
        try:
            logger.info(
                f"DEBUG - Making {method} request to URL: {url} with params: {params} and json: {json}"
            )
            if method.upper() == "GET":
                response = await self.client.get(url, params=params)
            elif method.upper() == "POST":
                response = await self.client.post(url, json=json, params=params)
            elif method.upper() == "PUT":
                response = await self.client.put(url, json=json, params=params)
            elif method.upper() == "DELETE":
                response = await self.client.delete(url, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            logger.info(
                f"DEBUG - Response status: {response.status_code}, URL: {response.url}"
            )

            if response.status_code in (200, 201, 204):
                if response.status_code == 204:
                    return {"success": True}
                return response.json()

            error_detail = "Unknown error"
            try:
                error_data = response.json()
                if "detail" in error_data:
                    error_detail = error_data["detail"]
            except Exception:
                error_detail = response.text

            logger.error(
                f"API request failed: {method} {url} - Status: {response.status_code} - {error_detail}"
            )
            return {"error": error_detail, "status_code": response.status_code}

        except Exception as e:
            logger.error(f"Error making API request: {e}")
            return {"error": str(e), "status_code": 500}


class BaseServiceClient:
    """Base class for all database service clients."""

    def __init__(self, db: AsyncSession):
        """Initialize the service client.

        Args:
            db: Database session
        """
        self.db = db
