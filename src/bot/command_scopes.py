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
    """Set up command scopes for private and group chats."""
    # Define commands for private chats - based on user_management.md and auction_management.md
    private_commands = [
        # Core user commands
        BotCommand("start", "Register with the bot and set up your profile"),
        BotCommand("help", "Get help with bot commands and game concepts"),
        BotCommand("game_guide", "Learn about the game and cricket terminology"),
        BotCommand("profile", "View and edit your profile information"),
        # Gully management
        BotCommand("my_gullies", "View all gullies you are participating in"),
        BotCommand("switch_gully", "Switch your active gully context"),
        # Team and auction management
        BotCommand("myteam", "View your current team composition"),
        BotCommand("submit_squad", "Submit initial squad of 18 players (Round 0)"),
        BotCommand("bid", "Place a bid during active auction"),
        BotCommand("auction_status", "Check current auction status"),
        # Admin commands (only visible to admins)
        BotCommand("admin_panel", "Access admin functionality"),
        BotCommand("create_gully", "Create a new gully"),
        BotCommand("setup_wizard", "Launch or resume the gully setup wizard"),
        BotCommand("invite_link", "Generate a custom invite link for the group"),
        BotCommand("admin_roles", "Manage granular admin permissions"),
        BotCommand("bulk_add", "Facilitate adding multiple users at once"),
    ]

    # Define commands for group chats - based on user_management.md and auction_management.md
    group_commands = [
        # Core group commands
        BotCommand("help_group", "Get help with group-specific commands"),
        BotCommand("gully_info", "View information about the current gully"),
        BotCommand("join_gully", "Join the gully associated with this group"),
        # Team commands
        BotCommand("team_info", "View information about teams in this gully"),
        # Auction commands
        BotCommand("round_zero_status", "Check status of Round 0 submissions"),
        BotCommand("vote_time_slot", "Vote for preferred auction time"),
        BotCommand("time_slot_results", "View results of time slot voting"),
        BotCommand("auction_status", "Check current auction status"),
        # Admin commands (only visible to admins)
        BotCommand("add_admin", "Assign admin role to a user"),
        BotCommand("remove_admin", "Remove admin role from a user"),
        BotCommand("gully_settings", "Configure gully settings"),
        BotCommand("nominate_admin", "Nominate a new admin"),
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
