import logging
import asyncio
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


# Configure logging
logger = logging.getLogger(__name__)

# Define conversation states
(
    SHOW_SQUAD_MENU,
    SHOW_PLAYER_FILTERS,
    HANDLE_PLAYER_FILTER,
    SHOW_PLAYERS,
    HANDLE_PLAYER_SELECTION,
    HANDLE_MULTI_SELECT,
    VIEW_SQUAD,
    HANDLE_MULTI_REMOVE,
    CONFIRM_SQUAD_SUBMISSION,
    HANDLE_REMOVE_PLAYER,
    NAME_SEARCH,
    HANDLE_NEW_SQUAD,
) = range(12)

# Player type mapping - updated based on models.py
PLAYER_TYPES = {
    "BAT": "Batsman",
    "BOWL": "Bowler",
    "AR": "All-Rounder",  # Updated from ALL to AR
    "WK": "Wicket Keeper",
}


# Add new constants for multi-select and multi-remove
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
        return await show_all_players(update, context)
    elif callback_data == SQUAD_MENU.VIEW_SQUAD or callback_data == "view_squad":
        return await view_squad(update, context)
    elif callback_data == SQUAD_MENU.SUBMIT_SQUAD or callback_data == "submit_squad":
        return await confirm_submission(update, context)
    elif (
        callback_data == SQUAD_MENU.START_BUILDING
        or callback_data == "start_building_squad"
    ):
        return await show_all_players(update, context)
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

    Args:
        update: Update object
        context: Context object

    Returns:
        Next conversation state
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

    # Try to get current squad
    squad_client = await get_squad_client()
    squad = await squad_client.get_draft_squad(participant_id)

    # Check if squad exists
    has_squad = squad is not None and isinstance(squad, dict) and "players" in squad
    player_count = len(squad.get("players", [])) if has_squad else 0

    # Create keyboard
    keyboard = []

    if has_squad:
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

    return SHOW_SQUAD_MENU


