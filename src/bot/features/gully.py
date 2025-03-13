"""
Gully management feature module for GullyGuru bot.
Handles automatic user onboarding when they join a group.
"""

import logging
from typing import Dict, Any, Optional

from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

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
            return new_gully
        else:
            logger.error(f"Failed to create gully for group {group_name}")
            return None

    except Exception as e:
        logger.error(f"Error creating gully for group {group_name}: {e}")
        return None


async def send_welcome_message(
    bot: Bot, chat_id: int, gully_id: int, admin_username: str
) -> None:
    """
    Send welcome message to the group with deep link for registration.

    Args:
        bot: The Telegram bot instance
        chat_id: The Telegram chat ID
        gully_id: The Gully ID
        admin_username: The username of the admin
    """
    try:
        # Create deep link with telegram_group_id
        deep_link = f"https://t.me/{bot.username}?start=group_{chat_id}"

        # Create inline keyboard with deep link
        keyboard = [[InlineKeyboardButton("Register to Play", url=deep_link)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Format admin username properly - ensure it doesn't have @ if provided by user
        admin_display = admin_username.lstrip("@") if admin_username else "Admin"

        # Send welcome message with simple text formatting
        welcome_text = "Hello everyone! This group is now set up as a Gully.\n"

        # Add admin info with proper formatting
        if admin_display != "Admin":
            welcome_text += f"@{admin_display} is the admin.\n"
        else:
            welcome_text += "Admin is the admin.\n"

        welcome_text += (
            "To participate in the game, please open a private chat with me:"
        )

        await bot.send_message(
            chat_id=chat_id,
            text=welcome_text,
            reply_markup=reply_markup,
        )
        logger.info(f"Welcome message sent to group {chat_id}")
    except Exception as e:
        logger.error(f"Error sending welcome message to group {chat_id}: {e}")


async def new_chat_members_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle new chat members, including the bot itself.

    When the bot is added to a group:
    1. Create a new Gully for the group
    2. Assign the user who added the bot as the Gully admin
    3. Send a welcome message with a deep link for registration
    """
    chat = update.effective_chat
    new_members = update.message.new_chat_members
    bot_user = context.bot.id

    # Check if the bot was added to the group
    if any(member.id == bot_user for member in new_members):
        logger.info(f"Bot was added to group: {chat.title} (ID: {chat.id})")

        # Bot was added to the group
        group_id = chat.id
        group_name = chat.title

        # Get the user who added the bot (message sender)
        user_who_added = update.effective_user
        logger.info(
            f"Bot was added by user: {user_who_added.username} (ID: {user_who_added.id})"
        )

        # Create gully for the group
        gully = await create_gully_for_group(context.bot, group_id, group_name)

        if gully:
            # Create or get user record
            db_user = await api_client.users.get_user(user_who_added.id)
            if not db_user:
                logger.info(
                    f"Creating new user for {user_who_added.username} (ID: {user_who_added.id})"
                )
                db_user = await api_client.users.create_user(
                    {
                        "telegram_id": user_who_added.id,
                        "username": user_who_added.username or "",
                        "full_name": f"{user_who_added.first_name} {user_who_added.last_name or ''}".strip(),
                    }
                )

            if db_user:
                # Add user as admin to the gully
                logger.info(
                    f"Adding user {db_user['id']} as admin to gully {gully['id']}"
                )
                await api_client.gullies.add_user_to_gully(
                    user_id=db_user["id"], gully_id=gully["id"], role="admin"
                )

                # Send welcome message with deep link
                await send_welcome_message(
                    context.bot,
                    chat.id,
                    gully["id"],
                    user_who_added.username or "Admin",
                )
            else:
                logger.error(
                    f"Failed to create or get user for {user_who_added.username}"
                )
        else:
            logger.error(f"Failed to create gully for group {group_name}")
    else:
        # Regular user joined the group
        logger.info(f"New members joined group {chat.title} (ID: {chat.id})")
