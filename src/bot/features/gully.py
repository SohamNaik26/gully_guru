"""
Gully management feature module for GullyGuru bot.
Handles automatic user onboarding when they join a group.
"""

import logging
from typing import Dict, Any, Optional

from telegram import Update, Bot
from telegram.ext import ContextTypes
from telegram.constants import ChatType

from src.bot import api_client, initialize_api_client

# Configure logging
logger = logging.getLogger(__name__)


async def create_gully_for_group(
    bot: Bot, group_id: int, group_name: str
) -> Optional[Dict[str, Any]]:
    """
    Create a new gully for a Telegram group.

    Args:
        bot: The Telegram bot instance
        group_id: The Telegram group ID
        group_name: The name of the Telegram group

    Returns:
        The created gully data or None if creation failed
    """
    logger.info(f"Creating gully for group: {group_name} (ID: {group_id})")

    try:
        # Ensure API client is initialized
        await initialize_api_client()

        # Check if gully already exists for this group
        existing_gully = await api_client.gullies.get_gully_by_group(group_id)

        if existing_gully:
            logger.info(f"Gully already exists for group {group_name} (ID: {group_id})")
            return existing_gully

        # Create new gully
        new_gully = await api_client.gullies.create_gully(
            name=group_name, telegram_group_id=group_id
        )

        if new_gully:
            logger.info(
                f"Successfully created gully for group {group_name}: {new_gully.get('id')}"
            )

            # Send welcome message to the group
            await bot.send_message(
                chat_id=group_id,
                text=f"🏏 *Welcome to GullyGuru!* 🏏\n\n"
                f"I've created a new gully for this group: *{group_name}*\n\n"
                f"Group admins have been automatically added as gully admins.\n\n"
                f"Use /auction_status to check the current auction status.",
                parse_mode="Markdown",
            )

            return new_gully
        else:
            logger.error(f"Failed to create gully for group {group_name}")
            return None

    except Exception as e:
        logger.error(f"Error creating gully for group {group_name}: {e}")
        return None


# TODO: create a new function to to add users from user table to gullyparticipant, add owner of telegram group as admins. add by default others as members.