@log_function_call
async def view_squad(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    View the user's draft squad with cached data when possible.
    """
    query = update.callback_query
    if query:
        await query.answer()

    participant_id = context.user_data.get("participant_id")
    if not participant_id:
        logger.error("No participant ID found in context")
        if query:
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

    # Show loading message
    if query:
        await query.edit_message_text(
            "Loading your squad...\n\n" "This may take a moment. Please wait.",
            parse_mode="Markdown",
        )

    # Get the user's draft squad - make API call only if needed
    squad_client = await get_squad_client()

    # We need fresh squad data here to show the current state
    squad_data = await squad_client.get_draft_squad(participant_id)

    # Update cached squad data
    context.user_data["cached_squad"] = squad_data if squad_data else {"players": []}

    if not squad_data or not squad_data.get("players"):
        # No squad or empty squad
        message = (
            "You don't have any players in your squad yet.\n\n"
            "Let's start by adding some players to your squad!"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "🔍 Find Players", callback_data=SQUAD_MENU.ADD_PLAYERS
                ),
                InlineKeyboardButton(
                    "⬅️ Back to Menu", callback_data=SQUAD_MENU.BACK_TO_MENU
                ),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        if query:
            await query.edit_message_text(message, reply_markup=reply_markup)
        else:
            await update.message.reply_text(message, reply_markup=reply_markup)

        return VIEW_SQUAD

    # Calculate budget and player count
    total_budget = 120.0  # Default budget
    used_budget = 0.0
    players = squad_data["players"]
    player_count = len(players)

    # Calculate used budget - directly use the data from API
    for player in players:
        if "player" in player and "base_price" in player["player"]:
            try:
                used_budget += float(player["player"]["base_price"])
            except (ValueError, TypeError):
                logger.warning(f"Invalid base_price for player: {player}")

    remaining_budget = total_budget - used_budget

    # Create the message
    message = (
        "👥 *Your Squad*\n\n"
        f"Players: {player_count}/18\n"
        f"Budget: {used_budget:.1f}/{total_budget:.1f} Cr (Remaining: {remaining_budget:.1f} Cr)\n\n"
    )

    # Add submission status
    if player_count >= 15 and player_count <= 18:
        message += "✅ You have enough players to submit your squad.\n\n"
    else:
        message += f"❌ You need between 15-18 players to submit your squad. Currently: {player_count}\n\n"

    message += "Players in your squad:\n\n"

    # List all players directly from API without grouping
    for i, player in enumerate(players):
        player_data = player.get("player", {})
        player_name = player_data.get("name", "Unknown")
        player_team = player_data.get("team", "Unknown")
        player_price = player_data.get("base_price", "0.0")
        player_type = player_data.get("player_type", "Unknown")

        # Map player type to readable format using the updated PLAYER_TYPES mapping
        readable_type = PLAYER_TYPES.get(player_type, player_type)

        message += f"{i+1}. {player_name} ({player_team}) - {readable_type} - {player_price} Cr\n"

    # Create the keyboard
    keyboard = []

    # Add multi-remove option
    keyboard.append(
        [
            InlineKeyboardButton(
                "🗑️ Remove Multiple Players", callback_data=MULTI_REMOVE.MULTI_REMOVE
            )
        ]
    )

    # Add navigation buttons
    keyboard.append(
        [
            InlineKeyboardButton(
                "🔍 Add More Players", callback_data=SQUAD_MENU.ADD_PLAYERS
            ),
            InlineKeyboardButton(
                "📤 Submit Squad", callback_data=SQUAD_MENU.SUBMIT_SQUAD
            ),
        ]
    )

    # Add back button
    keyboard.append(
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data=SQUAD_MENU.BACK_TO_MENU)]
    )

    reply_markup = InlineKeyboardMarkup(keyboard)

    if query:
        await query.edit_message_text(
            message, reply_markup=reply_markup, parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            message, reply_markup=reply_markup, parse_mode="Markdown"
        )

    return VIEW_SQUAD


@log_function_call
async def confirm_submission(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Confirm squad submission.

    Args:
        update: Update object
        context: Context object

    Returns:
        Next conversation state
    """
    query = update.callback_query
    await query.answer()

    # Get participant ID from context
    participant_id = context.user_data.get("participant_id")

    # Get the user's draft squad
    squad_client = await get_squad_client()
    squad_data = await squad_client.get_draft_squad(participant_id)

    # Check if squad exists
    if not squad_data or not squad_data.get("players"):
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
        return SHOW_SQUAD_MENU

    # Calculate budget and player count
    total_budget = 120.0  # Default budget
    used_budget = 0.0
    players = squad_data["players"]
    player_count = len(players)

    # Calculate used budget
    for player in players:
        if "player" in player and "base_price" in player["player"]:
            used_budget += float(player["player"]["base_price"])

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
                            "🔍 Add More Players", callback_data=PLAYER_FILTER.BACK
                        ),
                        InlineKeyboardButton(
                            "⬅️ Back to Menu", callback_data=SQUAD_MENU.BACK_TO_MENU
                        ),
                    ]
                ]
            ),
        )
        return HANDLE_PLAYER_SELECTION

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
        return HANDLE_PLAYER_SELECTION

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
        return HANDLE_PLAYER_SELECTION

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

    return CONFIRM_SQUAD_SUBMISSION


