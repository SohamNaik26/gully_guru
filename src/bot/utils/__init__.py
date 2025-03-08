"""
Utility functions for the bot.
"""

from telegram.ext import ContextTypes
from typing import Optional


async def get_active_gully_id(
    user_id: int, context: ContextTypes.DEFAULT_TYPE
) -> Optional[int]:
    """
    Get the active gully ID for a user.

    First checks user_data for an active gully, then falls back to chat_data.

    Args:
        user_id: The user's Telegram ID
        context: The context object from the handler

    Returns:
        The active gully ID or None if not found
    """
    # First check user_data
    if "active_gully_id" in context.user_data:
        return context.user_data["active_gully_id"]

    # Then check chat_data if in a group
    if context.chat_data and "gully_id" in context.chat_data:
        return context.chat_data["gully_id"]

    return None
