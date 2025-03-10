"""
Features module for GullyGuru bot.
Contains all feature modules and handler registration.
"""

import logging
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters

from src.bot.features.admin import (
    admin_panel_command,
    handle_admin_callback,
)
from src.bot.features.auction import auction_status_command, handle_auction_callback
from src.bot.features.gully import new_chat_members_handler
from src.bot.features.team import my_team_command, handle_team_callback

# Configure logging
logger = logging.getLogger(__name__)


def register_handlers(application):
    """Register all command and callback handlers."""
    logger.info("Registering feature handlers...")

    # Admin feature handlers
    application.add_handler(CommandHandler("admin_panel", admin_panel_command))
    application.add_handler(
        CallbackQueryHandler(handle_admin_callback, pattern="^admin_")
    )

    # Auction feature handlers
    application.add_handler(CommandHandler("auction_status", auction_status_command))
    application.add_handler(
        CallbackQueryHandler(
            handle_auction_callback,
            pattern="^(start_auction|next_player|end_auction|bid_)",
        )
    )

    # Gully feature handlers - only keep the new members handler
    application.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_chat_members_handler)
    )

    # Team feature handlers
    application.add_handler(CommandHandler("my_team", my_team_command))
    application.add_handler(
        CallbackQueryHandler(handle_team_callback, pattern="^team_")
    )

    logger.info("All feature handlers registered successfully")
