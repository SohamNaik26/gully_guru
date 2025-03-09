"""
Utility functions for the bot.
"""

import logging
from typing import Optional

from src.api.api_client_instance import api_client

logger = logging.getLogger(__name__)


async def get_active_gully_id(user_id: int, context=None) -> Optional[int]:
    """
    Get the active gully ID for a user.
    If no active gully is found, try to get it from context.user_data.

    Args:
        user_id: The user's database ID
        context: Optional context object from the handler

    Returns:
        The active gully ID or None if not found
    """
    # Try to get from database first
    participations = await api_client.gullies.get_user_gully_participations(user_id)
    active_participation = next(
        (p for p in participations if p.get("is_active", False)), None
    )

    if active_participation:
        return active_participation.get("gully_id")

    # If not found in database, try to get from context
    if context and hasattr(context, "user_data"):
        return context.user_data.get("active_gully_id")

    return None
