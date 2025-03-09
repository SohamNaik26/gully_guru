import logging
from typing import Dict, Any, Optional, List
import httpx

from src.api.services.base import BaseService

logger = logging.getLogger(__name__)


class GullyService(BaseService):
    """Client for interacting with gully-related API endpoints."""

    def __init__(self, base_url: str, client: httpx.AsyncClient = None):
        """Initialize the gully service client.

        Args:
            base_url: The base URL for the API
            client: An optional httpx AsyncClient instance
        """
        super().__init__(base_url, client)
        self.endpoint = f"{self.base_url}/gullies/"

    def _build_url(self, *path_segments: str) -> str:
        """Build a URL with proper formatting.

        Args:
            *path_segments: Path segments to append to the base endpoint

        Returns:
            Properly formatted URL without double slashes
        """
        # Start with the base endpoint without trailing slash
        base = self.endpoint.rstrip("/")

        # Join all path segments, ensuring each has no leading/trailing slashes
        path = "/".join(segment.strip("/") for segment in path_segments if segment)

        # Return the combined URL
        return f"{base}/{path}" if path else base

    async def get_all_gullies(self) -> List[Dict[str, Any]]:
        """Get all gullies.

        Returns:
            List of gullies
        """
        # Add default query parameters to avoid redirect
        params = {"skip": 0, "limit": 100}
        url = self._build_url()
        logger.debug(f"Making request to {url} with params {params}")
        response = await self._make_request("GET", url, params=params)
        if "error" in response:
            error_msg = response.get("error", "Unknown error")
            status_code = response.get("status_code", "Unknown")
            logger.error(
                f"Error getting all gullies: {error_msg} (Status: {status_code})"
            )
            return []
        return response

    async def get_gully(self, gully_id: int) -> Optional[Dict[str, Any]]:
        """Get a gully by ID.

        Args:
            gully_id: The ID of the gully

        Returns:
            Gully data or None if not found
        """
        url = self._build_url(str(gully_id))
        logger.debug(f"Making request to {url}")
        response = await self._make_request("GET", url)
        if "error" in response:
            error_msg = response.get("error", "Unknown error")
            status_code = response.get("status_code", "Unknown")
            logger.error(f"Error getting gully: {error_msg} (Status: {status_code})")
            return None
        return response

    async def get_gully_by_group(self, group_id: int) -> Optional[Dict[str, Any]]:
        """Get a gully by Telegram group ID.

        Args:
            group_id: The Telegram group ID

        Returns:
            Gully data or None if not found
        """
        url = self._build_url("group", str(group_id))
        logger.debug(f"Making request to {url}")
        response = await self._make_request("GET", url)
        if "error" in response:
            error_msg = response.get("error", "Unknown error")
            status_code = response.get("status_code", "Unknown")
            logger.error(
                f"Error getting gully by group: {error_msg} (Status: {status_code})"
            )
            return None
        return response

    async def create_gully(
        self,
        name: str,
        telegram_group_id: int,
    ) -> Optional[Dict[str, Any]]:
        """Create a new gully.

        Args:
            name: The name of the gully
            telegram_group_id: The Telegram group ID

        Returns:
            The created gully or None if creation failed
        """
        # Use JSON body instead of query parameters
        data = {
            "name": name,
            "telegram_group_id": telegram_group_id,
        }
        url = self._build_url()
        logger.debug(f"Creating gully with data: {data}")
        response = await self._make_request("POST", url, json=data)
        if "error" in response:
            error_msg = response.get("error", "Unknown error")
            status_code = response.get("status_code", "Unknown")
            logger.error(f"Error creating gully: {error_msg} (Status: {status_code})")
            return None
        return response

    async def get_gully_participants(
        self, gully_id: int, skip: int = 0, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get participants of a gully.

        Args:
            gully_id: The ID of the gully
            skip: Number of participants to skip
            limit: Maximum number of participants to return

        Returns:
            List of gully participants
        """
        params = {"skip": skip, "limit": limit}
        url = self._build_url("participants", str(gully_id))
        response = await self._make_request(
            "GET",
            url,
            params=params,
        )
        if "error" in response:
            logger.error(f"Error getting gully participants: {response['error']}")
            return []
        return response

    async def get_user_gully_participations(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all gullies a user participates in.

        Args:
            user_id: The ID of the user

        Returns:
            List of gully participations
        """
        url = self._build_url("user-gullies", str(user_id))
        response = await self._make_request("GET", url)
        if "error" in response:
            logger.error(
                f"Error getting user gully participations: {response['error']}"
            )
            return []
        return response

    async def get_user_gully_participation(
        self, user_id: int, gully_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get a user's participation in a specific gully.

        Args:
            user_id: The ID of the user
            gully_id: The ID of the gully

        Returns:
            Gully participation data or None if not found
        """
        # First get all participations
        participations = await self.get_user_gully_participations(user_id)

        # Find the specific participation for this gully
        for participation in participations:
            if participation.get("gully_id") == gully_id:
                return participation

        # Not found
        logger.debug(f"User {user_id} is not a participant in gully {gully_id}")
        return None

    async def add_user_to_gully(
        self, user_id: int, gully_id: int, role: str = "member"
    ) -> Optional[Dict[str, Any]]:
        """Add a user to a gully.

        Args:
            user_id: The ID of the user
            gully_id: The ID of the gully
            role: The role of the user in the gully

        Returns:
            Gully participant data or None if addition failed
        """
        url = self._build_url("participants", str(gully_id), str(user_id))
        response = await self._make_request(
            "POST",
            url,
            params={"role": role},
        )
        if "error" in response:
            logger.error(f"Error adding user to gully: {response['error']}")
            return None
        return response

    async def set_active_gully(self, participant_id: int) -> Optional[Dict[str, Any]]:
        """Set a gully as active for a user.

        Args:
            participant_id: The ID of the gully participant

        Returns:
            Result of the operation
        """
        url = self._build_url("participants", str(participant_id), "activate")
        response = await self._make_request("PUT", url)
        if "error" in response:
            logger.error(f"Error setting active gully: {response['error']}")
            return None
        return response

    async def update_gully_participant_role(
        self, participant_id: int, role: str
    ) -> Optional[Dict[str, Any]]:
        """Update a participant's role in a gully.

        Args:
            participant_id: The ID of the gully participant
            role: The new role (admin, member, owner)

        Returns:
            Result of the operation
        """
        url = self._build_url("participants", str(participant_id), "role")
        response = await self._make_request("PUT", url, params={"role": role})
        if "error" in response:
            logger.error(f"Error updating participant role: {response['error']}")
            return None
        return response
