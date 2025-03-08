"""
Utility functions for group management.
Centralizes group-related logic to avoid code duplication.
"""

import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from src.bot.api_client_instance import api_client
from src.bot.utils.user_management import (
    ensure_user_exists,
    ensure_user_in_gully,
    assign_admin_role,
)

logger = logging.getLogger(__name__)


async def get_active_group_chats() -> list:
    """
    Get a list of active group chat IDs where the bot is a member.
    Fetches this information from the database.

    Returns:
        list: List of chat IDs
    """
    try:
        # Get all active gullies from the database
        gullies = await api_client.get_all_gullies()

        # Extract chat IDs from gullies
        chat_ids = [
            gully.get("telegram_group_id")
            for gully in gullies
            if gully.get("telegram_group_id")
        ]

        logger.info(f"Found {len(chat_ids)} active group chats")
        return chat_ids
    except Exception as e:
        logger.error(f"Error fetching active group chats: {e}")
        return []


async def setup_new_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Set up a new group when the bot is added.
    Automatically adds the group owner as an admin.

    Args:
        update: The update object
        context: The context object
    """
    chat = update.effective_chat
    bot = context.bot

    try:
        # Get the group administrators
        chat_admins = await bot.get_chat_administrators(chat.id)

        # Find the group owner (creator)
        group_owner = next(
            (admin for admin in chat_admins if admin.status == "creator"), None
        )

        if not group_owner:
            logger.warning(f"Could not find owner for chat {chat.id}")
            return

        logger.info(f"Group owner found: {group_owner.user.id} for chat {chat.id}")

        # Check if a gully exists for this group
        gully = await api_client.get_gully_by_chat_id(chat.id)

        if not gully:
            # No gully exists yet, send a message to prompt creation
            await update.message.reply_text(
                "Welcome to GullyGuru! 🏏\n\n"
                "To get started, please create a gully for this group by using the /create_gully command.\n\n"
                "Only group administrators can create gullies."
            )
            return

        # Ensure owner exists in database
        owner_user = await ensure_user_exists(group_owner.user)
        if not owner_user:
            await update.message.reply_text(
                "There was an error setting up the group owner. Please try again later."
            )
            return

        # Gully exists, make sure the owner is an admin
        try:
            # First ensure the owner is registered in the gully
            await ensure_user_in_gully(group_owner.user.id, gully["id"])

            # Then make them an admin
            await assign_admin_role(group_owner.user.id, gully["id"])

            # Send a confirmation message
            await update.message.reply_text(
                f"Group owner @{group_owner.user.username or group_owner.user.first_name} "
                f"has been automatically assigned as an admin in this gully."
            )

            # Refresh command scopes to ensure admin commands are available
            from src.bot.command_scopes import refresh_command_scopes

            await refresh_command_scopes(context.application)
        except Exception as e:
            logger.error(f"Error assigning admin role to group owner: {e}")
    except Exception as e:
        logger.error(f"Error setting up new group: {e}")


async def process_new_members(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Process new members added to a group chat.
    Automatically registers them in the gully if it exists.

    Args:
        update: The update object
        context: The context object
    """
    chat = update.effective_chat
    new_members = update.message.new_chat_members
    bot = context.bot

    # Filter out the bot itself from new members for user processing
    new_users = [member for member in new_members if member.id != bot.id]

    # If no new users, we're done
    if not new_users:
        return

    # Check if this is a gully group
    gully = await api_client.get_gully_by_chat_id(chat.id)
    if not gully:
        logger.info(f"New members added to non-gully chat {chat.id}")
        return

    # Process each new user
    for user in new_users:
        try:
            # Ensure user exists in database
            db_user = await ensure_user_exists(user)
            if not db_user:
                continue

            # Add user to gully
            if await ensure_user_in_gully(user.id, gully["id"]):
                logger.info(f"User {user.id} auto-registered in gully {gully['id']}")

            # Create deep link for private chat
            deep_link = f"https://t.me/{bot.username}?start=from_group_{chat.id}"

            # Send welcome message with button
            await update.message.reply_text(
                f"Welcome @{user.username or user.first_name} 🏏\n\n"
                f"Please start a private conversation with me to complete your setup.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Start Private Chat", url=deep_link)]]
                ),
            )
        except Exception as e:
            logger.error(f"Error processing new user {user.id}: {e}")
