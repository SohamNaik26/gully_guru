"""
Player factories for the GullyGuru API.
This module provides factory classes for creating response objects for player-related data.
"""

from typing import Dict, Any, List


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
        return {
            "id": data.get("id"),
            "name": data.get("name"),
            "team": data.get("team"),
            "player_type": data.get("player_type"),
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
