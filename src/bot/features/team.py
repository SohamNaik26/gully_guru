"""
Team management features for GullyGuru bot.
Handles squad building and team management.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

from src.bot.api_client.onboarding import get_onboarding_client

# Configure logging
logger = logging.getLogger(__name__)


async def show_my_squad(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show the user's squad.
    This is a placeholder for now.
    """
    message = (
        "🏏 *My Squad* 🏏\n\n"
        "This feature is coming soon!\n\n"
        "You'll be able to view and manage your squad here."
    )

    keyboard = [
        [InlineKeyboardButton("Back to Main Menu", callback_data="back_to_main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            message, reply_markup=reply_markup, parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            message, reply_markup=reply_markup, parse_mode="Markdown"
        )


async def build_squad(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the 'Build Squad' button click.
    This is a placeholder for now.
    """
    query = update.callback_query
    await query.answer()

    # Extract gully ID from callback data
    try:
        gully_id = int(query.data.split("_")[2])
    except (ValueError, IndexError):
        logger.error(f"Invalid callback data for build_squad: {query.data}")
        await query.edit_message_text("❌ Invalid request. Please try again.")
        return

    # Get API client
    client = await get_onboarding_client()

    # Get gully
    gully = await client.get_gully(gully_id)
    if not gully:
        await query.edit_message_text("❌ Gully not found. Please try again later.")
        return

    # Store active gully ID in context
    context.user_data["active_gully_id"] = gully_id

    message = (
        f"🏏 *Build Your Squad for {gully['name']}* 🏏\n\n"
        "This feature is coming soon!\n\n"
        "You'll be able to select players for your squad here."
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "Select Batsmen", callback_data=f"select_batsmen_{gully_id}"
            ),
            InlineKeyboardButton(
                "Select Bowlers", callback_data=f"select_bowlers_{gully_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                "Select All-Rounders", callback_data=f"select_allrounders_{gully_id}"
            ),
            InlineKeyboardButton(
                "Select Wicket-Keepers", callback_data=f"select_keepers_{gully_id}"
            ),
        ],
        [InlineKeyboardButton("Back to Main Menu", callback_data="back_to_main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        message, reply_markup=reply_markup, parse_mode="Markdown"
    )


# Register handlers
def register_team_handlers(application):
    """Register team handlers."""
    application.add_handler(CallbackQueryHandler(build_squad, pattern="^team_build_"))