@log_function_call
async def handle_multi_select_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle callbacks from multi-select mode with optimized API usage.
    Only makes API calls when the user confirms their selection.
    """
    query = update.callback_query
    await query.answer()

    callback_data = query.data

    # Ignore header callbacks
    if callback_data.startswith("header_") or callback_data == "page_info":
        return HANDLE_MULTI_SELECT

    if callback_data == MULTI_SELECT.CONFIRM_MULTI_SELECT:
        # Add all selected players to draft in a single API call
        participant_id = context.user_data.get("participant_id")
        selected_players = context.user_data.get("multi_select_players", [])

        if not selected_players:
            await query.edit_message_text(
                "No new players selected. Your squad already has players.\n\n"
                "What would you like to do?",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Select More Players",
                                callback_data=SQUAD_MENU.ADD_PLAYERS,
                            ),
                            InlineKeyboardButton(
                                "View Squad", callback_data=SQUAD_MENU.VIEW_SQUAD
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                "Back to Menu", callback_data=SQUAD_MENU.BACK_TO_MENU
                            )
                        ],
                    ]
                ),
            )
            return SHOW_SQUAD_MENU

        # Show a loading message
        await query.edit_message_text(
            f"Adding {len(selected_players)} players to your squad...\n\n"
            "This may take a moment. Please wait.",
            parse_mode="Markdown",
        )

        # Add players to draft in a single API call
        squad_client = await get_squad_client()
        try:
            # Use the batch add method
            result = await squad_client.add_multiple_players_to_draft(
                participant_id, selected_players
            )

            if result.get("success"):
                logger.info(
                    f"Successfully added {len(selected_players)} players to squad"
                )

                # Clear multi-select list
                context.user_data["multi_select_players"] = []

                # Update cached squad
                squad = await squad_client.get_draft_squad(participant_id)
                context.user_data["cached_squad"] = squad if squad else {"players": []}

                # Show success message
                await query.edit_message_text(
                    f"✅ Added {len(selected_players)} players to your squad.\n\n"
                    "What would you like to do next?",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "👥 View Squad", callback_data=SQUAD_MENU.VIEW_SQUAD
                                ),
                                InlineKeyboardButton(
                                    "📤 Submit Squad",
                                    callback_data=SQUAD_MENU.SUBMIT_SQUAD,
                                ),
                            ],
                            [
                                InlineKeyboardButton(
                                    "⬅️ Back to Menu",
                                    callback_data=SQUAD_MENU.BACK_TO_MENU,
                                )
                            ],
                        ]
                    ),
                )
            else:
                error_message = result.get("error", "Unknown error")
                logger.error(f"Failed to add players: {error_message}")

                await query.edit_message_text(
                    f"❌ Failed to add players: {error_message}\n\n"
                    "Please try again.",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Try Again",
                                    callback_data=MULTI_SELECT.CONFIRM_MULTI_SELECT,
                                ),
                                InlineKeyboardButton(
                                    "⬅️ Back to Menu",
                                    callback_data=SQUAD_MENU.BACK_TO_MENU,
                                ),
                            ],
                        ]
                    ),
                )
        except Exception as e:
            logger.exception(f"Error adding players: {str(e)}")

            await query.edit_message_text(
                f"❌ Error adding players: {str(e)}\n\n" "Please try again.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Try Again",
                                callback_data=MULTI_SELECT.CONFIRM_MULTI_SELECT,
                            ),
                            InlineKeyboardButton(
                                "⬅️ Back to Menu", callback_data=SQUAD_MENU.BACK_TO_MENU
                            ),
                        ],
                    ]
                ),
            )

        return SHOW_SQUAD_MENU

    elif callback_data == MULTI_SELECT.CANCEL_MULTI_SELECT:
        # Clear multi-select list
        context.user_data["multi_select_players"] = []

        # Remove the reply keyboard if it exists
        reply_markup = ReplyKeyboardRemove()
        await query.message.reply_text(
            "Selection cancelled.", reply_markup=reply_markup
        )

        # Go back to squad menu
        return await show_squad_menu(update, context)
    elif callback_data == SQUAD_MENU.VIEW_SQUAD:
        # Remove the reply keyboard if it exists
        reply_markup = ReplyKeyboardRemove()
        await query.message.reply_text("Viewing squad...", reply_markup=reply_markup)

        return await view_squad(update, context)
    elif callback_data == SQUAD_MENU.BACK_TO_MENU:
        # Remove the reply keyboard if it exists
        reply_markup = ReplyKeyboardRemove()
        await query.message.reply_text(
            "Returning to menu...", reply_markup=reply_markup
        )

        return await show_squad_menu(update, context)

    return HANDLE_MULTI_SELECT


@log_function_call
async def handle_view_squad_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle callbacks from the view squad screen.

    Args:
        update: Update object
        context: Context object

    Returns:
        Next conversation state
    """
    query = update.callback_query
    await query.answer()

    callback_data = query.data

    if callback_data == MULTI_REMOVE.MULTI_REMOVE:
        # Initialize multi-remove mode
        context.user_data["multi_remove_players"] = []
        return await show_multi_remove(update, context)
    elif callback_data == PLAYER_FILTER.BACK:
        return await show_all_players(update, context)
    elif callback_data == SQUAD_MENU.SUBMIT_SQUAD:
        return await confirm_submission(update, context)
    elif callback_data == SQUAD_MENU.BACK_TO_MENU:
        return await show_squad_menu(update, context)
    else:
        # Unknown callback, go back to view squad
        return await view_squad(update, context)


