"""
Factory classes for creating gully-related response objects.
"""

from typing import Dict, List, Any, Optional


class GullyResponseFactory:
    """Factory for creating gully response objects."""

    @staticmethod
    def create_response(data: Any) -> Dict[str, Any]:
        """
        Create a gully response from data.

        Args:
            data: Gully data

        Returns:
            Gully response
        """
        response = {
            "id": data.get("id"),
            "name": data.get("name"),
            "telegram_group_id": data.get("telegram_group_id"),
            "status": data.get("status"),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
        }

        return response

    @staticmethod
    def create_response_list(data_list: List[Any]) -> List[Dict[str, Any]]:
        """
        Create a list of gully responses from data.

        Args:
            data_list: List of gully data

        Returns:
            List of gully responses
        """
        return [GullyResponseFactory.create_response(data) for data in data_list]


class GullyParticipantResponseFactory:
    """Factory for creating gully participant response objects."""

    @staticmethod
    def create_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a gully participant response from data.

        Args:
            data: Gully participant data

        Returns:
            Gully participant response
        """
        return {
            "id": data.get("id"),
            "gully_id": data.get("gully_id"),
            "user_id": data.get("user_id"),
            "is_admin": data.get("is_admin"),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
            "username": data.get("username"),
            "full_name": data.get("full_name"),
            "telegram_id": data.get("telegram_id"),
        }

    @staticmethod
    def create_response_list(data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create a list of gully participant responses from data.

        Args:
            data_list: List of gully participant data

        Returns:
            List of gully participant responses
        """
        return [
            GullyParticipantResponseFactory.create_response(data) for data in data_list
        ]


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
            "gully_status": data.get("gully_status"),
            "total_participants": data.get("total_participants", 0),
            "submitted_participants": data.get("submitted_participants", 0),
            "all_submitted": data.get("all_submitted", False),
            "submitted_details": data.get("submitted_details", []),
            "not_submitted_details": data.get("not_submitted_details", []),
        }
