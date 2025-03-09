from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from typing import List, Dict, Any
import logging

from src.api.api_client_instance import api_client
from src.bot.keyboards.players import (
    get_player_filters_keyboard,
    get_player_details_keyboard,
)
from src.bot.utils.formatting import format_player_card


async def list_players_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle the /players command."""
    # Set current view for pagination
    context.user_data["current_view"] = "players"

    # Get page from context or default to 0
    page = context.user_data.get("current_page", 0)

    # Get filters from context or default to None
    team_filter = context.user_data.get("team_filter")
    type_filter = context.user_data.get("type_filter")

    # Get players from API
    players = await api_client.get_players(
        skip=page * 10, limit=10, team=team_filter, player_type=type_filter
    )

    if not players:
        # No players found
        keyboard = get_player_filters_keyboard()
        await update.effective_message.reply_text(
            "No players found with the current filters. Try different filters.",
            reply_markup=keyboard,
        )
        return

    # Format player list
    message = "*Available Players*\n\n"

    for i, player in enumerate(players):
        message += (
            f"{i+1}. *{player['name']}* ({player['team']}) - {player['player_type']}\n"
        )
        if player.get("sold_price"):
            message += f"   Price: ₹{player['sold_price']} cr\n"
        elif player.get("base_price"):
            message += f"   Base Price: ₹{player['base_price']} cr\n"
        message += "\n"

    # Add filter info if any
    if team_filter or type_filter:
        message += "*Filters:* "
        if team_filter:
            message += f"Team: {team_filter} "
        if type_filter:
            message += f"Type: {type_filter}"
        message += "\n\n"

    # Create keyboard with player selection buttons
    keyboard = []

    # Add player selection buttons
    for i, player in enumerate(players[:5]):
        keyboard.append(
            [
                InlineKeyboardButton(
                    f"{i+1}. {player['name']} ({player['team']})",
                    callback_data=f"player_details_{player['id']}",
                )
            ]
        )

    if len(players) > 5:
        for i, player in enumerate(players[5:10]):
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"{i+6}. {player['name']} ({player['team']})",
                        callback_data=f"player_details_{player['id']}",
                    )
                ]
            )

    # Add pagination
    pagination = []
    if page > 0:
        pagination.append(
            InlineKeyboardButton("« Prev", callback_data=f"nav_page_{page-1}")
        )

    pagination.append(InlineKeyboardButton("Filters", callback_data="player_filters"))

    # Assume there are more players if we got a full page
    if len(players) == 10:
        pagination.append(
            InlineKeyboardButton("Next »", callback_data=f"nav_page_{page+1}")
        )

    keyboard.append(pagination)

    # Add back button
    keyboard.append(
        [InlineKeyboardButton("« Back to Menu", callback_data="nav_back_main")]
    )

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send or edit message
    if update.callback_query:
        await update.callback_query.edit_message_text(
            message, reply_markup=reply_markup, parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            message, reply_markup=reply_markup, parse_mode="Markdown"
        )


async def search_players_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle the /search command."""
    # Check if search term was provided
    if not context.args:
        await update.message.reply_text(
            "Please provide a search term. Example: /search Kohli"
        )
        return

    # Get search term
    search_term = " ".join(context.args)

    # Search players
    players = await api_client.get_players(search=search_term, limit=10)

    if not players:
        await update.message.reply_text(f"No players found matching '{search_term}'.")
        return

    # Format player list
    message = f"*Search Results for '{search_term}'*\n\n"

    for i, player in enumerate(players):
        message += (
            f"{i+1}. *{player['name']}* ({player['team']}) - {player['player_type']}\n"
        )
        if player.get("sold_price"):
            message += f"   Price: ₹{player['sold_price']} cr\n"
        elif player.get("base_price"):
            message += f"   Base Price: ₹{player['base_price']} cr\n"
        message += "\n"

    # Create keyboard with player selection buttons
    keyboard = []

    # Add player selection buttons
    for i, player in enumerate(players[:5]):
        keyboard.append(
            [
                InlineKeyboardButton(
                    f"{i+1}. {player['name']} ({player['team']})",
                    callback_data=f"player_details_{player['id']}",
                )
            ]
        )

    if len(players) > 5:
        for i, player in enumerate(players[5:10]):
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"{i+6}. {player['name']} ({player['team']})",
                        callback_data=f"player_details_{player['id']}",
                    )
                ]
            )

    # Add back button
    keyboard.append([InlineKeyboardButton("« Back", callback_data="nav_back_players")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        message, reply_markup=reply_markup, parse_mode="Markdown"
    )


async def player_details(
    update: Update, context: ContextTypes.DEFAULT_TYPE, player_id: int = None
) -> None:
    """Show detailed information about a player."""
    if player_id is None:
        # Extract player_id from callback data
        if update.callback_query:
            player_id = int(update.callback_query.data.split("_")[-1])
        else:
            await update.effective_message.reply_text("Invalid player selection.")
            return

    # Get player details
    player = await api_client.get_player(player_id)

    if not player:
        await update.effective_message.reply_text("Player not found.")
        return

    # Format player card
    message = format_player_card(player)

    # Create keyboard
    keyboard = get_player_details_keyboard(player)

    # Send or edit message
    if update.callback_query:
        await update.callback_query.edit_message_text(
            message, reply_markup=keyboard, parse_mode="Markdown"
        )
    else:
        await update.effective_message.reply_text(
            message, reply_markup=keyboard, parse_mode="Markdown"
        )
