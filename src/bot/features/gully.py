"""
Gully management feature module for GullyGuru bot.
Handles automatic user onboarding when they join a group.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from src.bot.sync_manager import add_user_to_gully, create_or_get_gully

# Configure logging
logger = logging.getLogger(__name__)


async def new_chat_members_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle new members joining a chat.
    Automatically adds them to the gully if one exists, or creates a new gully.
    """
    chat = update.effective_chat
    new_members = update.message.new_chat_members

    # Skip if not a group chat
    if chat.type not in ["group", "supergroup"]:
        logger.debug(f"Skipping new members event for non-group chat: {chat.id}")
        return

    logger.info(
        f"Processing {len(new_members)} new members in group: {chat.title} (ID: {chat.id})"
    )

    # Get or create the gully for this group using the improved function
    gully = await create_or_get_gully(chat)
    if not gully:
        logger.error(f"Failed to create or get gully for group {chat.id}")
        return

    # Check if any of the new members are admins
    try:
        admins = await context.bot.get_chat_administrators(chat.id)
        admin_ids = {admin.user.id for admin in admins}
        logger.debug(f"Found {len(admin_ids)} admins in group {chat.id}")
    except Exception as e:
        logger.error(f"Error getting chat administrators: {e}")
        admin_ids = set()

    # Process each new member
    added_count = 0
    for member in new_members:
        # Skip bots
        if member.is_bot:
            logger.debug(f"Skipping bot user {member.id}")
            continue

        # Check if user is an admin
        is_admin = member.id in admin_ids
        role = "admin" if is_admin else "member"

        # Add user to gully using the improved sync manager function
        success = await add_user_to_gully(member, gully["id"], is_admin)
        if success:
            added_count += 1
            logger.info(
                f"Added new user {member.first_name} (ID: {member.id}) as {role} to gully {gully['id']}"
            )

    # Send welcome message if users were added
    if added_count > 0:
        welcome_message = (
            f"Welcome to {chat.title}! 👋\n\n"
            f"You've been automatically added to this gully. "
            f"Use /my_team to manage your team and participate in the fantasy league."
        )
        try:
            await context.bot.send_message(chat_id=chat.id, text=welcome_message)
        except Exception as e:
            logger.error(f"Error sending welcome message: {e}")
