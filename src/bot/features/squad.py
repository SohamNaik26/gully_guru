"""
Squad building feature for GullyGuru bot.
Implements the squad selection, viewing, and submission functionality.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from src.bot.api_client.squad import get_squad_client
from src.bot.api_client.onboarding import get_onboarding_client
from src.utils.decorators import log_function_call

# Configure logging
logger = logging.getLogger(__name__)


# Define conversation states
class STATES:
    SHOW_SQUAD_MENU = 1
    SELECTING_PLAYERS = 2
    VIEWING_SQUAD = 3
    CONFIRMING_SUBMISSION = 4
    SUBMIT_OR_CONTINUE = 5
    SQUAD_ACTIONS = 6
    REMOVING_PLAYERS = 7
    CONFIRM_SUBMISSION = 8
    HANDLE_MULTI_SELECT = 9
    HANDLE_MULTI_REMOVE = 10
    REMOVING_EXISTING_PLAYERS = 11
    CONFIRM_FINAL_SUBMISSION = 12


# Define callback data constants
class SQUAD_MENU:
    ADD_PLAYERS = "add_players"
    VIEW_SQUAD = "view_squad"
    SUBMIT_SQUAD = "submit_squad"
    CANCEL = "cancel"
    BACK_TO_MENU = "back_to_menu"
    START_BUILDING = "start_building_squad"


class PLAYER_FILTER:
    BATSMEN = "batsmen"
    BOWLERS = "bowlers"
    ALL_ROUNDERS = "all_rounders"
    WICKET_KEEPERS = "wicket_keepers"
    ALL_PLAYERS = "all_players"
    SEARCH_BY_NAME = "search_by_name"
    BACK = "back_to_filters"
    CANCEL = "cancel_filters"


class PLAYER_SELECTION:
    SELECT_PLAYER = "select_player"
    PAGE_PREFIX = "page_"
    MORE_PLAYERS = "more_players"


class REMOVE_PLAYER:
    REMOVE_PLAYER = "remove_player"
    MULTI_REMOVE = "multi_remove"
    TOGGLE_REMOVE = "toggle_remove"
    CONFIRM_MULTI_REMOVE = "confirm_multi_remove"
    CANCEL_MULTI_REMOVE = "cancel_multi_remove"


class CONFIRM_SUBMISSION:
    CONFIRM = "confirm_final"
    CANCEL = "cancel_submission"


class MULTI_SELECT:
    TOGGLE_SELECT = "toggle_select"
    CONFIRM_MULTI_SELECT = "confirm_multi_select"
    CANCEL_MULTI_SELECT = "cancel_multi_select"
    MULTI_SELECT = "multi_select"


class MULTI_REMOVE:
    TOGGLE_REMOVE = "toggle_remove"
    CONFIRM_MULTI_REMOVE = "confirm_multi_remove"
    CANCEL_MULTI_REMOVE = "cancel_multi_remove"
    MULTI_REMOVE = "multi_remove"


# Player type mapping
PLAYER_TYPES = {
    "BAT": "Batsman",
    "BOWL": "Bowler",
    "AR": "All-Rounder",
    "WK": "Wicket Keeper",
}


# Reply keyboard actions
class REPLY_KEYBOARD_ACTIONS:
    SELECT_PLAYER = "select_player"
    VIEW_CURRENT_SQUAD = "view_current_squad"
    SUBMIT_SQUAD = "submit_squad"
    BACK_TO_MENU = "back_to_menu"


@log_function_call
async def squad_menu_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Entry point for the squad menu from the main menu.
    This is a wrapper around show_squad_menu for direct access from main menu.
    """
    # If this is called from a callback query, answer it
    if update.callback_query:
        await update.callback_query.answer()

    # Show the squad menu
    return await show_squad_menu(update, context)


