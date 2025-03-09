"""
Utility functions for gully management.
Centralizes gully creation and management logic to avoid code duplication.
"""

import logging
from datetime import datetime, timedelta
from telegram import Chat, User as TelegramUser
from telegram.ext import ContextTypes
from typing import List, Dict, Any, Optional

from src.bot.api_client_instance import api_client
from src.bot.utils.user_management import ensure_user_exists, ensure_user_in_gully

# Configure logging
logger = logging.getLogger(__name__)


async def setup_new_group(chat: Chat) -> Dict[str, Any]:
    """
    Set up a new group as a gully.

    Args:
        chat: The Telegram chat object

    Returns:
        dict: The created gully data or error information
    """
    try:
        # Check if a gully already exists for this group
        existing_gully = await api_client.get_gully_by_chat_id(chat.id)
        if existing_gully:
            logger.info(f"Gully already exists for group {chat.id}")
            return {
                "success": True,
                "gully": existing_gully,
                "message": "Gully already exists",
            }

        # Create a new gully
        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=180)).strftime("%Y-%m-%d")

        gully_name = chat.title or f"Gully_{chat.id}"
        gully = await api_client.create_gully(
            name=gully_name,
            telegram_group_id=chat.id,
            start_date=start_date,
            end_date=end_date,
        )

        if not gully:
            logger.error(f"Failed to create gully for group {chat.id}")
            return {"success": False, "error": "Failed to create gully"}

        logger.info(f"Created new gully {gully.get('id')} for group {chat.id}")
        return {
            "success": True,
            "gully": gully,
            "message": "Gully created successfully",
        }
    except Exception as e:
        logger.error(f"Error setting up new group: {e}")
        return {"success": False, "error": str(e)}


async def process_new_members(
    chat: Chat, new_members: List[TelegramUser], context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Process new members added to a group.

    Args:
        chat: The Telegram chat object
        new_members: List of new Telegram users
        context: The bot context
    """
    try:
        # Get the gully for this group
        gully = await api_client.get_gully_by_chat_id(chat.id)
        if not gully:
            # No gully exists, create one
            result = await setup_new_group(chat)
            if not result.get("success"):
                logger.error(f"Failed to set up group {chat.id}: {result.get('error')}")
                return
            gully = result.get("gully")

        gully_id = gully.get("id")

        # Process each new member
        for member in new_members:
            if member.is_bot:
                # Skip bots
                continue

            # Ensure user exists in database
            db_user = await ensure_user_exists(member)
            if not db_user:
                logger.error(f"Failed to create user {member.id} in database")
                continue

            # Add user to gully
            participant = await ensure_user_in_gully(db_user["id"], gully_id)
            if not participant:
                logger.error(f"Failed to add user {member.id} to gully {gully_id}")
                continue

            logger.info(f"Added user {member.id} to gully {gully_id}")

            # Send welcome message
            try:
                await context.bot.send_message(
                    chat.id,
                    f"Welcome {member.first_name}! You've been added to the "
                    f"{gully.get('name')} fantasy cricket league.",
                )
            except Exception as e:
                logger.error(f"Error sending welcome message: {e}")

    except Exception as e:
        logger.error(f"Error processing new members: {e}")


async def get_gully_by_chat(chat_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a gully by chat ID.

    Args:
        chat_id: The Telegram chat ID

    Returns:
        Optional[Dict[str, Any]]: The gully data or None if not found
    """
    try:
        return await api_client.get_gully_by_chat_id(chat_id)
    except Exception as e:
        logger.error(f"Error getting gully by chat ID {chat_id}: {e}")
        return None


async def get_active_group_chats() -> List[Dict[str, Any]]:
    """
    Get all active group chats (gullies).

    Returns:
        List[Dict[str, Any]]: List of active gullies with their chat IDs
    """
    try:
        # Get all gullies
        gullies = await api_client.get_all_gullies()

        # Filter to active gullies with valid telegram_group_id
        active_groups = []
        for gully in gullies:
            if gully.get("status") == "active" and gully.get("telegram_group_id"):
                active_groups.append(
                    {
                        "id": gully.get("id"),
                        "name": gully.get("name"),
                        "telegram_group_id": gully.get("telegram_group_id"),
                    }
                )

        return active_groups
    except Exception as e:
        logger.error(f"Error getting active group chats: {e}")
        return []
