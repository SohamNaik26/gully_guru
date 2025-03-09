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
from src.bot.services import user_service, gully_service, admin_service

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
    """Set up command scopes for private and gully chats."""
    # Define commands for private chats - based on user journey documentation
    private_commands = [
        # Core user commands
        BotCommand("help", "Show available commands and how to use them"),
        BotCommand("game_guide", "Learn about the game and cricket terminology"),
        BotCommand("myteam", "View your current team composition"),
        BotCommand("submit_squad", "Submit initial squad of 18 players (Round 0)"),
        BotCommand("bid", "Place a bid during active auction"),
        BotCommand("auction_status", "Check auction status for all rounds"),
    ]

    # Define commands for gully chats - based on user journey documentation
    gully_commands = [
        # Auction and game commands
        BotCommand("auction_status", "Check auction status for all rounds"),
        BotCommand("help", "Show available commands"),
        BotCommand("join_gully", "Join this gully and start playing"),
    ]

    # Define admin-only commands - visible only to chat administrators
    admin_commands = [
        BotCommand("admin_panel", "Access admin functionality"),
        BotCommand("create_gully", "Create a new gully for this group"),
        BotCommand("add_member", "Add a user to this gully"),
        BotCommand("manage_admins", "View and manage gully admins"),
    ]

    # Set commands for private chats
    await application.bot.set_my_commands(
        private_commands, scope=BotCommandScopeAllPrivateChats()
    )
    logger.info("Private chat commands set successfully")

    # Set commands for gully chats
    await application.bot.set_my_commands(
        gully_commands, scope=BotCommandScopeAllGroupChats()
    )
    logger.info("Gully chat commands set successfully")

    # Set admin commands for gully chat administrators
    active_gullies = await gully_service.get_active_gullies()
    if active_gullies:
        for gully in active_gullies:
            try:
                chat_id = gully["telegram_group_id"]
                gully_id = gully["id"]

                # Set admin commands for all administrators in this chat
                await application.bot.set_my_commands(
                    admin_commands,
                    scope=BotCommandScopeChatAdministrators(chat_id=chat_id),
                )
                logger.info(f"Admin commands set for gully chat {chat_id}")

                # Get the gully owner and ensure they have admin commands
                try:
                    chat_admins = await application.bot.get_chat_administrators(chat_id)
                    gully_owner = next(
                        (admin for admin in chat_admins if admin.status == "creator"),
                        None,
                    )

                    if gully_owner:
                        # Ensure the owner is registered in the system
                        db_user = await user_service.ensure_user_exists(
                            gully_owner.user
                        )
                        if db_user:
                            # Ensure the owner is in the gully and set as admin
                            participant = await gully_service.add_user_to_gully(
                                db_user["id"], gully_id
                            )
                            if participant:
                                # Set the user as admin
                                result = await admin_service.assign_admin_role(
                                    db_user["id"], gully_id
                                )
                                if result:
                                    logger.info(
                                        f"Gully owner {gully_owner.user.id} assigned as admin "
                                        f"in gully {gully_id}"
                                    )
                                else:
                                    logger.error(
                                        f"Failed to assign admin role to gully owner "
                                        f"{gully_owner.user.id} in gully {gully_id}"
                                    )
                except Exception as e:
                    logger.error(f"Error setting up gully owner as admin: {e}")
            except Exception as e:
                logger.error(
                    f"Failed to set admin commands for gully chat {chat_id}: {e}"
                )
    else:
        logger.info("No active gully chats found, skipping admin command setup")

    # Set default commands (visible to all users in all contexts)
    default_commands = [
        BotCommand("join_gully", "Join a gully and start playing"),
        BotCommand("help", "Show available commands and how to use them"),
    ]
    await application.bot.set_my_commands(
        default_commands, scope=BotCommandScopeDefault()
    )
    logger.info("Default commands set successfully")


async def refresh_command_scopes(application: Application) -> None:
    """
    Refresh command scopes for all chats.
    This should be called after scanning groups to ensure admin commands are properly set.
    """
    try:
        # Set up command scopes
        await setup_command_scopes(application)
        logger.info("Command scopes refreshed successfully")
    except Exception as e:
        logger.error(f"Error refreshing command scopes: {e}")
        raise


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
