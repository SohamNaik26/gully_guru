"""
Gully service for the GullyGuru API.
This module provides methods for interacting with gully-related database operations.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func

from src.api.services.base import BaseService
from src.db.models.models import (
    Gully,
    GullyParticipant,
    User,
)

logger = logging.getLogger(__name__)


class GullyService(BaseService):
    """Service for gully-related operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize the gully service.

        Args:
            db: Database session
        """
        super().__init__(None, None)
        self.db = db

    async def get_gullies(
        self,
        filters: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Tuple[List[Gully], int]:
        """
        Get gullies with optional filtering.

        Args:
            filters: Optional dictionary of field names and values to filter by
            user_id: Optional filter by user ID
            limit: Maximum number of gullies to return
            offset: Number of gullies to skip

        Returns:
            Tuple of (list of gullies, total count)
        """
        # Start with a base query
        query = select(Gully)

        # Apply filters if provided
        if filters:
            for field, value in filters.items():
                if hasattr(Gully, field) and value is not None:
                    query = query.where(getattr(Gully, field) == value)

        # Apply user_id filter if provided
        if user_id is not None:
            # Join with GullyParticipant to filter by user_id
            query = (
                query.join(GullyParticipant, Gully.id == GullyParticipant.gully_id)
                .where(GullyParticipant.user_id == user_id)
                .distinct()
            )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        # Apply pagination
        query = query.offset(offset).limit(limit)

        # Execute query
        result = await self.db.execute(query)
        gullies = result.scalars().all()

        return list(gullies), total

    async def get_gully(self, gully_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a gully by ID.

        Args:
            gully_id: The ID of the gully

        Returns:
            Gully data or None if not found
        """
        gully = await self.db.get(Gully, gully_id)
        if not gully:
            return None

        return {
            "id": gully.id,
            "name": gully.name,
            "status": gully.status,
            "telegram_group_id": gully.telegram_group_id,
            "created_at": gully.created_at,
            "updated_at": gully.updated_at,
        }

    async def get_gully_by_group(
        self, telegram_group_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get a gully by Telegram group ID.

        Args:
            telegram_group_id: The Telegram group ID

        Returns:
            Gully data or None if not found
        """
        stmt = select(Gully).where(Gully.telegram_group_id == telegram_group_id)
        result = await self.db.execute(stmt)
        gully = result.scalars().first()

        if not gully:
            return None

        return {
            "id": gully.id,
            "name": gully.name,
            "status": gully.status,
            "telegram_group_id": gully.telegram_group_id,
            "created_at": gully.created_at,
            "updated_at": gully.updated_at,
        }

    async def get_gully_by_telegram_id(
        self, telegram_group_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get a gully by Telegram group ID (alias for get_gully_by_group).

        Args:
            telegram_group_id: The Telegram group ID

        Returns:
            Gully data or None if not found
        """
        return await self.get_gully_by_group(telegram_group_id)

    async def create_gully(self, **gully_data) -> Dict[str, Any]:
        """
        Create a new gully.

        Args:
            **gully_data: Gully data to create

        Returns:
            Created gully data
        """
        # Check if a gully with the same telegram_group_id already exists
        if "telegram_group_id" in gully_data and gully_data["telegram_group_id"]:
            existing_gully = await self.get_gully_by_group(
                gully_data["telegram_group_id"]
            )
            if existing_gully:
                logger.info(
                    f"Gully with telegram_group_id {gully_data['telegram_group_id']} already exists, "
                    "returning existing gully"
                )
                return existing_gully

        gully = Gully(**gully_data)
        self.db.add(gully)
        await self.db.commit()
        await self.db.refresh(gully)

        return {
            "id": gully.id,
            "name": gully.name,
            "status": gully.status,
            "telegram_group_id": gully.telegram_group_id,
            "created_at": gully.created_at,
            "updated_at": gully.updated_at,
        }

    async def update_gully(
        self, gully_id: int, gully_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update a gully.

        Args:
            gully_id: The ID of the gully to update
            gully_data: Gully data to update

        Returns:
            Updated gully data or None if not found
        """
        gully = await self.db.get(Gully, gully_id)
        if not gully:
            return None

        for key, value in gully_data.items():
            setattr(gully, key, value)

        await self.db.commit()
        await self.db.refresh(gully)

        return {
            "id": gully.id,
            "name": gully.name,
            "status": gully.status,
            "telegram_group_id": gully.telegram_group_id,
            "created_at": gully.created_at,
            "updated_at": gully.updated_at,
        }

    async def update_gully_status(self, gully_id: int, status: str) -> Dict[str, Any]:
        """
        Update a gully's status.

        Args:
            gully_id: The ID of the gully to update
            status: New status

        Returns:
            Dictionary with success status and message
        """
        gully = await self.db.get(Gully, gully_id)
        if not gully:
            return {"success": False, "message": f"Gully with ID {gully_id} not found"}

        # Validate status
        valid_statuses = ["draft", "active", "completed", "cancelled"]
        if status not in valid_statuses:
            return {
                "success": False,
                "message": f"Invalid status: {status}. Must be one of {valid_statuses}",
            }

        gully.status = status
        await self.db.commit()
        await self.db.refresh(gully)

        return {"success": True, "message": f"Gully status updated to {status}"}

    async def delete_gully(self, gully_id: int) -> bool:
        """
        Delete a gully.

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

    async def get_user_gullies(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all gullies a user participates in.

        Args:
            user_id: The ID of the user

        Returns:
            List of gullies
        """
        stmt = (
            select(Gully)
            .join(
                GullyParticipant,
                GullyParticipant.gully_id == Gully.id,
            )
            .where(GullyParticipant.user_id == user_id)
        )

        result = await self.db.execute(stmt)
        gullies = result.scalars().all()

        # Convert to dictionaries
        gully_dicts = []
        for gully in gullies:
            gully_dict = {
                "id": gully.id,
                "name": gully.name,
                "status": gully.status,
                "telegram_group_id": gully.telegram_group_id,
                "created_at": gully.created_at,
                "updated_at": gully.updated_at,
            }
            gully_dicts.append(gully_dict)

        return gully_dicts

    async def get_gullies_by_telegram_ids(
        self, telegram_group_ids: List[int]
    ) -> List[Dict[str, Any]]:
        """
        Get gullies by a list of Telegram group IDs.

        This method is useful for bot operations where we need to find
        multiple gullies by their Telegram group IDs.

        Args:
            telegram_group_ids: List of Telegram group IDs

        Returns:
            List of gully data matching the Telegram group IDs
        """
        stmt = select(Gully).where(Gully.telegram_group_id.in_(telegram_group_ids))
        result = await self.db.execute(stmt)
        gullies = result.scalars().all()

        # Convert to dictionaries
        gully_dicts = []
        for gully in gullies:
            gully_dict = {
                "id": gully.id,
                "name": gully.name,
                "status": gully.status,
                "telegram_group_id": gully.telegram_group_id,
                "created_at": gully.created_at,
                "updated_at": gully.updated_at,
            }
            gully_dicts.append(gully_dict)

        return gully_dicts
