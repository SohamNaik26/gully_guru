"""
Player service for the GullyGuru API.
This module provides methods for interacting with player-related database operations.
"""

from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func

from src.api.services.base import BaseService
from src.db.models.models import Player


class PlayerService(BaseService):
    """Service for player-related operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize the player service.

        Args:
            db: Database session
        """
        super().__init__(None, None)
        self.db = db

    async def create_player(self, player_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new player.

        Args:
            player_data: Dictionary containing player data

        Returns:
            Dictionary with created player data
        """
        # Create new player
        player = Player(**player_data)
        self.db.add(player)
        await self.db.commit()
        await self.db.refresh(player)

        # Convert SQLModel to dict
        player_dict = {
            "id": player.id,
            "name": player.name,
            "team": player.team,
            "player_type": player.player_type,
            "base_price": player.base_price,
            "sold_price": player.sold_price,
            "season": player.season,
            "created_at": player.created_at,
            "updated_at": player.updated_at,
        }

        return player_dict

    async def get_player(self, player_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a player by ID.

        Args:
            player_id: ID of the player to retrieve

        Returns:
            Dictionary with player data or None if not found
        """
        player = await self.db.get(Player, player_id)
        if not player:
            return None

        # Convert SQLModel to dict
        player_dict = {
            "id": player.id,
            "name": player.name,
            "team": player.team,
            "player_type": player.player_type,
            "base_price": player.base_price,
            "sold_price": player.sold_price,
            "season": player.season,
            "created_at": player.created_at,
            "updated_at": player.updated_at,
        }

        return player_dict

    async def get_players(
        self, limit: int = 10, offset: int = 0, filters: Dict[str, Any] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get a list of players with optional filtering.

        Args:
            limit: Maximum number of players to return
            offset: Number of players to skip
            filters: Dictionary of field names and values to filter by

        Returns:
            Tuple of (list of player dictionaries, total count)
        """
        # Build query with filters
        query = select(Player)
        if filters:
            for field, value in filters.items():
                if field == "name" and value is not None:
                    # Use partial match for name
                    query = query.where(Player.name.ilike(f"%{value}%"))
                elif hasattr(Player, field) and value is not None:
                    query = query.where(getattr(Player, field) == value)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        query = query.offset(offset).limit(limit)

        # Execute query
        result = await self.db.execute(query)
        players = result.scalars().all()

        # Convert SQLModels to dicts
        player_dicts = []
        for player in players:
            player_dict = {
                "id": player.id,
                "name": player.name,
                "team": player.team,
                "player_type": player.player_type,
                "base_price": player.base_price,
                "sold_price": player.sold_price,
                "season": player.season,
                "created_at": player.created_at,
                "updated_at": player.updated_at,
            }
            player_dicts.append(player_dict)

        return player_dicts, total

    async def update_player(
        self, player_id: int, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update a player.

        Args:
            player_id: ID of the player to update
            update_data: Dictionary containing fields to update

        Returns:
            Dictionary with updated player data or None if not found
        """
        player = await self.db.get(Player, player_id)
        if not player:
            return None

        # Update player attributes
        for key, value in update_data.items():
            if hasattr(player, key):
                setattr(player, key, value)

        player.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(player)

        # Convert SQLModel to dict
        player_dict = {
            "id": player.id,
            "name": player.name,
            "team": player.team,
            "player_type": player.player_type,
            "base_price": player.base_price,
            "sold_price": player.sold_price,
            "season": player.season,
            "created_at": player.created_at,
            "updated_at": player.updated_at,
        }

        return player_dict

    async def delete_player(self, player_id: int) -> bool:
        """
        Delete a player.

        Args:
            player_id: ID of the player to delete

        Returns:
            True if player was deleted, False if not found
        """
        player = await self.db.get(Player, player_id)
        if not player:
            return False

        await self.db.delete(player)
        await self.db.commit()

        return True
