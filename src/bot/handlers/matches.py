import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.api.api_client_instance import api_client
from src.bot.utils.formatting import format_match_card

logger = logging.getLogger(__name__)


async def list_matches_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle the /matches command to list upcoming matches."""
    user = update.effective_user

    # Get user from database
    db_user = await api_client.get_user(user.id)

    if not db_user:
        await update.message.reply_text(
            "You don't have an account yet. Use /join_gully to create one."
        )
        return

    # Get matches from API
    matches = await api_client.get_matches()

    if not matches:
        await update.message.reply_text("No upcoming matches found.")
        return

    # Pagination
    page = context.user_data.get("current_page", 1)
    items_per_page = 5
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    total_pages = (len(matches) + items_per_page - 1) // items_per_page

    # Get matches for current page
    current_matches = matches[start_idx:end_idx]

    # Format message
    message = "*Upcoming Matches*\n\n"

    for match in current_matches:
        # Create a brief summary for each match in the list
        match_date = match.get("date", "Unknown date")
        team1 = match.get("team1", "Team 1")
        team2 = match.get("team2", "Team 2")
        status = match.get("status", "upcoming")

        status_text = (
            "🔴 Live"
            if status == "live"
            else "🔜 Upcoming" if status == "upcoming" else "✅ Completed"
        )

        message += f"{status_text} *{team1} vs {team2}*\n"
        message += f"📅 {match_date}\n\n"

    # Create pagination keyboard
    keyboard = []

    # Add navigation buttons
    nav_buttons = []

    # Previous page button
    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton("◀️ Previous", callback_data=f"nav_page_{page-1}")
        )

    # Page indicator
    nav_buttons.append(
        InlineKeyboardButton(f"{page}/{total_pages}", callback_data="nav_noop")
    )

    # Next page button
    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton("Next ▶️", callback_data=f"nav_page_{page+1}")
        )

    keyboard.append(nav_buttons)

    # Add view details buttons for each match
    for i, match in enumerate(current_matches):
        keyboard.append(
            [
                InlineKeyboardButton(
                    f"View {match.get('team1')} vs {match.get('team2')}",
                    callback_data=f"match_view_{match.get('id')}",
                )
            ]
        )

    # Add back button
    keyboard.append(
        [InlineKeyboardButton("Back to Menu", callback_data="nav_back_main")]
    )

    # Set current view for pagination
    context.user_data["current_view"] = "matches"

    # Send message with keyboard
    await update.message.reply_text(
        message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )


async def view_match_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE, match_id: int = None
) -> None:
    """Handle viewing a specific match."""
    # If this is called from a callback query
    query = update.callback_query
    if query:
        await query.answer()

        # Extract match_id from callback data if not provided
        if not match_id and query.data.startswith("match_view_"):
            match_id = int(query.data.split("_")[-1])

    # Get match details
    match = await api_client.get_match(match_id)

    if not match:
        message = "Match not found."
        if query:
            await query.edit_message_text(message)
        else:
            await update.message.reply_text(message)
        return

    # Format match card
    message = format_match_card(match)

    # Create keyboard
    keyboard = [
        [
            InlineKeyboardButton(
                "Predict Winner", callback_data=f"match_predict_{match_id}"
            )
        ],
        [InlineKeyboardButton("Back to Matches", callback_data="nav_back_matches")],
    ]

    # Send or edit message
    if query:
        await query.edit_message_text(
            message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )
