import logging
from telegram import Update
from telegram.ext import ContextTypes

from src.api.api_client_instance import api_client
from src.bot.handlers import players

logger = logging.getLogger(__name__)


async def handle_player_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle player-related callbacks."""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("player_view_"):
        # Extract player ID from callback data
        player_id = int(data.split("_")[-1])
        await view_player(update, context, player_id)

    elif data.startswith("player_buy_"):
        # Extract player ID from callback data
        player_id = int(data.split("_")[-1])
        await buy_player(update, context, player_id)

    elif data.startswith("player_filter_"):
        # Extract filter type from callback data
        filter_type = data.split("_")[-1]
        context.user_data["player_filter"] = filter_type
        await players.list_players_command(update, context)

    elif data == "player_clear_filter":
        # Clear filter
        if "player_filter" in context.user_data:
            del context.user_data["player_filter"]
        await players.list_players_command(update, context)


async def view_player(
    update: Update, context: ContextTypes.DEFAULT_TYPE, player_id: int
) -> None:
    """View details of a specific player."""
    query = update.callback_query

    # Get player details from API
    player = await api_client.get_player(player_id)

    if not player:
        await query.edit_message_text("Player not found.")
        return

    # Format player details
    from src.bot.utils.formatting import format_player_card

    message = format_player_card(player)

    # Create keyboard for player actions
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    keyboard = []

    # Add buy button if player is available
    if player.get("auction_status") == "available":
        keyboard.append(
            [
                InlineKeyboardButton(
                    "Buy Player", callback_data=f"player_buy_{player_id}"
                )
            ]
        )

    # Add back button
    keyboard.append(
        [InlineKeyboardButton("Back to Players", callback_data="nav_back_players")]
    )

    # Edit message with player details and keyboard
    await query.edit_message_text(
        message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )


async def buy_player(
    update: Update, context: ContextTypes.DEFAULT_TYPE, player_id: int
) -> None:
    """Handle buying a player."""
    query = update.callback_query
    user = update.effective_user

    # Get user from database
    db_user = await api_client.get_user(user.id)

    if not db_user:
        await query.edit_message_text(
            "You don't have an account yet. Use /join_gully to create one."
        )
        return

    # Try to buy player
    result = await api_client.buy_player(db_user["id"], player_id)

    if result.get("success"):
        await query.edit_message_text(
            f"Successfully bought player: {result.get('player_name')}",
            parse_mode="Markdown",
        )
    else:
        error_message = result.get("error", "Unknown error occurred")
        await query.edit_message_text(
            f"Failed to buy player: {error_message}", parse_mode="Markdown"
        )