@log_function_call
async def squad_entry_point(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Entry point for all squad-related callbacks.
    Routes to the appropriate handler based on the callback data.
    """
    query = update.callback_query
    await query.answer()

    callback_data = query.data
    logger.info(f"Squad entry point received callback: {callback_data}")

    # Route to the appropriate handler based on the callback
    if callback_data == "squad_view" or callback_data == "menu_my_squad":
        # This is the "My Squad" button from the main menu
        return await my_squad_entry(update, context)
    elif callback_data == SQUAD_MENU.ADD_PLAYERS or callback_data == "add_players":
        return await show_player_selection_keyboard(update, context)
    elif callback_data == SQUAD_MENU.VIEW_SQUAD or callback_data == "view_squad":
        return await view_squad(update, context)
    elif callback_data == SQUAD_MENU.SUBMIT_SQUAD or callback_data == "submit_squad":
        return await confirm_submission(update, context)
    elif (
        callback_data == SQUAD_MENU.START_BUILDING
        or callback_data == "start_building_squad"
    ):
        return await show_player_selection_keyboard(update, context)
    elif callback_data == SQUAD_MENU.BACK_TO_MENU or callback_data == "back_to_menu":
        # Return to the squad menu
        return await show_squad_menu(update, context)
    elif callback_data == SQUAD_MENU.CANCEL or callback_data == "cancel":
        await query.edit_message_text("Squad building cancelled.")
        return ConversationHandler.END
    else:
        # Unknown callback, go back to squad menu
        logger.warning(f"Unknown callback in squad_entry_point: {callback_data}")
        return await show_squad_menu(update, context)


@log_function_call
async def show_squad_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Show the squad building menu.
    Uses cached squad data when available to avoid unnecessary API calls.
    """
    query = update.callback_query
    if query:
        await query.answer()
        message = query.message
    else:
        message = update.message

    # Get participant ID from context
    participant_id = context.user_data.get("participant_id")
    if not participant_id:
        await message.reply_text(
            "Session expired. Please use the main menu to access squad building again."
        )
        return ConversationHandler.END

    # Check if we have cached squad data
    cached_squad = context.user_data.get("cached_squad")

    # If no cached data, fetch from API
    if cached_squad is None:
        # Try to get current squad
        squad_client = await get_squad_client()
        squad = await squad_client.get_draft_squad(participant_id)

        # Cache the squad data
        context.user_data["cached_squad"] = squad if squad else {"players": []}
        cached_squad = context.user_data["cached_squad"]

    # Check if squad exists
    has_squad = cached_squad is not None and "players" in cached_squad
    player_count = len(cached_squad.get("players", [])) if has_squad else 0

    # Create keyboard
    keyboard = []

    if has_squad and player_count > 0:
        # Normal squad menu for existing squads
        keyboard = [
            [
                InlineKeyboardButton(
                    "Select Players", callback_data=SQUAD_MENU.ADD_PLAYERS
                ),
                InlineKeyboardButton("View Squad", callback_data=SQUAD_MENU.VIEW_SQUAD),
            ],
            [
                InlineKeyboardButton(
                    "Submit Squad", callback_data=SQUAD_MENU.SUBMIT_SQUAD
                ),
                InlineKeyboardButton("Cancel", callback_data=SQUAD_MENU.CANCEL),
            ],
        ]

        text = (
            f"🏏 *Squad Building Menu*\n\n"
            f"Current squad: {player_count}/18 players\n\n"
            f"Select an option to continue:"
        )
    else:
        # Special menu for new users without a squad
        keyboard = [
            [
                InlineKeyboardButton(
                    "Start Building Squad", callback_data=SQUAD_MENU.START_BUILDING
                ),
            ],
            [
                InlineKeyboardButton("Cancel", callback_data=SQUAD_MENU.CANCEL),
            ],
        ]

        text = (
            f"🏏 *Welcome to Squad Building!*\n\n"
            f"You don't have a squad yet. Let's create one!\n\n"
            f"You'll need to select 15-18 players for your squad.\n\n"
            f"Select an option to continue:"
        )

        # Store in context that this is a new squad
        context.user_data["new_squad"] = True

    reply_markup = InlineKeyboardMarkup(keyboard)

    if query:
        await query.edit_message_text(
            text, reply_markup=reply_markup, parse_mode="Markdown"
        )
    else:
        await message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    return STATES.SHOW_SQUAD_MENU


@log_function_call
async def view_squad(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Show the user's current squad.
    """
    query = update.callback_query
    if query:
        await query.answer()
        message = query.message
    else:
        message = update.message

    # Get participant ID from context
    participant_id = context.user_data.get("participant_id")
    logger.info(f"Viewing squad for participant_id: {participant_id}")

    if not participant_id:
        logger.error("No participant_id found in context")
        await message.reply_text(
            "Session expired. Please use the main menu to access squad building again.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "⬅️ Back to Main Menu", callback_data="main_menu"
                        )
                    ]
                ]
            ),
        )
        return ConversationHandler.END

    # Try to get current squad
    try:
        squad_client = await get_squad_client()
        squad = await squad_client.get_draft_squad(participant_id)

        # Debug log
        logger.info(f"Retrieved squad: {squad}")

        # Cache the squad data
        context.user_data["cached_squad"] = squad if squad else {"players": []}

        # Check if squad exists
        has_squad = squad is not None and "players" in squad
        player_count = len(squad.get("players", [])) if has_squad else 0

        # Create the message
        squad_message = "👥 *Your Squad*\n\n" f"Players: {player_count}/18\n"

        # Add submission status
        if player_count >= 15 and player_count <= 18:
            squad_message += "✅ You have enough players to submit your squad.\n\n"
        else:
            squad_message += f"❌ You need between 15-18 players to submit your squad. Currently: {player_count}\n\n"

        squad_message += "Players in your squad:\n\n"

        # Store player IDs for reference
        squad_player_ids = []

        # List all players
        for i, player in enumerate(squad.get("players", []), 1):
            player_data = player.get("player", {})
            player_id = player.get("player_id")
            squad_player_ids.append(player_id)

            player_name = player_data.get("name", "Unknown")
            player_team = player_data.get("team", "Unknown")
            player_price = player_data.get("base_price", "0.0")
            player_type = player_data.get("player_type", "Unknown")

            # Map player type to readable format
            readable_type = PLAYER_TYPES.get(player_type, player_type)

            squad_message += f"{i}. {player_name} - {player_team} - {readable_type} - {player_price} Cr\n"

        # Store squad player IDs in context
        context.user_data["squad_player_ids"] = squad_player_ids

        # Create reply keyboard with actions
        keyboard = []

        # Add remove players option if there are players
        if player_count > 0:
            keyboard.append(["🗑️ Remove Players"])

        # Add navigation buttons
        keyboard.append(["🔍 Add More Players"])

        # Add submit button if enough players
        if player_count >= 15 and player_count <= 18:
            keyboard.append(["📤 Submit Squad"])

        # Add back button
        keyboard.append(["⬅️ Back to Menu"])

        reply_markup = ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True, selective=True
        )

        # If this was called from a callback query, we need to send a new message with reply keyboard
        if query:
            # First, edit the inline message to show just the squad info
            await query.edit_message_text(squad_message, parse_mode="Markdown")
            # Then send a new message with the reply keyboard
            await message.reply_text(
                "What would you like to do?", reply_markup=reply_markup
            )
        else:
            # If this was called from a message, just reply with the squad and keyboard
            await message.reply_text(
                squad_message, reply_markup=reply_markup, parse_mode="Markdown"
            )

        return STATES.VIEWING_SQUAD

    except Exception as e:
        logger.error(f"Error viewing squad: {str(e)}")
        await message.reply_text(
            "An error occurred while retrieving your squad. Please try again later.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "⬅️ Back to Main Menu", callback_data="main_menu"
                        )
                    ]
                ]
            ),
        )
        return ConversationHandler.END


@log_function_call
async def show_player_selection_keyboard(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Show a reply keyboard with players for selection.
    Each row contains one player with all details.
    Fetches data once and caches it to minimize API calls.
    """
    query = update.callback_query
    if query:
        await query.answer()
        message = query.message
    else:
        message = update.message

    # Get participant ID from context
    participant_id = context.user_data.get("participant_id")
    if not participant_id:
        logger.error("No participant ID found in context")
        await message.reply_text(
            "Session expired. Please use the main menu to access squad building again."
        )
        return ConversationHandler.END

    # Show loading message
    loading_message = await message.reply_text(
        "Loading players...\n\n" "This may take a moment. Please wait.",
        parse_mode="Markdown",
    )

    # Check if we have cached data
    cached_players = context.user_data.get("cached_players")
    cached_squad = context.user_data.get("cached_squad")

    # Initialize or reset selection tracking
    context.user_data["selected_player_ids"] = []

    # Fetch data if not cached
    squad_client = await get_squad_client()

    if cached_squad is None:
        # Get current squad
        current_squad = await squad_client.get_draft_squad(participant_id)
        context.user_data["cached_squad"] = (
            current_squad if current_squad else {"players": []}
        )
        cached_squad = context.user_data["cached_squad"]

    if cached_players is None:
        # Get all available players
        all_players = await squad_client.get_available_players(limit=1000)
        context.user_data["cached_players"] = all_players
        cached_players = all_players

    # Extract player IDs already in squad
    squad_player_ids = []
    if cached_squad and "players" in cached_squad:
        squad_player_ids = [p.get("player_id") for p in cached_squad.get("players", [])]

    # Store squad player IDs for reference
    context.user_data["squad_player_ids"] = squad_player_ids

    # Create a player lookup dictionary for easy access
    player_lookup = {}
    for player in cached_players:
        player_lookup[player["id"]] = player

    context.user_data["player_lookup"] = player_lookup

    # Organize players by type for better display
    players_by_type = {
        "BAT": [],
        "BOWL": [],
        "AR": [],
        "WK": [],
    }

    for player in cached_players:
        player_type = player.get("player_type")
        if player_type in players_by_type:
            players_by_type[player_type].append(player)

    # Create a reply keyboard with all players
    keyboard = []

    # Add header for batsmen
    keyboard.append(["🏏 BATSMEN 🏏"])

    # Add batsmen
    for player in players_by_type["BAT"]:
        player_id = player.get("id")
        player_name = player.get("name", "Unknown")
        player_team = player.get("team", "Unknown")
        player_price = player.get("base_price", "0.0")

        # Check if already in squad
        in_squad = player_id in squad_player_ids

        if in_squad:
            prefix = "✅"  # Already in squad
        else:
            prefix = "⬜"  # Not selected

        button_text = f"{prefix} {player_name} - {player_team} - {player_price} Cr"
        keyboard.append([button_text])

    # Add header for bowlers
    keyboard.append(["🎯 BOWLERS 🎯"])

    # Add bowlers
    for player in players_by_type["BOWL"]:
        player_id = player.get("id")
        player_name = player.get("name", "Unknown")
        player_team = player.get("team", "Unknown")
        player_price = player.get("base_price", "0.0")

        # Check if already in squad
        in_squad = player_id in squad_player_ids

        if in_squad:
            prefix = "✅"  # Already in squad
        else:
            prefix = "⬜"  # Not selected

        button_text = f"{prefix} {player_name} - {player_team} - {player_price} Cr"
        keyboard.append([button_text])

    # Add header for all-rounders
    keyboard.append(["🏏🎯 ALL-ROUNDERS 🏏🎯"])

    # Add all-rounders
    for player in players_by_type["AR"]:
        player_id = player.get("id")
        player_name = player.get("name", "Unknown")
        player_team = player.get("team", "Unknown")
        player_price = player.get("base_price", "0.0")

        # Check if already in squad
        in_squad = player_id in squad_player_ids

        if in_squad:
            prefix = "✅"  # Already in squad
        else:
            prefix = "⬜"  # Not selected

        button_text = f"{prefix} {player_name} - {player_team} - {player_price} Cr"
        keyboard.append([button_text])

    # Add header for wicket-keepers
    keyboard.append(["🧤 WICKET-KEEPERS 🧤"])

    # Add wicket-keepers
    for player in players_by_type["WK"]:
        player_id = player.get("id")
        player_name = player.get("name", "Unknown")
        player_team = player.get("team", "Unknown")
        player_price = player.get("base_price", "0.0")

        # Check if already in squad
        in_squad = player_id in squad_player_ids

        if in_squad:
            prefix = "✅"  # Already in squad
        else:
            prefix = "⬜"  # Not selected

        button_text = f"{prefix} {player_name} - {player_team} - {player_price} Cr"
        keyboard.append([button_text])

    # Add view squad button
    keyboard.append(["🔄 View Current Squad"])

    # Create the reply keyboard markup
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        selective=True,
    )

    # Delete the loading message
    await loading_message.delete()

    # Calculate counts
    squad_count = len(squad_player_ids)

    # Create the message
    message_text = (
        "🏏 *Select Players for Your Squad*\n\n"
        f"Current squad: {squad_count}/18 players\n\n"
        "Tap on a player to select/deselect them for your squad.\n"
        "Players with ✅ are already in your squad.\n"
        "Players with ☑️ are selected but not yet added.\n\n"
        "When you're done selecting, tap 'View Current Squad' to review and submit."
    )

    # Send the message with the reply keyboard
    await message.reply_text(
        message_text,
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )

    return STATES.SELECTING_PLAYERS


@log_function_call
async def handle_player_selection_reply(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle player selection from reply keyboard.
    Toggle selection status without making API calls.
    """
    message_text = update.message.text

    # Check if user wants to view current squad
    if message_text == "🔄 View Current Squad":
        return await show_current_squad_selection(update, context)

    # Ignore header rows
    if (
        message_text.startswith("🏏 BATSMEN")
        or message_text.startswith("🎯 BOWLERS")
        or message_text.startswith("🏏🎯 ALL-ROUNDERS")
        or message_text.startswith("🧤 WICKET-KEEPERS")
    ):
        return STATES.SELECTING_PLAYERS

    # Extract player info from the message
    parts = message_text.split(" ", 1)
    if len(parts) < 2:
        return STATES.SELECTING_PLAYERS

    prefix = parts[0]
    player_info = parts[1]

    # Check if player is already in squad (has ✅)
    if prefix == "✅":
        await update.message.reply_text(
            "This player is already in your squad. To remove players, use the 'View Current Squad' option."
        )
        return STATES.SELECTING_PLAYERS

    # Find the player in cached data
    cached_players = context.user_data.get("cached_players", [])
    selected_player = None

    for player in cached_players:
        player_name = player.get("name", "Unknown")
        player_team = player.get("team", "Unknown")

        # Check if this player matches the selected one
        if f"{player_name} - {player_team}" in player_info:
            selected_player = player
            break

    if not selected_player:
        await update.message.reply_text(
            "❌ Could not find the selected player in the database."
        )
        return STATES.SELECTING_PLAYERS

    player_id = selected_player.get("id")
    player_name = selected_player.get("name", "Unknown")

    # Get current selections
    selected_player_ids = context.user_data.get("selected_player_ids", [])

    # Toggle selection
    if player_id in selected_player_ids:
        selected_player_ids.remove(player_id)
        await update.message.reply_text(f"❌ Removed {player_name} from selection.")
    else:
        # Check if maximum players reached
        squad_player_ids = context.user_data.get("squad_player_ids", [])
        total_selected = len(squad_player_ids) + len(selected_player_ids)

        if total_selected >= 18:
            await update.message.reply_text(
                "❌ You can select a maximum of 18 players. Please remove some players first."
            )
            return STATES.SELECTING_PLAYERS

        selected_player_ids.append(player_id)
        await update.message.reply_text(f"✅ Added {player_name} to selection.")

    # Update context
    context.user_data["selected_player_ids"] = selected_player_ids

    return STATES.SELECTING_PLAYERS


@log_function_call
async def show_current_squad_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Show the current squad during selection process.
    Uses cached data to avoid API calls.
    """
    # Get cached data
    cached_squad = context.user_data.get("cached_squad", {"players": []})
    selected_player_ids = context.user_data.get("selected_player_ids", [])
    player_lookup = context.user_data.get("player_lookup", {})

    # Extract current squad player IDs
    squad_player_ids = context.user_data.get("squad_player_ids", [])

    if not squad_player_ids and not selected_player_ids:
        await update.message.reply_text(
            "You haven't selected any players yet. Please select at least 15 players."
        )
        return STATES.SELECTING_PLAYERS

    # Build squad message
    squad_message = "Your Current Squad:\n\n"
    total_price = 0

    # Add existing squad players
    if squad_player_ids:
        squad_message += "Already in squad:\n"
        for i, player_id in enumerate(squad_player_ids, 1):
            player_data = None

            # Find player in cached squad
            for squad_player in cached_squad.get("players", []):
                if squad_player.get("player_id") == player_id:
                    player_data = squad_player.get("player", {})
                    break

            if player_data:
                player_name = player_data.get("name", "Unknown")
                player_team = player_data.get("team", "Unknown")
                player_price = player_data.get("base_price", "0.0")

                squad_message += (
                    f"{i}. {player_name} - {player_team} - {player_price} Cr ✅\n"
                )
                total_price += float(player_price)

    # Add newly selected players
    if selected_player_ids:
        if squad_player_ids:
            squad_message += "\nNewly selected:\n"
            start_index = len(squad_player_ids) + 1
        else:
            start_index = 1

        for i, player_id in enumerate(selected_player_ids, start_index):
            player = player_lookup.get(player_id, {})
            if player:
                player_name = player.get("name", "Unknown")
                player_team = player.get("team", "Unknown")
                player_price = player.get("base_price", "0.0")

                squad_message += (
                    f"{i}. {player_name} - {player_team} - {player_price} Cr ☑️\n"
                )
                total_price += float(player_price)

    # Add summary
    total_players = len(squad_player_ids) + len(selected_player_ids)
    squad_message += f"\nBudget Used: {total_price} Cr / 120 Cr\n"
    squad_message += f"Players: {total_players} / 18"

    # Create keyboard for actions
    keyboard = []

    # Add submit button if minimum players selected
    if total_players >= 15:
        keyboard.append(["Submit Squad"])

    # Add edit buttons
    if selected_player_ids:
        keyboard.append(["Edit Selection"])

    keyboard.append(["Continue Selecting"])

    reply_markup = ReplyKeyboardMarkup(
        keyboard, resize_keyboard=True, one_time_keyboard=True, selective=True
    )

    await update.message.reply_text(squad_message, reply_markup=reply_markup)
    return STATES.SQUAD_ACTIONS


@log_function_call
async def handle_squad_actions(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle actions from the squad view.
    """
    action = update.message.text

    if action == "Submit Squad":
        return await confirm_submission(update, context)
    elif action == "Edit Selection":
        return await show_remove_players_keyboard(update, context)
    elif action == "Continue Selecting":
        return await show_player_selection_keyboard(update, context)
    else:
        await update.message.reply_text("Invalid action. Please try again.")
        return await show_current_squad_selection(update, context)


@log_function_call
async def show_remove_players_keyboard(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Show keyboard for removing selected players.
    No API calls - works with cached data.
    """
    selected_player_ids = context.user_data.get("selected_player_ids", [])
    player_lookup = context.user_data.get("player_lookup", {})

    if not selected_player_ids:
        await update.message.reply_text("You don't have any new selections to edit.")
        return await show_current_squad_selection(update, context)

    # Create keyboard with selected players
    keyboard = []

    for player_id in selected_player_ids:
        player = player_lookup.get(player_id, {})
        if player:
            player_name = player.get("name", "Unknown")
            player_team = player.get("team", "Unknown")
            player_price = player.get("base_price", "0.0")

            keyboard.append([f"❌ {player_name} - {player_team} - {player_price} Cr"])

    # Add confirm and cancel buttons
    keyboard.append(["✅ Confirm Removals"])
    keyboard.append(["❌ Cancel"])

    reply_markup = ReplyKeyboardMarkup(
        keyboard, resize_keyboard=True, one_time_keyboard=False, selective=True
    )

    # Store players to remove
    context.user_data["players_to_remove"] = []

    await update.message.reply_text(
        "Select players to remove by tapping on them. Then tap 'Confirm Removals' when done.",
        reply_markup=reply_markup,
    )

    return STATES.REMOVING_PLAYERS


@log_function_call
async def handle_remove_player_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle player removal selection.
    No API calls - just updates context.
    """
    message_text = update.message.text

    # Check for confirm/cancel actions
    if message_text == "✅ Confirm Removals":
        return await confirm_player_removals(update, context)
    elif message_text == "❌ Cancel":
        await update.message.reply_text("Player removal cancelled.")
        return await show_current_squad_selection(update, context)

    # Extract player name from message
    # Format is: ❌ Player Name - Team - Price
    if not message_text.startswith("❌ "):
        await update.message.reply_text("Invalid selection. Please try again.")
        return STATES.REMOVING_PLAYERS

    player_info = message_text[2:]  # Remove the ❌ prefix

    # Find the player in selected players
    selected_player_ids = context.user_data.get("selected_player_ids", [])
    player_lookup = context.user_data.get("player_lookup", {})
    players_to_remove = context.user_data.get("players_to_remove", [])

    found_player_id = None
    for player_id in selected_player_ids:
        player = player_lookup.get(player_id, {})
        if player:
            player_name = player.get("name", "Unknown")
            player_team = player.get("team", "Unknown")

            if f"{player_name} - {player_team}" in player_info:
                found_player_id = player_id
                break

    if not found_player_id:
        await update.message.reply_text(
            "Player not found in your selections. Please try again."
        )
        return STATES.REMOVING_PLAYERS

    # Toggle removal
    if found_player_id in players_to_remove:
        players_to_remove.remove(found_player_id)
        await update.message.reply_text(f"Player will not be removed.")
    else:
        players_to_remove.append(found_player_id)
        await update.message.reply_text(f"Player marked for removal.")

    # Update context
    context.user_data["players_to_remove"] = players_to_remove

    return STATES.REMOVING_PLAYERS


@log_function_call
async def confirm_player_removals(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Confirm and process player removals.
    No API calls - just updates context.
    """
    players_to_remove = context.user_data.get("players_to_remove", [])
    selected_player_ids = context.user_data.get("selected_player_ids", [])
    player_lookup = context.user_data.get("player_lookup", {})

    if not players_to_remove:
        await update.message.reply_text("No players selected for removal.")
        return await show_current_squad_selection(update, context)

    # Get player names for confirmation message
    removed_player_names = []
    for player_id in players_to_remove:
        player = player_lookup.get(player_id, {})
        if player:
            removed_player_names.append(player.get("name", f"Player {player_id}"))

            # Remove from selected players
            if player_id in selected_player_ids:
                selected_player_ids.remove(player_id)

    # Update context
    context.user_data["selected_player_ids"] = selected_player_ids
    context.user_data["players_to_remove"] = []

    # Send confirmation
    await update.message.reply_text(
        f"✅ Removed {len(players_to_remove)} players: {', '.join(removed_player_names)}.\n"
        f"You now have {len(selected_player_ids)} new selections."
    )

    # Return to squad view
    return await show_current_squad_selection(update, context)


@log_function_call
async def confirm_submission(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Confirm squad submission.
    Uses cached data to avoid unnecessary API calls.
    """
    query = update.callback_query
    await query.answer()

    # Get participant ID from context
    participant_id = context.user_data.get("participant_id")

    # Get cached squad data
    cached_squad = context.user_data.get("cached_squad")

    # If no cached data or refresh is needed, fetch from API
    if cached_squad is None or context.user_data.get("refresh_squad", True):
        # Get the user's draft squad
        squad_client = await get_squad_client()
        squad_data = await squad_client.get_draft_squad(participant_id)

        # Cache the squad data
        context.user_data["cached_squad"] = (
            squad_data if squad_data else {"players": []}
        )
        context.user_data["refresh_squad"] = False
        cached_squad = context.user_data["cached_squad"]

    # Check if squad exists
    if not cached_squad or not cached_squad.get("players"):
        await query.edit_message_text(
            "You don't have a squad to submit yet.\n\n"
            "Let's start by building your squad first!",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Start Building Squad", callback_data=SQUAD_MENU.ADD_PLAYERS
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Back to Menu", callback_data=SQUAD_MENU.BACK_TO_MENU
                        )
                    ],
                ]
            ),
        )
        return STATES.SHOW_SQUAD_MENU

    # Calculate budget and player count
    total_budget = 120.0  # Default budget
    used_budget = 0.0
    players = cached_squad["players"]
    player_count = len(players)

    # Calculate used budget
    for player in players:
        if "player" in player and "base_price" in player["player"]:
            try:
                used_budget += float(player["player"]["base_price"])
            except (ValueError, TypeError):
                logger.warning(f"Invalid base_price for player: {player}")

    remaining_budget = total_budget - used_budget

    # Validate player count
    if player_count < 15:
        await query.edit_message_text(
            f"❌ You need at least 15 players to submit your squad. Currently: {player_count}\n\n"
            "Please add more players before submitting.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🔍 Add More Players", callback_data=SQUAD_MENU.ADD_PLAYERS
                        ),
                        InlineKeyboardButton(
                            "⬅️ Back to Menu", callback_data=SQUAD_MENU.BACK_TO_MENU
                        ),
                    ]
                ]
            ),
        )
        return STATES.VIEWING_SQUAD

    if player_count > 18:
        await query.edit_message_text(
            f"❌ You can have at most 18 players in your squad. Currently: {player_count}\n\n"
            "Please remove some players before submitting.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "👥 View Squad", callback_data=SQUAD_MENU.VIEW_SQUAD
                        ),
                        InlineKeyboardButton(
                            "⬅️ Back to Menu", callback_data=SQUAD_MENU.BACK_TO_MENU
                        ),
                    ]
                ]
            ),
        )
        return STATES.VIEWING_SQUAD

    # Validate budget
    if used_budget > total_budget:
        await query.edit_message_text(
            f"❌ Your squad exceeds the budget limit of {total_budget} Cr. "
            f"Current budget: {used_budget:.1f} Cr\n\n"
            "Please remove some players before submitting.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "👥 View Squad", callback_data=SQUAD_MENU.VIEW_SQUAD
                        ),
                        InlineKeyboardButton(
                            "⬅️ Back to Menu", callback_data=SQUAD_MENU.BACK_TO_MENU
                        ),
                    ]
                ]
            ),
        )
        return STATES.VIEWING_SQUAD

    # Show confirmation message
    message = (
        "🏏 *Confirm Squad Submission* 🏏\n\n"
        f"You are about to submit your squad with {player_count} players "
        f"and a total budget of {used_budget:.1f} Cr.\n\n"
        "This action cannot be undone. Are you sure you want to submit your squad?"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Confirm Submission", callback_data=CONFIRM_SUBMISSION.CONFIRM
            ),
            InlineKeyboardButton("❌ Cancel", callback_data=CONFIRM_SUBMISSION.CANCEL),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        message, reply_markup=reply_markup, parse_mode="Markdown"
    )

    return STATES.CONFIRMING_SUBMISSION


@log_function_call
async def handle_submission_confirmation_reply(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle confirmation of squad submission from reply keyboard.
    This is an alias for handle_final_submission_confirmation for backward compatibility.
    """
    return await handle_final_submission_confirmation(update, context)


@log_function_call
async def my_squad_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Entry point for the "My Squad" button from the main menu.
    Checks if the user has a squad and routes accordingly.
    """
    query = update.callback_query
    await query.answer()

    # Get participant ID from context
    participant_id = context.user_data.get("participant_id")
    if not participant_id:
        await query.edit_message_text(
            "Session expired. Please use the main menu to access squad building again.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "⬅️ Back to Main Menu", callback_data="main_menu"
                        )
                    ]
                ]
            ),
        )
        return ConversationHandler.END

    # Check if we have cached squad data
    cached_squad = context.user_data.get("cached_squad")

    # If no cached data or refresh is needed, fetch from API
    if cached_squad is None or context.user_data.get("refresh_squad", False):
        # Check if the user has a squad
        squad_client = await get_squad_client()
        squad_data = await squad_client.get_draft_squad(participant_id)

        # Cache the squad data
        context.user_data["cached_squad"] = (
            squad_data if squad_data else {"players": []}
        )
        context.user_data["refresh_squad"] = False
        cached_squad = context.user_data["cached_squad"]

    if cached_squad and "players" in cached_squad and cached_squad["players"]:
        # User has a squad, show it
        return await view_squad(update, context)
    else:
        # User doesn't have a squad, show squad menu
        return await show_squad_menu(update, context)


@log_function_call
async def get_user_participant_data(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> Tuple[Optional[int], Optional[int]]:
    """
    Get user and participant data from context or API.
    Returns a tuple of (user_id, participant_id).
    """
    # Try to get from context first
    user_id = context.user_data.get("user_id")
    participant_id = context.user_data.get("participant_id")

    # If not in context, try to get from API
    if not user_id or not participant_id:
        # Get user ID from update
        user_id = update.effective_user.id

        # Get participant ID from API
        onboarding_client = await get_onboarding_client()
        try:
            user_data = await onboarding_client.get_user_by_telegram_id(user_id)
            if user_data and "id" in user_data:
                user_id = user_data["id"]
                context.user_data["user_id"] = user_id

                # Get participant data
                participant_data = await onboarding_client.get_participant_by_user_id(
                    user_id
                )
                if participant_data and "id" in participant_data:
                    participant_id = participant_data["id"]
                    context.user_data["participant_id"] = participant_id
                else:
                    logger.error(f"No participant found for user {user_id}")
            else:
                logger.error(f"No user found for telegram ID {user_id}")
        except Exception as e:
            logger.exception(f"Error getting user/participant data: {str(e)}")

    return user_id, participant_id


@log_function_call
async def register_squad_handlers(application):
    """Register squad handlers."""
    logger.info("Registering squad handlers")

    # Add direct handlers for specific patterns outside the conversation
    application.add_handler(
        CallbackQueryHandler(my_squad_entry, pattern="^menu_my_squad$")
    )
    application.add_handler(CallbackQueryHandler(view_squad, pattern="^squad_view$"))

    # Add the squad entry point handler for other squad-related patterns
    application.add_handler(CallbackQueryHandler(squad_entry_point, pattern="^squad_"))

    # Add conversation handler for reply keyboard-based squad selection
    squad_selection_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                show_player_selection_keyboard, pattern=f"^{SQUAD_MENU.START_BUILDING}$"
            ),
            CallbackQueryHandler(
                show_player_selection_keyboard, pattern=f"^{SQUAD_MENU.ADD_PLAYERS}$"
            ),
        ],
        states={
            STATES.SELECTING_PLAYERS: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, handle_player_selection_reply
                )
            ],
            STATES.SQUAD_ACTIONS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_squad_actions)
            ],
            STATES.REMOVING_PLAYERS: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, handle_remove_player_selection
                )
            ],
            STATES.CONFIRM_SUBMISSION: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    handle_submission_confirmation,
                )
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_squad_selection),
            CallbackQueryHandler(cancel_squad_selection, pattern="^cancel$"),
        ],
        name="squad_selection",
        persistent=False,
    )

    application.add_handler(squad_selection_conv)

    # Add conversation handler for squad viewing and management with reply keyboard
    squad_view_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(view_squad, pattern=f"^{SQUAD_MENU.VIEW_SQUAD}$"),
            CallbackQueryHandler(view_squad, pattern="^squad_view$"),
            CallbackQueryHandler(my_squad_entry, pattern="^menu_my_squad$"),
        ],
        states={
            STATES.VIEWING_SQUAD: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, handle_squad_view_actions
                )
            ],
            STATES.REMOVING_EXISTING_PLAYERS: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    handle_remove_existing_player_selection,
                )
            ],
            STATES.CONFIRM_FINAL_SUBMISSION: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    handle_final_submission_confirmation,
                )
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_squad_selection),
            CallbackQueryHandler(cancel_squad_selection, pattern="^cancel$"),
        ],
        name="squad_view",
        persistent=False,
    )

    application.add_handler(squad_view_conv)
    logger.info("Squad handlers registered successfully")


@log_function_call
async def handle_squad_view_actions(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle actions from the squad view reply keyboard.
    """
    action = update.message.text

    if action == "🗑️ Remove Players":
        return await show_remove_existing_players_keyboard(update, context)
    elif action == "🔍 Add More Players":
        return await show_player_selection_keyboard(update, context)
    elif action == "📤 Submit Squad":
        return await confirm_squad_submission_from_view(update, context)
    elif action == "⬅️ Back to Menu":
        # Return to squad menu
        reply_markup = ReplyKeyboardRemove()
        await update.message.reply_text(
            "Returning to menu...", reply_markup=reply_markup
        )
        return await show_squad_menu(update, context)
    else:
        await update.message.reply_text("Invalid action. Please try again.")
        return await view_squad(update, context)


@log_function_call
async def show_remove_existing_players_keyboard(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Show keyboard for removing existing squad players.
    Uses reply keyboard for consistent UX.
    """
    cached_squad = context.user_data.get("cached_squad", {"players": []})
    squad_player_ids = context.user_data.get("squad_player_ids", [])

    if not squad_player_ids:
        await update.message.reply_text(
            "You don't have any players in your squad to remove."
        )
        return await view_squad(update, context)

    # Create keyboard with squad players
    keyboard = []

    for player in cached_squad.get("players", []):
        player_data = player.get("player", {})
        player_id = player.get("player_id")

        player_name = player_data.get("name", "Unknown")
        player_team = player_data.get("team", "Unknown")
        player_price = player_data.get("base_price", "0.0")

        keyboard.append([f"❌ {player_name} - {player_team} - {player_price} Cr"])

    # Add confirm and cancel buttons
    keyboard.append(["✅ Confirm Removals"])
    keyboard.append(["❌ Cancel"])

    reply_markup = ReplyKeyboardMarkup(
        keyboard, resize_keyboard=True, one_time_keyboard=False, selective=True
    )

    # Store players to remove
    context.user_data["existing_players_to_remove"] = []

    await update.message.reply_text(
        "Select players to remove by tapping on them. Then tap 'Confirm Removals' when done.",
        reply_markup=reply_markup,
    )

    return STATES.REMOVING_EXISTING_PLAYERS


@log_function_call
async def handle_remove_existing_player_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle player removal selection for existing squad players.
    No API calls - just updates context.
    """
    message_text = update.message.text

    # Check for confirm/cancel actions
    if message_text == "✅ Confirm Removals":
        return await confirm_existing_player_removals(update, context)
    elif message_text == "❌ Cancel":
        await update.message.reply_text("Player removal cancelled.")
        return await view_squad(update, context)

    # Extract player name from message
    # Format is: ❌ Player Name - Team - Price
    if not message_text.startswith("❌ "):
        await update.message.reply_text("Invalid selection. Please try again.")
        return STATES.REMOVING_EXISTING_PLAYERS

    player_info = message_text[2:]  # Remove the ❌ prefix

    # Find the player in squad
    cached_squad = context.user_data.get("cached_squad", {"players": []})
    existing_players_to_remove = context.user_data.get("existing_players_to_remove", [])

    found_player_id = None
    found_player_name = None

    for player in cached_squad.get("players", []):
        player_data = player.get("player", {})
        player_id = player.get("player_id")

        player_name = player_data.get("name", "Unknown")
        player_team = player_data.get("team", "Unknown")

        if f"{player_name} - {player_team}" in player_info:
            found_player_id = player_id
            found_player_name = player_name
            break

    if not found_player_id:
        await update.message.reply_text(
            "Player not found in your squad. Please try again."
        )
        return STATES.REMOVING_EXISTING_PLAYERS

    # Toggle removal
    if found_player_id in existing_players_to_remove:
        existing_players_to_remove.remove(found_player_id)
        await update.message.reply_text(f"{found_player_name} will not be removed.")
    else:
        existing_players_to_remove.append(found_player_id)
        await update.message.reply_text(f"{found_player_name} marked for removal.")

    # Update context
    context.user_data["existing_players_to_remove"] = existing_players_to_remove

    return STATES.REMOVING_EXISTING_PLAYERS


@log_function_call
async def confirm_existing_player_removals(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Confirm and process removal of existing squad players.
    Makes API calls to remove players.
    """
    existing_players_to_remove = context.user_data.get("existing_players_to_remove", [])
    cached_squad = context.user_data.get("cached_squad", {"players": []})
    participant_id = context.user_data.get("participant_id")

    if not existing_players_to_remove:
        await update.message.reply_text("No players selected for removal.")
        return await view_squad(update, context)

    # Show loading message
    loading_message = await update.message.reply_text(
        f"Removing {len(existing_players_to_remove)} players from your squad...\n\n"
        "This may take a moment. Please wait."
    )

    # Get player names for confirmation message
    removed_player_names = []

    # Find player names
    for player in cached_squad.get("players", []):
        player_data = player.get("player", {})
        player_id = player.get("player_id")

        if player_id in existing_players_to_remove:
            removed_player_names.append(player_data.get("name", f"Player {player_id}"))

    # Remove players from draft - this is where we make API calls
    squad_client = await get_squad_client()
    success_count = 0
    error_messages = []

    # Ideally, we would have a batch remove API endpoint
    # For now, we'll remove one by one but optimize this in the future
    for player_id in existing_players_to_remove:
        try:
            result = await squad_client.remove_player_from_draft(
                participant_id, player_id
            )
            if result.get("success"):
                success_count += 1
            else:
                error_message = result.get("error", "Unknown error")
                error_messages.append(f"Player {player_id}: {error_message}")
        except Exception as e:
            error_messages.append(f"Player {player_id}: {str(e)}")

    # Delete loading message
    await loading_message.delete()

    # Clear removal list
    context.user_data["existing_players_to_remove"] = []

    # Mark squad data for refresh
    context.user_data["refresh_squad"] = True

    # Show result message
    if success_count == len(existing_players_to_remove):
        await update.message.reply_text(
            f"✅ Successfully removed {success_count} players: {', '.join(removed_player_names)}."
        )
    else:
        error_text = "\n".join(error_messages[:5])
        if len(error_messages) > 5:
            error_text += f"\n...and {len(error_messages) - 5} more errors."

        await update.message.reply_text(
            f"⚠️ Removed {success_count} out of {len(existing_players_to_remove)} players.\n\n"
            f"Errors:\n{error_text}"
        )

    # Return to squad view
    return await view_squad(update, context)


@log_function_call
async def confirm_squad_submission_from_view(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Show confirmation for squad submission from squad view.
    Uses reply keyboard.
    """
    cached_squad = context.user_data.get("cached_squad", {"players": []})

    # Calculate player count and budget
    players = cached_squad.get("players", [])
    player_count = len(players)

    if player_count < 15:
        await update.message.reply_text(
            f"❌ You need at least 15 players to submit your squad. Currently: {player_count}\n\n"
            "Please add more players."
        )
        return await view_squad(update, context)

    if player_count > 18:
        await update.message.reply_text(
            f"❌ You can have at most 18 players in your squad. Currently: {player_count}\n\n"
            "Please remove some players."
        )
        return await view_squad(update, context)

    # Calculate budget
    total_budget = 120.0
    used_budget = 0.0

    for player in players:
        if "player" in player and "base_price" in player["player"]:
            try:
                used_budget += float(player["player"]["base_price"])
            except (ValueError, TypeError):
                pass

    # Create confirmation message
    message = (
        f"You have selected {player_count} players for a total of {used_budget:.1f} Cr.\n"
        "Are you sure you want to submit your squad?"
    )

    # Create keyboard
    keyboard = [["✅ Submit Squad"], ["🔄 Edit Squad"]]

    reply_markup = ReplyKeyboardMarkup(
        keyboard, resize_keyboard=True, one_time_keyboard=True, selective=True
    )

    await update.message.reply_text(message, reply_markup=reply_markup)
    return STATES.CONFIRM_FINAL_SUBMISSION


@log_function_call
async def handle_final_submission_confirmation(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle the final submission confirmation from squad view.
    Uses update_draft_squad to finalize the squad.
    """
    action = update.message.text

    if action == "✅ Submit Squad":
        return await submit_final_squad_from_view(update, context)
    elif action == "🔄 Edit Squad":
        await update.message.reply_text("Returning to squad editing.")
        return await view_squad(update, context)
    else:
        await update.message.reply_text("Invalid action. Please try again.")
        return await confirm_squad_submission_from_view(update, context)


@log_function_call
async def submit_final_squad_from_view(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Submit the final squad to the database from squad view.
    Uses update_draft_squad to finalize the squad.
    """
    participant_id = context.user_data.get("participant_id")
    cached_squad = context.user_data.get("cached_squad", {"players": []})

    if not participant_id:
        logger.error(f"No participant_id found for user {update.effective_user.id}")
        await update.message.reply_text(
            "❌ Error: Could not find your participant data. Please try again later."
        )
        return ConversationHandler.END

    # Extract player IDs from cached squad
    player_ids = [player.get("player_id") for player in cached_squad.get("players", [])]

    # Show loading message
    loading_message = await update.message.reply_text(
        "Finalizing your squad...\n\n" "This may take a moment. Please wait."
    )

    # Update the draft squad - this finalizes the squad
    squad_client = await get_squad_client()
    try:
        result = await squad_client.update_draft_squad(participant_id, player_ids)

        # Delete loading message
        await loading_message.delete()

        if result.get("success"):
            # Return to normal keyboard
            reply_markup = ReplyKeyboardRemove()

            await update.message.reply_text(
                "✅ Your squad has been submitted successfully!\n\n"
                "Your squad is now locked for the tournament. Good luck!",
                reply_markup=reply_markup,
            )

            # Show the main menu
            from src.bot.bot import show_main_menu

            await show_main_menu(update, context)
            return ConversationHandler.END
        else:
            error_message = result.get("error", "Unknown error")
            logger.error(f"Error submitting squad: {error_message}")
            await update.message.reply_text(
                f"❌ Error submitting squad: {error_message}\nPlease try again later."
            )
            return await view_squad(update, context)
    except Exception as e:
        # Delete loading message
        await loading_message.delete()

        logger.error(f"Error submitting squad: {str(e)}")
        await update.message.reply_text(
            f"❌ Error submitting squad: {str(e)}\nPlease try again later."
        )
        return await view_squad(update, context)


@log_function_call
async def cancel_squad_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Cancel the squad selection process.
    """
    # Clear selection data from context
    context.user_data.pop("selected_player_ids", None)
    context.user_data.pop("players_to_remove", None)
    context.user_data.pop("existing_players_to_remove", None)

    # Return to normal keyboard
    reply_markup = ReplyKeyboardRemove()

    if update.callback_query:
        await update.callback_query.edit_message_text("Squad selection cancelled.")
    else:
        await update.message.reply_text(
            "Squad selection cancelled.", reply_markup=reply_markup
        )

    # Show the main menu
    from src.bot.bot import show_main_menu

    await show_main_menu(update, context)
    return ConversationHandler.END


# Aliases for backward compatibility
squad_menu = show_squad_menu
submit_final_squad = submit_final_squad_from_view
handle_submission_confirmation_reply = handle_final_submission_confirmation
confirm_squad_submission = confirm_submission

# For any other potential imports
show_squad_selection = show_player_selection_keyboard
handle_squad_selection = handle_player_selection_reply
handle_squad_view_reply = handle_squad_view_actions


@log_function_call
async def show_all_players(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Show all available players for selection.
    This is an alias for show_player_selection_keyboard for backward compatibility.
    """
    return await show_player_selection_keyboard(update, context)


@log_function_call
async def handle_multi_select_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle multi-select callbacks.
    This is a placeholder for backward compatibility.
    """
    # This should be implemented based on your specific requirements
    query = update.callback_query
    await query.answer()

    # For now, just return to player selection
    return await show_player_selection_keyboard(update, context)


@log_function_call
async def handle_view_squad_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle view squad callbacks.
    This is a placeholder for backward compatibility.
    """
    # This should be implemented based on your specific requirements
    query = update.callback_query
    await query.answer()

    # For now, just return to view squad
    return await view_squad(update, context)


@log_function_call
async def handle_multi_remove_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle multi-remove callbacks.
    This is a placeholder for backward compatibility.
    """
    # This should be implemented based on your specific requirements
    query = update.callback_query
    await query.answer()

    # For now, just return to view squad
    return await view_squad(update, context)


@log_function_call
async def handle_submission_confirmation(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle submission confirmation callbacks.
    This is an alias for handle_final_submission_confirmation for backward compatibility.
    """
    return await handle_final_submission_confirmation(update, context)
