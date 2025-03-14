"""
Factory classes for creating participant-related response objects.
"""

from typing import Dict, List, Any


class ParticipantResponseFactory:
    """Factory for creating participant response objects."""

    @staticmethod
    def create_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a participant response from data.

        Args:
            data: Participant data

        Returns:
            Participant response
        """
        return {
            "id": data.get("id"),
            "user_id": data.get("user_id"),
            "gully_id": data.get("gully_id"),
            "role": data.get("role"),
            "team_name": data.get("team_name"),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
        }

    @staticmethod
    def create_response_list(data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create a list of participant responses from data.

        Args:
            data_list: List of participant data

        Returns:
            List of participant responses
        """
        return [ParticipantResponseFactory.create_response(data) for data in data_list]
