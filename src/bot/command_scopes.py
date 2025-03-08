#!/usr/bin/env python
"""
Module to set up Telegram bot commands with proper scopes.
This can be imported by the bot or run directly as a script.
"""

import asyncio
import logging
import os
from dotenv import load_dotenv
from telegram import (
    BotCommand,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeAllGroupChats,
    BotCommandScopeDefault,
    BotCommandScopeChatAdministrators,
)
from telegram.ext import Application, ApplicationBuilder
from src.bot.api_client_instance import api_client
from src.bot.utils.group_management import get_active_group_chats
from src.bot.utils.user_management import (
    ensure_user_exists,
    ensure_user_in_gully,
    assign_admin_role,
)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables when run as a script
if __name__ == "__main__":
    load_dotenv()
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def setup_command_scopes(application: Application) -> None:
    """Set up command scopes for private and group chats."""
    # Define commands for private chats - based on user journey documentation
    private_commands = [
        # Core user commands
        BotCommand("start", "Register and start using the bot"),
        BotCommand("help", "Show available commands and how to use them"),
        BotCommand("game_guide", "Learn about the game and cricket terminology"),
        BotCommand("myteam", "View your current team composition"),
        BotCommand("submit_squad", "Submit initial squad of 18 players (Round 0)"),
        BotCommand("bid", "Place a bid during active auction"),
        BotCommand("auction_status", "Check auction status for all rounds"),
    ]

    # Define commands for group chats - based on user journey documentation
    group_commands = [
        # Auction and game commands
        BotCommand("auction_status", "Check auction status for all rounds"),
        BotCommand("start", "Register to play"),
        BotCommand("help", "Show available commands"),
    ]

    # Define admin-only commands - visible only to chat administrators
    admin_commands = [
        BotCommand("admin_panel", "Access auction-related admin functionality"),
        BotCommand("create_gully", "Create a new gully and link it to this group"),
        BotCommand(
            "check_members", "Check all group members and prompt unregistered users"
        ),
    ]

    # Set commands for private chats
    await application.bot.set_my_commands(
        private_commands, scope=BotCommandScopeAllPrivateChats()
    )
    logger.info("Private chat commands set successfully")

    # Set commands for group chats
    await application.bot.set_my_commands(
        group_commands, scope=BotCommandScopeAllGroupChats()
    )
    logger.info("Group chat commands set successfully")

    # Set admin commands for group chat administrators
    active_chats = await get_active_group_chats()
    if active_chats:
        for chat_id in active_chats:
            try:
                # Set admin commands for all administrators in this chat
                await application.bot.set_my_commands(
                    admin_commands,
                    scope=BotCommandScopeChatAdministrators(chat_id=chat_id),
                )
                logger.info(f"Admin commands set for chat {chat_id}")

                # Get the group owner and ensure they have admin commands
                try:
                    chat_admins = await application.bot.get_chat_administrators(chat_id)
                    group_owner = next(
                        (admin for admin in chat_admins if admin.status == "creator"),
                        None,
                    )

                    if group_owner:
                        # Get the gully for this chat
                        gully = await api_client.get_gully_by_chat_id(chat_id)
                        if gully:
                            # Ensure the owner is registered in the gully and as an admin
                            await ensure_user_exists(group_owner.user)
                            await ensure_user_in_gully(group_owner.user.id, gully["id"])
                            await assign_admin_role(group_owner.user.id, gully["id"])
                            logger.info(
                                f"Group owner {group_owner.user.id} assigned as admin in gully {gully['id']}"
                            )
                except Exception as e:
                    logger.error(f"Error setting up group owner as admin: {e}")
            except Exception as e:
                logger.error(f"Failed to set admin commands for chat {chat_id}: {e}")
    else:
        logger.info("No active group chats found, skipping admin command setup")

    # Set default commands (visible to all users in all contexts)
    default_commands = [
        BotCommand("start", "Register and start using the bot"),
        BotCommand("help", "Show available commands and how to use them"),
    ]
    await application.bot.set_my_commands(
        default_commands, scope=BotCommandScopeDefault()
    )
    logger.info("Default commands set successfully")


async def refresh_command_scopes(application: Application) -> None:
    """
    Refresh command scopes for all chats.
    This should be called when a new group is added or when admin status changes.
    """
    try:
        await setup_command_scopes(application)
        logger.info("Command scopes refreshed successfully")
    except Exception as e:
        logger.error(f"Error refreshing command scopes: {e}")


async def main():
    """Run the command setup script when executed directly."""
    print("Setting up command scopes...")

    # Initialize the bot
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Set up command scopes
    await setup_command_scopes(application)

    # Close the application
    await application.shutdown()
    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
