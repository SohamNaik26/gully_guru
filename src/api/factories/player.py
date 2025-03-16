"""
Player factories for the GullyGuru API.
This module provides factory classes for creating response objects for player-related data.
"""

from typing import Dict, Any, List
from src.api.schemas.player import PlayerType


class PlayerResponseFactory:
    """Factory for creating player response objects."""

    @staticmethod
    def create_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a response object from player data.

        Args:
            data: Dictionary containing player data

        Returns:
            Response object
        """
        # Ensure player_type is a valid enum value
        player_type = data.get("player_type")

        # If player_type is a string, try to convert it to the enum value
        if isinstance(player_type, str):
            # Check if the string matches any of the enum values
            try:
                player_type = PlayerType(player_type)
            except ValueError:
                # If conversion fails, use a default value
                player_type = PlayerType.BAT

        return {
            "id": data.get("id"),
            "name": data.get("name"),
            "team": data.get("team"),
            "player_type": player_type,
            "base_price": data.get("base_price"),
            "sold_price": data.get("sold_price"),
            "season": data.get("season"),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
        }

    @staticmethod
    def create_response_list(data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create a list of response objects from a list of player data.

        Args:
            data_list: List of dictionaries containing player data

        Returns:
            List of response objects
        """
        return [PlayerResponseFactory.create_response(data) for data in data_list]
