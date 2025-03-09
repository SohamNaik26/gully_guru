#!/usr/bin/env python
"""
Main bot module for GullyGuru.
"""

import logging
import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from src.bot.handlers.help import help_command
from src.bot.handlers.game_guide import game_guide_command, handle_term_callback
from src.bot.handlers.join_gully import join_gully_command, handle_join_callback
from src.bot.handlers.team import my_team_command
from src.bot.handlers.auction import (
    submit_squad_command,
    bid_command,
    auction_status_command,
)
from src.bot.handlers.admin import (
    admin_panel_command,
    add_member_command,
    create_gully_command,
    manage_admins_command,
)
from src.bot.callbacks.auction import handle_auction_callback
from src.bot.callbacks.admin import handle_admin_callback
from src.bot.middleware import new_chat_members_handler
from src.bot.command_scopes import refresh_command_scopes
from src.api.api_client_instance import api_client
from src.bot.services import gully_service

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Route callback queries to the appropriate handler based on the pattern."""
    query = update.callback_query
    if query.data.startswith(("term_", "category_")):
        return handle_term_callback(update, context)
    elif query.data.startswith(("auction_", "squad_", "player_")):
        return handle_auction_callback(update, context)
    elif query.data.startswith("admin_"):
        return handle_admin_callback(update, context)
    elif query.data.startswith(("join_gully_", "decline_gully")):
        return handle_join_callback(update, context)

    # Default case
    query.answer("Unknown callback")
    return None


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the dispatcher."""
    logger.error("Exception while handling an update:", exc_info=context.error)


async def main_async():
    """Run the bot asynchronously."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    # Core Commands (available in all contexts)
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("game_guide", game_guide_command))
    application.add_handler(CommandHandler("join_gully", join_gully_command))

    # Personal Chat Commands
    application.add_handler(CommandHandler("my_team", my_team_command))
    application.add_handler(CommandHandler("bid", bid_command))
    application.add_handler(CommandHandler("submit_squad", submit_squad_command))
    application.add_handler(CommandHandler("auction_status", auction_status_command))

    # Admin Commands
    application.add_handler(CommandHandler("admin_panel", admin_panel_command))
    application.add_handler(CommandHandler("create_gully", create_gully_command))
    application.add_handler(CommandHandler("add_member", add_member_command))
    application.add_handler(CommandHandler("manage_admins", manage_admins_command))

    # Register callback query handlers
    application.add_handler(CallbackQueryHandler(callback_handler))

    # Register middleware
    application.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_chat_members_handler)
    )

    # Register error handler
    application.add_error_handler(error_handler)

    # Initialize the application
    await application.initialize()

    # Set up command scopes
    await refresh_command_scopes(application)

    # Scan all groups and set up gullies and admins
    logger.info("Scanning groups to set up gullies and admins...")
    scan_results = await gully_service.scan_and_setup_groups(application.bot)
    logger.info(
        f"Group scan complete: {scan_results['groups_scanned']} groups scanned, "
        f"{scan_results['gullies_created']} gullies created, "
        f"{scan_results['admins_set']} admins set up, "
        f"{scan_results['errors']} errors"
    )

    # Start the Bot
    await application.start()
    await application.updater.start_polling()
    logger.info("Bot started successfully")

    # Run the bot until the user presses Ctrl-C
    try:
        # Wait for signal to stop
        stop_signal = asyncio.Future()
        await stop_signal
    except (KeyboardInterrupt, SystemExit):
        # Handle graceful shutdown
        pass
    finally:
        # Ensure proper shutdown
        await application.stop()

        # Close the API client
        logger.info("Closing API client connection")
        await api_client.close()


def main():
    """Main function to run the bot."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
