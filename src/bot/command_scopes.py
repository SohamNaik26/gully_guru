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
        BotCommand("squad", "Manage your Initial Squad Selection"),
        # Auction commands for private chats
        BotCommand("release_players", "Select players to release during auction"),
        BotCommand("my_team", "View your current team"),
        BotCommand("reset_auction", "Reset auction for the active gully"),
    ]

    # Visible group commands
    group_commands = [
        BotCommand("hello", "Hello!!"),
        BotCommand("start_auction", "Start the auction process for the gully"),
        BotCommand("pause_auction", "Temporarily pause the auction"),
    ]

    try:
        # Clear commands with explicit language code
        await application.bot.delete_my_commands(
            scope=BotCommandScopeDefault(),
            language_code=None,  # This ensures we clear commands for all languages
        )
        await application.bot.delete_my_commands(
            scope=BotCommandScopeAllPrivateChats(), language_code=None
        )
        await application.bot.delete_my_commands(
            scope=BotCommandScopeAllGroupChats(), language_code=None
        )

        # Add a verification step
        default_commands = await application.bot.get_my_commands(
            scope=BotCommandScopeDefault()
        )
        private_chat_commands = await application.bot.get_my_commands(
            scope=BotCommandScopeAllPrivateChats()
        )
        group_chat_commands = await application.bot.get_my_commands(
            scope=BotCommandScopeAllGroupChats()
        )

        logger.info(
            f"After deletion - Default commands: {len(default_commands)}, "
            f"Private chat commands: {len(private_chat_commands)}, "
            f"Group chat commands: {len(group_chat_commands)}"
        )

        # Now set the new commands
        await application.bot.set_my_commands(
            private_commands, scope=BotCommandScopeAllPrivateChats()
        )

        await application.bot.set_my_commands(
            group_commands, scope=BotCommandScopeAllGroupChats()
        )

        # Verify the commands were set correctly
        updated_private_commands = await application.bot.get_my_commands(
            scope=BotCommandScopeAllPrivateChats()
        )
        updated_group_commands = await application.bot.get_my_commands(
            scope=BotCommandScopeAllGroupChats()
        )

        logger.info(
            f"After setting - Private commands: {len(updated_private_commands)}, "
            f"Group commands: {len(updated_group_commands)}"
        )

        logger.info("Command scopes updated successfully")

    except Exception as e:
        logger.error(f"Error updating command scopes: {e}")
        logger.exception("Command scope update exception:")


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
