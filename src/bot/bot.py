#!/usr/bin/env python
"""
Main bot module for GullyGuru.
"""

import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import asyncio

from src.config import settings
from src.bot.handlers.start import (
    start_command,
    help_command,
    check_members_command,
    handle_start_callback,
)
from src.bot.handlers.game_guide import game_guide_command, handle_term_callback
from src.bot.handlers.team import my_team_command
from src.bot.handlers.auction import (
    auction_status_command,
    submit_squad_command,
    bid_command,
)
from src.bot.handlers.admin import admin_panel_command, create_gully_command
from src.bot.callbacks.auction import handle_auction_callback
from src.bot.callbacks.admin import handle_admin_callback
from src.bot.middleware import new_chat_members_handler

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")
    if update.effective_message:
        await update.effective_message.reply_text(
            "Sorry, something went wrong. Please try again later."
        )


async def main_async():
    """Async main function to run the bot."""
    # Create the application
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Register command handlers based on user journey documentation

    # Core Commands (available in all contexts)
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))

    # Personal Chat Commands
    application.add_handler(CommandHandler("game_guide", game_guide_command))
    application.add_handler(CommandHandler("myteam", my_team_command))
    application.add_handler(CommandHandler("submit_squad", submit_squad_command))
    application.add_handler(CommandHandler("bid", bid_command))
    application.add_handler(CommandHandler("auction_status", auction_status_command))

    # Admin Commands
    application.add_handler(CommandHandler("admin_panel", admin_panel_command))
    application.add_handler(CommandHandler("create_gully", create_gully_command))

    # Group Chat Commands
    # auction_status_command is already registered above and works in both contexts
    application.add_handler(CommandHandler("check_members", check_members_command))

    # Event Handlers
    application.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_chat_members_handler)
    )

    # Register callback query handlers
    application.add_handler(
        CallbackQueryHandler(handle_term_callback, pattern="^(term_|category_)")
    )
    application.add_handler(
        CallbackQueryHandler(
            handle_auction_callback, pattern="^(auction_|squad_|player_)"
        )
    )
    application.add_handler(
        CallbackQueryHandler(handle_admin_callback, pattern="^admin_")
    )
    application.add_handler(
        CallbackQueryHandler(handle_start_callback, pattern="^start_")
    )

    # Error handler
    application.add_error_handler(error_handler)

    # Set up command scopes
    from src.bot.command_scopes import setup_command_scopes

    # Initialize command scopes
    await setup_command_scopes(application)

    # Log startup
    logger.info("Bot is running. Press Ctrl+C to stop.")

    # Start the bot
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    # Keep the bot running
    try:
        # Keep the bot running until interrupted
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        # Log shutdown
        logger.info("Bot is shutting down...")
    finally:
        # Stop the bot
        await application.stop()


def main():
    """Main function to run the bot."""
    # Run the async main function
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
