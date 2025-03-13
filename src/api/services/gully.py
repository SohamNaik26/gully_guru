"""
Gully service for the GullyGuru API.
This module provides client methods for interacting with gully-related API endpoints and database operations.
"""

import logging
from typing import Dict, Any, Optional, List
import httpx

from sqlmodel import select

from src.api.services.base import BaseService, BaseServiceClient
from src.db.models.models import Gully, GullyParticipant

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
        # Main resources endpoints
        self.gullies_endpoint = f"{self.base_url}/gullies"
        self.participants_endpoint = f"{self.base_url}/gullies/participants/"

    def _build_gullies_url(self, *path_segments: str) -> str:
        """Build a URL for gullies endpoints with proper formatting.

        Args:
            *path_segments: Path segments to append to the gullies endpoint

        Returns:
            Properly formatted URL without double slashes
        """
        # Start with the base endpoint without trailing slash
        base = self.gullies_endpoint.rstrip("/")

        # Join all path segments, ensuring each has no leading/trailing slashes
        path = "/".join(segment.strip("/") for segment in path_segments if segment)

        # Return the combined URL
        return f"{base}/{path}" if path else base

    def _build_participants_url(self, *path_segments: str) -> str:
        """Build a URL for participants endpoints with proper formatting.

        Args:
            *path_segments: Path segments to append to the participants endpoint

        Returns:
            Properly formatted URL without double slashes
        """
        # Start with the base endpoint without trailing slash
        base = self.participants_endpoint.rstrip("/")

        # Join all path segments, ensuring each has no leading/trailing slashes
        path = "/".join(segment.strip("/") for segment in path_segments if segment)

        # Return the combined URL
        return f"{base}/{path}" if path else base

    async def get_gullies(
        self, skip: int = 0, limit: int = 10, user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get a list of gullies with optional filtering.

        Args:
            skip: Number of gullies to skip
            limit: Maximum number of gullies to return
            user_id: Filter by user ID (gullies the user is participating in)

        Returns:
            List of gullies
        """
        params = {"skip": skip, "limit": limit}
        if user_id:
            params["user_id"] = user_id

        response = await self._make_request("GET", self.gullies_endpoint, params=params)
        if "error" in response:
            logger.error(f"Error getting gullies: {response['error']}")
            return []
        return response

    async def get_gully(self, gully_id: int) -> Optional[Dict[str, Any]]:
        """Get a gully by ID.

        Args:
            gully_id: The ID of the gully

        Returns:
            Gully data or None if not found
        """
        response = await self._make_request(
            "GET", self._build_gullies_url(str(gully_id))
        )
        if "error" in response:
            logger.error(f"Error getting gully: {response['error']}")
            return None
        return response

    async def create_gully(
        self, gully_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Create a new gully.

        Args:
            gully_data: Gully data to create

        Returns:
            Created gully data or None if creation failed
        """
        response = await self._make_request(
            "POST", self.gullies_endpoint, json=gully_data
        )
        if "error" in response:
            logger.error(f"Error creating gully: {response['error']}")
            return None
        return response

    async def update_gully(
        self, gully_id: int, gully_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update a gully.

        Args:
            gully_id: The ID of the gully to update
            gully_data: Gully data to update

        Returns:
            Updated gully data or None if update failed
        """
        response = await self._make_request(
            "PUT", self._build_gullies_url(str(gully_id)), json=gully_data
        )
        if "error" in response:
            logger.error(f"Error updating gully: {response['error']}")
            return None
        return response

    async def delete_gully(self, gully_id: int) -> bool:
        """Delete a gully.

        Args:
            gully_id: The ID of the gully to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        response = await self._make_request(
            "DELETE", self._build_gullies_url(str(gully_id))
        )
        if "error" in response:
            logger.error(f"Error deleting gully: {response['error']}")
            return False
        return True

    async def get_participants(self, gully_id: int) -> List[Dict[str, Any]]:
        """Get participants of a gully.

        Args:
            gully_id: The ID of the gully

        Returns:
            List of participants
        """
        response = await self._make_request(
            "GET", self._build_participants_url(str(gully_id))
        )
        if "error" in response:
            logger.error(f"Error getting participants: {response['error']}")
            return []
        return response

    async def add_participant(
        self, gully_id: int, participant_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Add a participant to a gully.

        Args:
            gully_id: The ID of the gully
            participant_data: Participant data to add

        Returns:
            Added participant data or None if addition failed
        """
        response = await self._make_request(
            "POST",
            self._build_participants_url(str(gully_id)),
            json=participant_data,
        )
        if "error" in response:
            logger.error(f"Error adding participant: {response['error']}")
            return None
        return response

    async def remove_participant(self, gully_id: int, user_id: int) -> bool:
        """Remove a participant from a gully.

        Args:
            gully_id: The ID of the gully
            user_id: The ID of the user to remove

        Returns:
            True if removal was successful, False otherwise
        """
        response = await self._make_request(
            "DELETE", self._build_participants_url(str(gully_id), str(user_id))
        )
        if "error" in response:
            logger.error(f"Error removing participant: {response['error']}")
            return False
        return True


class GullyServiceClient(BaseServiceClient):
    """Client for interacting with gully-related database operations."""

    async def get_gullies(
        self, skip: int = 0, limit: int = 10, user_id: Optional[int] = None
    ) -> List[Gully]:
        """Get a list of gullies with optional filtering.

        Args:
            skip: Number of gullies to skip
            limit: Maximum number of gullies to return
            user_id: Filter by user ID (gullies the user is participating in)

        Returns:
            List of gullies
        """
        if user_id:
            # Get gullies the user is participating in
            stmt = (
                select(Gully)
                .join(
                    GullyParticipant,
                    GullyParticipant.gully_id == Gully.id,
                )
                .where(GullyParticipant.user_id == user_id)
                .offset(skip)
                .limit(limit)
            )
        else:
            # Get all gullies
            stmt = select(Gully).offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_gully(self, gully_id: int) -> Optional[Gully]:
        """Get a gully by ID.

        Args:
            gully_id: The ID of the gully

        Returns:
            Gully object or None if not found
        """
        return await self.db.get(Gully, gully_id)

    async def create_gully(self, gully_data: Dict[str, Any]) -> Gully:
        """Create a new gully.

        Args:
            gully_data: Gully data to create

        Returns:
            Created gully object
        """
        gully = Gully(**gully_data)
        self.db.add(gully)
        await self.db.commit()
        await self.db.refresh(gully)
        return gully

    async def update_gully(
        self, gully_id: int, gully_data: Dict[str, Any]
    ) -> Optional[Gully]:
        """Update a gully.

        Args:
            gully_id: The ID of the gully to update
            gully_data: Gully data to update

        Returns:
            Updated gully object or None if not found
        """
        gully = await self.db.get(Gully, gully_id)
        if not gully:
            return None

        for key, value in gully_data.items():
            setattr(gully, key, value)

        await self.db.commit()
        await self.db.refresh(gully)
        return gully

    async def delete_gully(self, gully_id: int) -> bool:
        """Delete a gully.

        Args:
            gully_id: The ID of the gully to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        gully = await self.db.get(Gully, gully_id)
        if not gully:
            return False

        await self.db.delete(gully)
        await self.db.commit()
        return True

    async def get_participants(self, gully_id: int) -> List[GullyParticipant]:
        """Get participants of a gully.

        Args:
            gully_id: The ID of the gully

        Returns:
            List of participants
        """
        stmt = select(GullyParticipant).where(GullyParticipant.gully_id == gully_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def add_participant(
        self, gully_id: int, participant_data: Dict[str, Any]
    ) -> GullyParticipant:
        """Add a participant to a gully.

        Args:
            gully_id: The ID of the gully
            participant_data: Participant data to add

        Returns:
            Added participant object
        """
        # Ensure gully_id is set
        participant_data["gully_id"] = gully_id

        participant = GullyParticipant(**participant_data)
        self.db.add(participant)
        await self.db.commit()
        await self.db.refresh(participant)
        return participant

    async def remove_participant(self, gully_id: int, user_id: int) -> bool:
        """Remove a participant from a gully.

        Args:
            gully_id: The ID of the gully
            user_id: The ID of the user to remove

        Returns:
            True if removal was successful, False otherwise
        """
        stmt = select(GullyParticipant).where(
            GullyParticipant.gully_id == gully_id,
            GullyParticipant.user_id == user_id,
        )
        result = await self.db.execute(stmt)
        participant = result.scalars().first()

        if not participant:
            return False

        await self.db.delete(participant)
        await self.db.commit()
        return True
