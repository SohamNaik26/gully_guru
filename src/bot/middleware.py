"""
Middleware for the Telegram bot.
This includes handlers for events like new chat members.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes, Application
from typing import Callable, Any, Awaitable

from src.bot.api_client_instance import api_client
from src.bot.utils.group_management import setup_new_group, process_new_members

# Configure logging
logger = logging.getLogger(__name__)


async def gully_context_middleware(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    callback: Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[Any]],
) -> Any:
    """Middleware to handle gully context."""
    # Skip middleware for certain commands
    if update.message and update.message.text:
        skip_commands = [
            "/start",
            "/create_gully",
            "/join_gully",
            "/switch_gully",
            "/my_gullies",
        ]
        if any(update.message.text.startswith(cmd) for cmd in skip_commands):
            return await callback(update, context)

    # Get user
    user = update.effective_user
    if not user:
        return await callback(update, context)

    # Get user from database
    db_user = await api_client.get_user(user.id)
    if not db_user:
        return await callback(update, context)

    # Handle group context
    if update.effective_chat and update.effective_chat.type in ["group", "supergroup"]:
        # Get gully for this group
        group_gully = await api_client.get_gully_by_group(update.effective_chat.id)

        if group_gully:
            # Store group gully in context
            context.chat_data["gully_id"] = group_gully.get("id")

            # If user has no active gully, set this as active
            if not db_user.get("active_gully_id"):
                await api_client.set_active_gully(
                    db_user.get("id"), group_gully.get("id")
                )

    # Store active gully in context
    active_gully_id = db_user.get("active_gully_id")
    if active_gully_id:
        context.user_data["active_gully_id"] = active_gully_id

    return await callback(update, context)


async def new_chat_members_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle new members added to a chat.
    Sends a welcome message with instructions to start a private chat with the bot.
    Also automatically adds the group owner as an admin when the bot is added to a group.
    """
    bot = context.bot
    new_members = update.message.new_chat_members

    # Check if the bot itself was added to the group
    bot_added = any(member.id == bot.id for member in new_members)

    # If the bot was just added to the group, set up the group
    if bot_added:
        await setup_new_group(update, context)

    # Process new members (excluding the bot)
    await process_new_members(update, context)


async def check_user_in_gully(user_id: int, gully_id: int) -> bool:
    """
    Check if a user is a member of a specific gully.
    Returns True if the user is a member, False otherwise.

    This is a thin wrapper around the API client method for backward compatibility.
    """
    try:
        return await api_client.is_user_in_gully(user_id, gully_id)
    except Exception as e:
        logger.error(f"Error checking if user {user_id} is in gully {gully_id}: {e}")
        return False


async def refresh_command_scopes(application: Application) -> None:
    """
    Refresh command scopes for all chats.
    This is a thin wrapper around the command_scopes module for backward compatibility.
    """
    from src.bot.command_scopes import refresh_command_scopes as refresh_scopes

    await refresh_scopes(application)
