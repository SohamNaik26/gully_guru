"""
Mock data factory for API client tests.
"""

from typing import Dict, Any, Optional
import random
import string
from datetime import datetime


class MockDataFactory:
    """Factory for generating mock data for tests."""

    @staticmethod
    def random_string(length: int = 10) -> str:
        """Generate a random string of fixed length."""
        letters = string.ascii_lowercase
        return "".join(random.choice(letters) for _ in range(length))

    @staticmethod
    def random_int(min_val: int = 1, max_val: int = 1000000) -> int:
        """Generate a random integer within a range."""
        return random.randint(min_val, max_val)

    @staticmethod
    def user(
        id: Optional[int] = None,
        telegram_id: Optional[int] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate mock user data."""
        return {
            "id": id or MockDataFactory.random_int(),
            "telegram_id": telegram_id or MockDataFactory.random_int(),
            "first_name": first_name or f"User{MockDataFactory.random_string(5)}",
            "last_name": last_name or f"Last{MockDataFactory.random_string(5)}",
            "username": username or f"user_{MockDataFactory.random_string(8)}",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

    @staticmethod
    def gully(
        id: Optional[int] = None,
        name: Optional[str] = None,
        telegram_group_id: Optional[int] = None,
        status: str = "active",
    ) -> Dict[str, Any]:
        """Generate mock gully data."""
        return {
            "id": id or MockDataFactory.random_int(),
            "name": name or f"Gully{MockDataFactory.random_string(5)}",
            "telegram_group_id": telegram_group_id or MockDataFactory.random_int(),
            "status": status,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

    @staticmethod
    def gully_participant(
        id: Optional[int] = None,
        user_id: Optional[int] = None,
        gully_id: Optional[int] = None,
        role: str = "member",
        is_active: bool = True,
        registration_complete: bool = True,
    ) -> Dict[str, Any]:
        """Generate mock gully participant data."""
        return {
            "id": id or MockDataFactory.random_int(),
            "user_id": user_id or MockDataFactory.random_int(),
            "gully_id": gully_id or MockDataFactory.random_int(),
            "team_name": f"Team{MockDataFactory.random_string(5)}",
            "budget": 100.0,
            "points": 0,
            "role": role,
            "is_active": is_active,
            "registration_complete": registration_complete,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

    @staticmethod
    def permission(
        id: Optional[int] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate mock permission data."""
        return {
            "id": id or MockDataFactory.random_int(),
            "name": name or f"permission_{MockDataFactory.random_string(8)}",
            "description": description or f"Description for {name or 'permission'}",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
