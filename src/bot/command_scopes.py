#!/usr/bin/env python
"""
Command scopes module for GullyGuru bot.
Handles setting up command scopes for different chat types.
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
)
from telegram.ext import Application, ApplicationBuilder

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
    # Define commands for private chats
    private_commands = [
        # Core user commands
        BotCommand("my_team", "View your current team composition"),
        BotCommand("submit_squad", "Create or update your team"),
        # Admin commands
        BotCommand("admin_panel", "Access admin controls for your gullies"),
    ]

    # Define commands for gully chats
    gully_commands = [
        # Gully commands
        BotCommand("auction_status", "Check current auction status"),
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

    # Set default commands (visible to all users in all contexts)
    default_commands = []  # No default commands

    if default_commands:  # Only set if there are any default commands
        await application.bot.set_my_commands(
            default_commands, scope=BotCommandScopeDefault()
        )
        logger.info("Default commands set successfully")


async def refresh_command_scopes(application: Application) -> None:
    """Refresh command scopes for the bot."""
    logger.info("Refreshing command scopes...")
    await setup_command_scopes(application)
    logger.info("Command scopes refreshed successfully")


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


# if __name__ == "__main__":
#     asyncio.run(main())