@log_function_call
async def show_multi_remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Show multi-remove interface for removing multiple players at once.

    Args:
        update: Update object
        context: Context object

    Returns:
        Next conversation state
    """
    query = update.callback_query
    await query.answer()

    # Get participant ID from context
    participant_id = context.user_data.get("participant_id")

    # Get the user's draft squad
    squad_client = await get_squad_client()
    squad_data = await squad_client.get_draft_squad(participant_id)

    if not squad_data or not squad_data.get("players"):
        # No squad or empty squad
        await query.edit_message_text(
            "You don't have any players in your squad to remove.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🔍 Find Players", callback_data=PLAYER_FILTER.BACK
                        ),
                        InlineKeyboardButton(
                            "⬅️ Back to Menu", callback_data=SQUAD_MENU.BACK_TO_MENU
                        ),
                    ]
                ]
            ),
        )
        return VIEW_SQUAD

    # Initialize multi-remove if not already done
    if "multi_remove_players" not in context.user_data:
        context.user_data["multi_remove_players"] = []

    # Create message
    message = "🗑️ *Select Players to Remove*\n\n"
    message += f"Currently selected for removal: {len(context.user_data['multi_remove_players'])}\n\n"
    message += "Select players to remove from your squad:\n\n"

    # Create keyboard with all players in squad
    keyboard = []
    players = squad_data["players"]

    for player in players:
        player_data = player.get("player", {})
        player_id = player.get("player_id")
        player_name = player_data.get("name", "Unknown")
        player_team = player_data.get("team", "Unknown")
        player_price = player_data.get("base_price", "0.0")
        player_type = player_data.get("player_type", "Unknown")

        # Check if selected for removal
        is_selected = player_id in context.user_data["multi_remove_players"]

        if is_selected:
            button_text = (
                f"☑️ {player_name} ({player_team}) - {player_type} - {player_price} Cr"
            )
        else:
            button_text = (
                f"⬜ {player_name} ({player_team}) - {player_type} - {player_price} Cr"
            )

        keyboard.append(
            [
                InlineKeyboardButton(
                    button_text,
                    callback_data=f"{MULTI_REMOVE.TOGGLE_REMOVE} {player_id}",
                )
            ]
        )

    # Add confirm and cancel buttons
    keyboard.append(
        [
            InlineKeyboardButton(
                "✅ Confirm Removal", callback_data=MULTI_REMOVE.CONFIRM_MULTI_REMOVE
            ),
            InlineKeyboardButton(
                "❌ Cancel", callback_data=MULTI_REMOVE.CANCEL_MULTI_REMOVE
            ),
        ]
    )

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        message, reply_markup=reply_markup, parse_mode="Markdown"
    )

    return HANDLE_MULTI_REMOVE


@log_function_call
async def handle_multi_remove_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle callbacks from multi-remove mode.

    Args:
        update: Update object
        context: Context object

    Returns:
        Next conversation state
    """
    query = update.callback_query
    await query.answer()

    callback_data = query.data

    if callback_data.startswith(MULTI_REMOVE.TOGGLE_REMOVE):
        # Extract player ID
        player_id = int(callback_data.split(" ")[1])

        # Toggle selection
        if "multi_remove_players" not in context.user_data:
            context.user_data["multi_remove_players"] = []

        if player_id in context.user_data["multi_remove_players"]:
            context.user_data["multi_remove_players"].remove(player_id)
        else:
            context.user_data["multi_remove_players"].append(player_id)

        # Refresh the multi-remove UI
        return await show_multi_remove(update, context)
    elif callback_data == MULTI_REMOVE.CONFIRM_MULTI_REMOVE:
        # Remove all selected players from draft
        participant_id = context.user_data.get("participant_id")
        selected_players = context.user_data.get("multi_remove_players", [])

        if not selected_players:
            await query.edit_message_text(
                "No players selected for removal.\n\n" "What would you like to do?",
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
            return VIEW_SQUAD

        # Show a loading message
        await query.edit_message_text(
            f"Removing {len(selected_players)} players from your squad...\n\n"
            "This may take a moment. Please wait.",
            parse_mode="Markdown",
        )

        # Remove players from draft
        squad_client = await get_squad_client()
        success_count = 0
        error_messages = []

        for player_id in selected_players:
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

        # Clear multi-remove list
        context.user_data["multi_remove_players"] = []

        # Update cached squad
        squad = await squad_client.get_draft_squad(participant_id)
        context.user_data["cached_squad"] = squad if squad else {"players": []}

        # Show result message
        if success_count == len(selected_players):
            await query.edit_message_text(
                f"✅ Successfully removed {success_count} players from your squad.\n\n"
                "What would you like to do next?",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "👥 View Squad", callback_data=SQUAD_MENU.VIEW_SQUAD
                            ),
                            InlineKeyboardButton(
                                "🔍 Add Players", callback_data=SQUAD_MENU.ADD_PLAYERS
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                "⬅️ Back to Menu", callback_data=SQUAD_MENU.BACK_TO_MENU
                            )
                        ],
                    ]
                ),
            )
        else:
            error_text = "\n".join(error_messages[:5])
            if len(error_messages) > 5:
                error_text += f"\n...and {len(error_messages) - 5} more errors."

            await query.edit_message_text(
                f"⚠️ Removed {success_count} out of {len(selected_players)} players.\n\n"
                f"Errors:\n{error_text}\n\n"
                "What would you like to do next?",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "👥 View Squad", callback_data=SQUAD_MENU.VIEW_SQUAD
                            ),
                            InlineKeyboardButton(
                                "🔍 Add Players", callback_data=SQUAD_MENU.ADD_PLAYERS
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                "⬅️ Back to Menu", callback_data=SQUAD_MENU.BACK_TO_MENU
                            )
                        ],
                    ]
                ),
            )

        return SHOW_SQUAD_MENU

    elif callback_data == MULTI_REMOVE.CANCEL_MULTI_REMOVE:
        # Clear multi-remove list
        context.user_data["multi_remove_players"] = []

        # Go back to view squad
        return await view_squad(update, context)
    else:
        # Unknown callback, go back to view squad
        return await view_squad(update, context)


