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
    BotCommandScopeDefault,
    BotCommandScopeAllGroupChats,
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
    """Set up command scopes for private chats."""
    # Define commands for private chats
    private_commands = [
        # Core user commands
        BotCommand("start", "Start the bot and register your team"),
        BotCommand("gullies", "View and select your gullies"),
        BotCommand("squad", "Manage your squad"),
    ]

    group_commands = [
        BotCommand("hello", "Hello!!"),
    ]
    # First, delete all commands for all scopes to ensure a clean slate
    await application.bot.delete_my_commands(scope=BotCommandScopeDefault())
    await application.bot.delete_my_commands(scope=BotCommandScopeAllPrivateChats())
    await application.bot.delete_my_commands(scope=BotCommandScopeAllGroupChats())
    logger.info("All existing command scopes cleared")

    # Set commands for private chats only
    await application.bot.set_my_commands(
        private_commands, scope=BotCommandScopeAllPrivateChats()
    )
    logger.info("Private chat commands set successfully")

    # Explicitly set empty commands for group chats
    await application.bot.set_my_commands(
        group_commands, scope=BotCommandScopeAllGroupChats()
    )
    logger.info("Group chat commands explicitly set")


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


if __name__ == "__main__":
    asyncio.run(main())
