"""
Middleware for the Telegram bot.
This includes handlers for events like new chat members.
"""

import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, Application
from typing import Callable, Any, Awaitable

from src.api.api_client_instance import api_client
from src.bot.services import user_service, gully_service

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
            "/join_gully",
            "/help",
            "/switch_gully",
            "/start",
            "/game_guide",
        ]
        if any(update.message.text.startswith(cmd) for cmd in skip_commands):
            return await callback(update, context)

    # Get the user
    user = update.effective_user
    if not user:
        return await callback(update, context)

    # Get the user from the database
    db_user = await api_client.users.get_user(user.id)
    if not db_user:
        # User not found, let the handler deal with it
        return await callback(update, context)

    # If in a group chat, check if it's a gully
    if update.effective_chat and update.effective_chat.type in ["group", "supergroup"]:
        gully = await api_client.gullies.get_gully_by_group(update.effective_chat.id)
        if gully:
            # Set the active gully for the user
            await api_client.gullies.set_active_gully(
                db_user.get("id"), gully.get("id")
            )

    # Continue with the handler
    return await callback(update, context)


async def new_chat_members_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle new chat members.
    This is triggered when a user joins a group or when the bot is added to a group.
    """
    # Get the new members
    new_members = update.message.new_chat_members
    if not new_members:
        return

    # Check if the bot is among the new members
    bot = context.bot
    bot_added = any(member.id == bot.id for member in new_members)

    # If the bot was added to a new group
    if bot_added:
        await setup_new_gully(update, context)
        return

    # Process new members (non-bot)
    chat = update.effective_chat

    # Get the gully for this group
    gully = await gully_service.create_gully(
        name=chat.title or f"Gully {chat.id}", telegram_group_id=chat.id
    )

    # Process each new member
    for member in new_members:
        if member.is_bot:
            # Skip bots
            continue

        # Ensure user exists in database
        db_user = await user_service.ensure_user_exists(member)
        if not db_user:
            logger.error(f"Failed to create user {member.id} in database")
            continue

        # Check if user is already in the gully
        participant = await api_client.gullies.get_user_gully_participation(
            db_user["id"], gully["id"]
        )

        if participant:
            # User is already in the gully, just welcome them
            await context.bot.send_message(
                chat.id,
                f"Welcome back {member.first_name}! You're already registered in the "
                f"{gully.get('name')} fantasy cricket league.",
            )
        else:
            # Send welcome message with join button
            bot_username = context.bot.username
            deep_link = f"https://t.me/{bot_username}?start=from_gully_{gully['id']}"

            await context.bot.send_message(
                chat.id,
                f"Welcome {member.first_name}! 🏏\n\n"
                f"Join our fantasy cricket league *{gully.get('name')}* to start playing!",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Join Gully", url=deep_link)]]
                ),
            )


async def check_user_in_gully(user_id: int, gully_id: int) -> bool:
    """
    Check if a user is a member of a gully.

    Args:
        user_id: The Telegram ID of the user
        gully_id: The ID of the gully

    Returns:
        True if the user is a member of the gully, False otherwise
    """
    return await api_client.gullies.get_user_gully_participations(user_id)


async def refresh_command_scopes(application: Application) -> None:
    """
    Refresh command scopes for the bot.
    This ensures that commands are only available in the appropriate contexts.
    """
    from src.bot.command_scopes import refresh_command_scopes as refresh

    await refresh(application)


async def setup_new_gully(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Set up a new gully when the bot is added to a group.

    Args:
        update: The update object
        context: The context object
    """
    chat = update.effective_chat

    # Create a new gully for this group
    gully = await gully_service.create_gully(
        name=chat.title or f"Gully {chat.id}", telegram_group_id=chat.id
    )

    if gully:
        logger.info(
            f"Created new gully for group {chat.id}: {gully['name']} (ID: {gully['id']})"
        )

        # Set the group owner as admin
        owner_result = await gully_service.set_group_owner_as_admin(
            chat.id, gully["id"], context.bot
        )

        if owner_result["success"]:
            logger.info(f"Set group owner as admin for gully {gully['id']}")

            # Send welcome message
            await context.bot.send_message(
                chat_id=chat.id,
                text=(
                    f"👋 Hello! I'm GullyGuru, your fantasy cricket assistant.\n\n"
                    f"I've created a new gully called *{gully['name']}* for this group.\n\n"
                    f"The group owner has been set as the gully admin.\n\n"
                    f"To join this gully, members can use the /join_gully command."
                ),
                parse_mode="Markdown",
            )
        else:
            logger.error(f"Failed to set group owner as admin: {owner_result['error']}")
    else:
        logger.error(f"Failed to create gully for group {chat.id}")

        # Send error message
        await context.bot.send_message(
            chat_id=chat.id,
            text="❌ Sorry, I couldn't set up a gully for this group. Please try again later.",
        )
