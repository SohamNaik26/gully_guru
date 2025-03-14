"""
Factory classes for creating fantasy-related response objects.
"""

from typing import Dict, Any, List


class DraftPlayerResponseFactory:
    """Factory for creating draft player response objects."""

    @staticmethod
    def create_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a draft player response from data.

        Args:
            data: Draft player data

        Returns:
            Draft player response
        """
        return {
            "id": data.get("id"),
            "user_id": data.get("user_id"),
            "player_id": data.get("player_id"),
            "gully_id": data.get("gully_id"),
            "status": data.get("status"),
            "player": data.get("player", {}),
        }

    @staticmethod
    def create_response_list(data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create a list of draft player responses from data.

        Args:
            data_list: List of draft player data

        Returns:
            List of draft player responses
        """
        return [DraftPlayerResponseFactory.create_response(data) for data in data_list]


class DraftSquadResponseFactory:
    """Factory for creating draft squad response objects."""

    @staticmethod
    def create_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a draft squad response from data.

        Args:
            data: Draft squad data

        Returns:
            Draft squad response
        """
        return {
            "user_id": data.get("user_id"),
            "gully_id": data.get("gully_id"),
            "players": [
                DraftPlayerResponseFactory.create_response(player)
                for player in data.get("players", [])
            ],
        }


class SubmissionStatusResponseFactory:
    """Factory for creating submission status response objects."""

    @staticmethod
    def create_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a submission status response from data.

        Args:
            data: Submission status data

        Returns:
            Submission status response
        """
        return {
            "gully_id": data.get("gully_id"),
            "total_participants": data.get("total_participants", 0),
            "submitted_count": data.get("submitted_count", 0),
            "is_complete": data.get("is_complete", False),
            "status": data.get("status", "pending"),
        }


class AuctionStartResponseFactory:
    """Factory for creating auction start response objects."""

    @staticmethod
    def create_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an auction start response from data.

        Args:
            data: Auction start data

        Returns:
            Auction start response
        """
        return {
            "gully_id": data.get("gully_id"),
            "status": data.get("status", "pending"),
            "contested_players_count": data.get("contested_players_count", 0),
            "uncontested_players_count": data.get("uncontested_players_count", 0),
        }


class ContestPlayerResponseFactory:
    """Factory for creating contest player response objects."""

    @staticmethod
    def create_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a contest player response from data.

        Args:
            data: Contest player data

        Returns:
            Contest player response
        """
        return {
            "player_id": data.get("player_id"),
            "player_name": data.get("player_name", ""),
            "team": data.get("team", ""),
            "role": data.get("role", ""),
            "participants": data.get("participants", []),
        }


class SquadResponseFactory:
    """Factory for creating squad response objects."""

    @staticmethod
    def create_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a squad response from data.

        Args:
            data: Squad data

        Returns:
            Squad response
        """
        return {"players": data.get("players", [])}