@log_function_call
async def handle_submission_confirmation(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle confirmation of squad submission.

    Args:
        update: Update object
        context: Context object

    Returns:
        Next conversation state
    """
    query = update.callback_query
    await query.answer()

    callback_data = query.data

    if callback_data == CONFIRM_SUBMISSION.CONFIRM:
        # Submit the squad
        participant_id = context.user_data.get("participant_id")

        # Show a loading message
        await query.edit_message_text(
            "Submitting your squad...\n\n" "This may take a moment. Please wait.",
            parse_mode="Markdown",
        )

        # Submit the squad
        squad_client = await get_squad_client()
        try:
            result = await squad_client.submit_draft_squad(participant_id)

            if result.get("success"):
                # Show success message
                await query.edit_message_text(
                    "✅ *Squad Submitted Successfully!*\n\n"
                    "Your squad has been submitted and is now locked for the tournament.\n\n"
                    "Good luck!",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "⬅️ Back to Main Menu", callback_data="main_menu"
                                )
                            ]
                        ]
                    ),
                    parse_mode="Markdown",
                )
            else:
                error_message = result.get("error", "Unknown error")
                logger.error(f"Failed to submit squad: {error_message}")

                await query.edit_message_text(
                    f"❌ Failed to submit squad: {error_message}\n\n"
                    "Please try again.",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Try Again", callback_data=SQUAD_MENU.SUBMIT_SQUAD
                                ),
                                InlineKeyboardButton(
                                    "⬅️ Back to Menu",
                                    callback_data=SQUAD_MENU.BACK_TO_MENU,
                                ),
                            ],
                        ]
                    ),
                )
        except Exception as e:
            logger.exception(f"Error submitting squad: {str(e)}")

            await query.edit_message_text(
                f"❌ Error submitting squad: {str(e)}\n\n" "Please try again.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Try Again", callback_data=SQUAD_MENU.SUBMIT_SQUAD
                            ),
                            InlineKeyboardButton(
                                "⬅️ Back to Menu", callback_data=SQUAD_MENU.BACK_TO_MENU
                            ),
                        ],
                    ]
                ),
            )

        return ConversationHandler.END
    elif callback_data == CONFIRM_SUBMISSION.CANCEL:
        # Cancel submission
        await query.edit_message_text(
            "Squad submission cancelled.\n\n" "What would you like to do next?",
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
        return SHOW_SQUAD_MENU
    else:
        # Unknown callback, go back to confirmation
        return await confirm_submission(update, context)


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

    # Check if the user has a squad
    squad_client = await get_squad_client()
    squad_data = await squad_client.get_draft_squad(participant_id)

    if squad_data and "players" in squad_data and squad_data["players"]:
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
async def show_all_players(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Show all players with a scrollable interface using ReplyKeyboardMarkup.
    Fetches all players at once and caches them to minimize API calls.
    """
    query = update.callback_query
    if query:
        await query.answer()
        message = query.message
    else:
        message = update.message

    # Get user and participant data
    user_id, participant_id = await get_user_participant_data(update, context)
    if not participant_id:
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

    # Show loading message
    loading_message = await message.reply_text(
        "Loading players...\n\n" "This may take a moment. Please wait.",
        parse_mode="Markdown",
    )

    # Initialize multi-select if not already done
    if "multi_select_players" not in context.user_data:
        context.user_data["multi_select_players"] = []

    # Get all players - fetch once and cache
    squad_client = await get_squad_client()

    try:
        # Get current squad to know which players are already selected
        current_squad = await squad_client.get_draft_squad(participant_id)
        context.user_data["cached_squad"] = (
            current_squad if current_squad else {"players": []}
        )

        # Get all available players
        all_players = await squad_client.get_available_players(limit=1000)

        # Cache the players
        context.user_data["cached_players"] = all_players

        # Extract player IDs already in squad
        squad_player_ids = []
        if current_squad and "players" in current_squad:
            squad_player_ids = [
                p.get("player_id") for p in current_squad.get("players", [])
            ]

        # Organize players by type
        players_by_type = {
            "BAT": [],
            "BOWL": [],
            "AR": [],
            "WK": [],
        }

        for player in all_players:
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

            # Check if already in squad or selected
            in_squad = player_id in squad_player_ids
            is_selected = player_id in context.user_data["multi_select_players"]

            if in_squad:
                prefix = "✅"  # Already in squad
            elif is_selected:
                prefix = "☑️"  # Selected but not yet added
            else:
                prefix = "⬜"  # Not selected

            button_text = f"{prefix} {player_name} ({player_team}) - {player_price} Cr"
            keyboard.append([button_text])

        # Add header for bowlers
        keyboard.append(["🎯 BOWLERS 🎯"])

        # Add bowlers
        for player in players_by_type["BOWL"]:
            player_id = player.get("id")
            player_name = player.get("name", "Unknown")
            player_team = player.get("team", "Unknown")
            player_price = player.get("base_price", "0.0")

            # Check if already in squad or selected
            in_squad = player_id in squad_player_ids
            is_selected = player_id in context.user_data["multi_select_players"]

            if in_squad:
                prefix = "✅"  # Already in squad
            elif is_selected:
                prefix = "☑️"  # Selected but not yet added
            else:
                prefix = "⬜"  # Not selected

            button_text = f"{prefix} {player_name} ({player_team}) - {player_price} Cr"
            keyboard.append([button_text])

        # Add header for all-rounders
        keyboard.append(["🏏🎯 ALL-ROUNDERS 🏏🎯"])

        # Add all-rounders
        for player in players_by_type["AR"]:
            player_id = player.get("id")
            player_name = player.get("name", "Unknown")
            player_team = player.get("team", "Unknown")
            player_price = player.get("base_price", "0.0")

            # Check if already in squad or selected
            in_squad = player_id in squad_player_ids
            is_selected = player_id in context.user_data["multi_select_players"]

            if in_squad:
                prefix = "✅"  # Already in squad
            elif is_selected:
                prefix = "☑️"  # Selected but not yet added
            else:
                prefix = "⬜"  # Not selected

            button_text = f"{prefix} {player_name} ({player_team}) - {player_price} Cr"
            keyboard.append([button_text])

        # Add header for wicket-keepers
        keyboard.append(["🧤 WICKET-KEEPERS 🧤"])

        # Add wicket-keepers
        for player in players_by_type["WK"]:
            player_id = player.get("id")
            player_name = player.get("name", "Unknown")
            player_team = player.get("team", "Unknown")
            player_price = player.get("base_price", "0.0")

            # Check if already in squad or selected
            in_squad = player_id in squad_player_ids
            is_selected = player_id in context.user_data["multi_select_players"]

            if in_squad:
                prefix = "✅"  # Already in squad
            elif is_selected:
                prefix = "☑️"  # Selected but not yet added
            else:
                prefix = "⬜"  # Not selected

            button_text = f"{prefix} {player_name} ({player_team}) - {player_price} Cr"
            keyboard.append([button_text])

        # Create the reply keyboard markup
        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=False,
            selective=True,
        )

        # Calculate counts
        total_players = len(all_players)
        selected_count = len(context.user_data["multi_select_players"])
        squad_count = len(squad_player_ids)

        # Create the message
        message_text = (
            "🏏 *Select Players for Your Squad*\n\n"
            f"Current squad: {squad_count}/18 players\n"
            f"Selected: {selected_count} new players\n\n"
            "Tap on a player to select/deselect them for your squad.\n"
            "Players with ✅ are already in your squad.\n"
            "Players with ☑️ are selected but not yet added.\n\n"
            "When you're done selecting, use the buttons below to confirm or cancel."
        )

        # Delete the loading message
        await loading_message.delete()

        # Send the message with the reply keyboard
        sent_message = await message.reply_text(
            message_text,
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )

        # Store the message ID for later reference
        context.user_data["player_selection_message_id"] = sent_message.message_id

        # Send control buttons as a separate message with inline keyboard
        control_keyboard = [
            [
                InlineKeyboardButton(
                    "✅ Confirm Selection",
                    callback_data=MULTI_SELECT.CONFIRM_MULTI_SELECT,
                ),
                InlineKeyboardButton(
                    "❌ Cancel", callback_data=MULTI_SELECT.CANCEL_MULTI_SELECT
                ),
            ],
            [
                InlineKeyboardButton(
                    "👥 View Squad", callback_data=SQUAD_MENU.VIEW_SQUAD
                ),
                InlineKeyboardButton(
                    "⬅️ Back to Menu", callback_data=SQUAD_MENU.BACK_TO_MENU
                ),
            ],
        ]

        control_markup = InlineKeyboardMarkup(control_keyboard)

        await message.reply_text(
            "Use these buttons to confirm your selection or navigate:",
            reply_markup=control_markup,
        )

        # Register a message handler for player selection
        context.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                handle_player_selection_message,
            ),
            group=1,
        )

        return HANDLE_MULTI_SELECT

    except Exception as e:
        logger.exception(f"Error showing players: {str(e)}")

        # Delete the loading message
        await loading_message.delete()

        await message.reply_text(
            f"❌ Error loading players: {str(e)}\n\n" "Please try again later.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "⬅️ Back to Menu", callback_data=SQUAD_MENU.BACK_TO_MENU
                        )
                    ]
                ]
            ),
        )

        return SHOW_SQUAD_MENU


