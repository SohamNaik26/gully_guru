"""
Features module for GullyGuru bot.
Contains feature modules and handler registration.
"""

import logging
from telegram.ext import MessageHandler, filters, Application
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.bot.features.onboarding import register_onboarding_handlers
from src.bot.features.squad import register_squad_handlers
from src.bot.api_client.onboarding import handle_complete_onboarding

# Configure logging
logger = logging.getLogger(__name__)


async def new_chat_members_handler(update, context):
    """
    Handle new chat members, including the bot itself.

    When the bot is added to a group:
    1. Create a new Gully for the group
    2. Assign the user who added the bot as the Gully admin
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
            f"Bot was added by user: {user_who_added.username or user_who_added.first_name} (ID: {user_who_added.id})"
        )

        # Generate deep link for registration
        deep_link = f"https://t.me/{context.bot.username}?start=group_{group_id}"

        # Send welcome message
        await update.message.reply_text(
            f"Hello everyone! I'm GullyGuru, your cricket fantasy game bot!\n\n"
            f"This group is now set up as a Gully.\n\n"
            f"@{user_who_added.username or user_who_added.first_name} is the admin.\n\n"
            f"To participate in the game, please click the button below:",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Register to Play", url=deep_link)]]
            ),
        )

        # Handle the complete onboarding process
        onboarding_result = await handle_complete_onboarding(
            bot_id=context.bot.id,
            group_id=group_id,
            group_name=group_name,
            admin_telegram_id=user_who_added.id,
            admin_first_name=user_who_added.first_name,
            admin_username=user_who_added.username,
            admin_last_name=user_who_added.last_name,
        )

        if onboarding_result["success"]:
            logger.info(f"Successfully completed onboarding for group {group_name}")
        else:
            logger.error(f"Failed to complete onboarding for group {group_name}")
    else:
        # Regular user joined the group
        logger.info(f"New members joined group {chat.title} (ID: {chat.id})")


def register_handlers(application):
    """Register onboarding-related handlers."""
    logger.info("Registering onboarding feature handlers...")

    # New chat members handler for onboarding
    application.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_chat_members_handler)
    )

    # Onboarding feature handlers (but not the NEW_CHAT_MEMBERS handler again)
    register_onboarding_handlers(application, skip_new_chat_members=True)

    logger.info("Onboarding handlers registered successfully")


async def register_all_features(application):
    """Register all feature handlers."""
    # Register onboarding handlers
    register_onboarding_handlers(application, skip_new_chat_members=False)

    # Register squad handlers - properly await this
    await register_squad_handlers(application)

    logger.info("All feature handlers registered successfully")