@log_function_call
async def handle_player_selection_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle player selection from the reply keyboard.
    """
    message_text = update.message.text

    # Ignore header rows
    if (
        message_text.startswith("🏏 BATSMEN")
        or message_text.startswith("🎯 BOWLERS")
        or message_text.startswith("🏏🎯 ALL-ROUNDERS")
        or message_text.startswith("🧤 WICKET-KEEPERS")
    ):
        return HANDLE_MULTI_SELECT

    # Extract player info from the message
    parts = message_text.split(" ", 1)
    if len(parts) < 2:
        return HANDLE_MULTI_SELECT

    prefix = parts[0]
    player_info = parts[1]

    # Find the player in cached data
    cached_players = context.user_data.get("cached_players", [])
    selected_player = None

    for player in cached_players:
        player_name = player.get("name", "Unknown")
        player_team = player.get("team", "Unknown")

        # Check if this player matches the selected one
        if f"{player_name} ({player_team})" in player_info:
            selected_player = player
            break

    if not selected_player:
        await update.message.reply_text(
            "❌ Could not find the selected player in the database.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "⬅️ Back to Menu", callback_data=SQUAD_MENU.BACK_TO_MENU
                        )
                    ]
                ]
            ),
        )
        return HANDLE_MULTI_SELECT

    player_id = selected_player.get("id")
    player_name = selected_player.get("name", "Unknown")

    # Get current squad player IDs
    current_squad = context.user_data.get("cached_squad", {"players": []})
    squad_player_ids = [p.get("player_id") for p in current_squad.get("players", [])]

    # Check if player is already in squad
    if player_id in squad_player_ids:
        await update.message.reply_text(
            f"ℹ️ {player_name} is already in your squad. To remove players, use the 'View Squad' option.",
        )
        return HANDLE_MULTI_SELECT

    # Toggle selection
    if "multi_select_players" not in context.user_data:
        context.user_data["multi_select_players"] = []

    if player_id in context.user_data["multi_select_players"]:
        context.user_data["multi_select_players"].remove(player_id)
        await update.message.reply_text(f"❌ Removed {player_name} from selection.")
    else:
        context.user_data["multi_select_players"].append(player_id)
        await update.message.reply_text(f"✅ Added {player_name} to selection.")

    # Update the selection count
    selected_count = len(context.user_data["multi_select_players"])
    squad_count = len(squad_player_ids)

    # Update the message with the new count
    message_text = (
        "🏏 *Select Players for Your Squad*\n\n"
        f"Current squad: {squad_count}/18 players\n"
        f"Selected: {selected_count} new players\n\n"
        "Tap on a player to select/deselect them for your squad.\n"
        "Players with ✅ are already in your squad.\n"
        "Players with ☑️ are selected but not yet added.\n\n"
        "When you're done selecting, use the buttons below to confirm or cancel."
    )

    # Try to edit the original message if we have its ID
    message_id = context.user_data.get("player_selection_message_id")
    if message_id:
        try:
            await context.bot.edit_message_text(
                message_text,
                chat_id=update.effective_chat.id,
                message_id=message_id,
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.warning(f"Could not edit message: {str(e)}")

    return HANDLE_MULTI_SELECT


@log_function_call
async def register_squad_handlers(application):
    """Register squad handlers."""
    # Add direct handlers for specific patterns outside the conversation
    application.add_handler(
        CallbackQueryHandler(my_squad_entry, pattern="^menu_my_squad$")
    )
    application.add_handler(CallbackQueryHandler(view_squad, pattern="^squad_view$"))

    # Add the squad entry point handler for other squad-related patterns
    application.add_handler(CallbackQueryHandler(squad_entry_point, pattern="^squad_"))

    # Add the main squad conversation handler
    squad_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(squad_entry_point, pattern="^squad_"),
            CallbackQueryHandler(my_squad_entry, pattern="^menu_my_squad$"),
            CallbackQueryHandler(squad_entry_point, pattern="^start_building_squad$"),
        ],
        states={
            SHOW_SQUAD_MENU: [
                CallbackQueryHandler(squad_entry_point),
            ],
            HANDLE_MULTI_SELECT: [
                CallbackQueryHandler(handle_multi_select_callback),
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, handle_player_selection_message
                ),
            ],
            VIEW_SQUAD: [
                CallbackQueryHandler(handle_view_squad_callback),
            ],
            HANDLE_MULTI_REMOVE: [
                CallbackQueryHandler(handle_multi_remove_callback),
            ],
            CONFIRM_SQUAD_SUBMISSION: [
                CallbackQueryHandler(handle_submission_confirmation),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(
                lambda u, c: ConversationHandler.END, pattern="^cancel$"
            )
        ],
        name="squad_conversation",
        persistent=False,
    )

    application.add_handler(squad_conv_handler)
    logger.info("Squad handlers registered successfully")
