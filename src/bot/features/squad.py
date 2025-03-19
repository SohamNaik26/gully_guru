"""
Squad management features for the GullyGuru bot.
Handles squad viewing, editing, and submission.
"""

import logging
import json
from typing import Dict, Any, Optional, List
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters,
)

# Use the centralized client initialization
from src.bot.api_client.init import (
    get_initialized_onboarding_client,
    get_initialized_squad_client,
    wait_for_api,
)
from src.bot.context import manager as ctx_manager

# Use the utility function
from src.bot.utils.callbacks import create_feature_callback_data

# Configure logging
logger = logging.getLogger(__name__)

# Conversation states
SELECTING_PLAYERS = 1

# Constants
SQUAD_SIZE = 18
PLAYERS_PER_PAGE = 10  # Show 10 players per page
PAGE_KEY = "player_page"  # Key for storing current page in context


def create_callback_data(action: str, data: Dict[str, Any] = None) -> str:
    """Create a callback data string with action and optional data."""
    return create_feature_callback_data("squad", action, data)


def parse_callback_data(callback_data: str) -> Dict[str, Any]:
    """Parse callback data string into a dictionary."""
    try:
        return json.loads(callback_data)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse callback data: {callback_data}")
        return {"a": "unknown"}


async def get_player_inline_keyboard(
    players: List[Dict[str, Any]], selected_ids: List[int], page: int = 0
) -> InlineKeyboardMarkup:
    """Create an inline keyboard with player buttons and pagination."""
    keyboard = []

    # Calculate total pages
    total_players = len(players)
    total_pages = (total_players + PLAYERS_PER_PAGE - 1) // PLAYERS_PER_PAGE

    # Get players for current page
    start_idx = page * PLAYERS_PER_PAGE
    end_idx = min(start_idx + PLAYERS_PER_PAGE, total_players)
    page_players = players[start_idx:end_idx]

    # Add player buttons (one per row)
    for player in page_players:
        is_selected = player["id"] in selected_ids
        status = "✅" if is_selected else ""
        name = player["name"]
        team = player["team"]
        price = player.get("base_price", 0)

        button_text = f"🏏 {name} - {team} - {price} Cr {status}"
        callback_data = create_callback_data("toggle", {"id": player["id"]})

        keyboard.append(
            [InlineKeyboardButton(button_text, callback_data=callback_data)]
        )

    # Add navigation row
    nav_row = []

    # Add page indicator in the middle
    page_text = f"Page {page+1}/{total_pages}"

    if page > 0:
        nav_row.append(
            InlineKeyboardButton(
                "⬅️ Previous", callback_data=create_callback_data("prev")
            )
        )

    nav_row.append(
        InlineKeyboardButton(page_text, callback_data=create_callback_data("page"))
    )

    if page < total_pages - 1:
        nav_row.append(
            InlineKeyboardButton("Next ➡️", callback_data=create_callback_data("next"))
        )

    if nav_row:
        keyboard.append(nav_row)

    # Add submit button
    keyboard.append(
        [
            InlineKeyboardButton(
                "✅ Submit Squad", callback_data=create_callback_data("submit")
            )
        ]
    )

    return InlineKeyboardMarkup(keyboard)


async def squad_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> Optional[int]:
    """
    Handle the /squad command.
    This command allows participants to view and edit their squad during the draft phase,
    and only view during other phases like auction.
    """
    logger.info(f"Squad: Command called by user {update.effective_user.id}")

    # Check if API is available
    if not await wait_for_api():
        await update.message.reply_text(
            "⚠️ The GullyGuru service is currently unavailable. Please try again later."
        )
        return ConversationHandler.END

    # Get the telegram user
    telegram_user_id = update.effective_user.id

    try:
        # Get user from database
        client = await get_initialized_onboarding_client()
        db_user = await client.get_user_by_telegram_id(telegram_user_id)

        if not db_user:
            await update.message.reply_text(
                "⚠️ Your account was not found. Please use /start to register."
            )
            return ConversationHandler.END

        user_id = db_user["id"]

        # Get user's active gully from context
        active_gully_id = ctx_manager.get_active_gully_id(context)

        # If no active gully set, get available gullies and prompt to select one
        if not active_gully_id:
            # Get user's gullies
            user_gullies = await client.get_user_gullies(user_id)

            if not user_gullies:
                await update.message.reply_text(
                    "⚠️ You are not a participant in any gully."
                )
                return ConversationHandler.END

            # If only one gully, set it as active
            if len(user_gullies) == 1:
                active_gully_id = user_gullies[0]["id"]
                ctx_manager.set_active_gully_id(context, active_gully_id)
            else:
                # Multiple gullies, prompt to select one
                return await show_gully_selection(update, context, user_gullies)

        # Get the gully info
        gully = await client.get_gully(active_gully_id)

        if not gully:
            await update.message.reply_text(
                "⚠️ Failed to retrieve information for the selected gully."
            )
            return ConversationHandler.END

        gully_name = gully.get("name", "Unknown Gully")
        gully_status = gully.get("status", "unknown").lower()

        logger.info(
            f"Processing squad for gully: {gully_name} (status: {gully_status})"
        )

        # Get participant info
        participant = await client.get_participant_by_user_and_gully(
            user_id=user_id, gully_id=active_gully_id
        )

        if not participant:
            await update.message.reply_text(
                "⚠️ You are not registered as a participant in the selected gully."
            )
            return ConversationHandler.END

        participant_id = participant["id"]
        team_name = participant.get("team_name", "Your Team")

        # Store important IDs in context
        ctx_manager.set_participant_id(context, participant_id, active_gully_id)
        ctx_manager.set_team_name(context, team_name, active_gully_id)

        # Check if squad selection is allowed for editing based on gully status
        edit_allowed_states = ["draft"]  # Only allow editing in draft state
        view_only_mode = gully_status not in edit_allowed_states

        # If view-only mode, inform the user to use /my_team command instead
        if view_only_mode:
            await update.message.reply_text(
                f"⚠️ Squad selection is only available during the draft phase.\n\n"
                f"The current phase for {gully_name} is: {gully_status}.\n\n"
                f"Please use /my_team to view the players you currently own."
            )
            return ConversationHandler.END

        # For draft state, continue with the normal squad selection flow
        # Get all available players for this gully
        await update.message.reply_text(
            f"Loading available players for {gully_name}..."
        )

        return SELECTING_PLAYERS

    except Exception as e:
        logger.error(f"Error in squad_command: {e}")
        logger.exception("Detailed error traceback:")
        await update.message.reply_text(
            "⚠️ Something went wrong while retrieving your squad information. Please try again later."
        )
        return ConversationHandler.END


async def show_player_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Show the player selection interface with pagination using inline keyboard."""
    logger.info("show_player_selection called")

    # Get current page from context or default to 0
    current_page = context.user_data.get(PAGE_KEY, 0)
    logger.info(f"Current page: {current_page}")

    # Get active gully ID
    active_gully_id = ctx_manager.get_active_gully_id(context)

    # Get all available players
    # Note: We store this in user_data rather than gully-specific context
    # because player data is common across all gullies and can be reused
    all_players = context.user_data.get(f"all_players_{active_gully_id}")
    if not all_players:
        squad_client = await get_initialized_squad_client()
        all_players = await squad_client.get_available_players(max_players=250)
        context.user_data[f"all_players_{active_gully_id}"] = all_players
        logger.info(
            f"Fetched {len(all_players)} available players for gully {active_gully_id}"
        )

    if not all_players:
        logger.warning("No players available")
        message = (
            "⚠️ No players available. Please try again later.\n\n"
            "This could be due to a temporary issue with the player database."
        )

        if isinstance(update, Update) and update.callback_query:
            await update.callback_query.edit_message_text(message)
        else:
            await update.message.reply_text(message)
        return ConversationHandler.END

    # Get selected player IDs from gully-specific context
    selected_player_ids = ctx_manager.get_selected_player_ids(context, active_gully_id)
    logger.info(f"Currently selected: {len(selected_player_ids)} players")

    # Create a dictionary of player details by ID for quick lookup
    player_dict = {player["id"]: player for player in all_players}

    # Get details of selected players
    selected_players = []
    for player_id in selected_player_ids:
        if player_id in player_dict:
            selected_players.append(player_dict[player_id])

    # Create inline keyboard with players for the current page
    reply_markup = await get_player_inline_keyboard(
        all_players, selected_player_ids, page=current_page
    )

    # Build message text with current squad details
    message_text = (
        f"Select your squad (exactly {SQUAD_SIZE} players required).\n\n"
        f"Currently selected: {len(selected_player_ids)}/{SQUAD_SIZE} players.\n\n"
    )

    # Add current squad details if any players are selected
    if selected_players:
        message_text += "Your current squad:\n"
        for i, player in enumerate(selected_players, 1):
            message_text += f"{i}. {player['name']} ({player['team']}) - {player.get('base_price', 0)} Cr\n"
        message_text += "\n"

    message_text += (
        f"Tap a player to select/deselect, use navigation buttons to browse players, "
        f"then tap '✅ Submit Squad' when done."
    )

    # Check if message is too long (Telegram has a 4096 character limit)
    if len(message_text) > 4000:
        # Truncate the squad list if needed
        message_text = (
            f"Select your squad (exactly {SQUAD_SIZE} players required).\n\n"
            f"Currently selected: {len(selected_player_ids)}/{SQUAD_SIZE} players.\n\n"
            f"(Squad list too long to display completely)\n\n"
            f"Tap a player to select/deselect, use navigation buttons to browse players, "
            f"then tap '✅ Submit Squad' when done."
        )

    if isinstance(update, Update) and update.callback_query:
        logger.info("Showing player selection from callback query")
        await update.callback_query.edit_message_text(
            text=message_text, reply_markup=reply_markup
        )
    else:
        logger.info("Showing player selection from direct command")
        await update.message.reply_text(text=message_text, reply_markup=reply_markup)

    return SELECTING_PLAYERS


async def handle_squad_callback_query(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Handle callback queries from the inline keyboard for squad management.
    """
    query = update.callback_query
    callback_data = query.data
    logger.info(f"Squad: Raw callback data received: {callback_data}")

    try:
        # Parse the callback data
        data = json.loads(callback_data)

        # Check if this callback is meant for the squad feature
        if "feature" in data and data.get("feature") != "squad":
            logger.info(f"Squad: Ignoring callback for feature: {data.get('feature')}")
            return

        action = data.get("a", "unknown")
        logger.info(f"Squad: Parsed action: {action}")

        # Answer the callback query to stop the loading indicator
        await query.answer()

        # Get active gully ID
        active_gully_id = ctx_manager.get_active_gully_id(context)

        # Handle different actions
        if action == "toggle":
            # Toggle player selection
            player_id = data.get("id")
            if player_id is not None:
                logger.info(f"Toggling player with ID: {player_id}")

                # Toggle player in gully-specific context
                ctx_manager.toggle_selected_player_id(
                    context, player_id, active_gully_id
                )

                # Show updated selection
                await show_player_selection(update, context)

        elif action == "prev":
            # Go to previous page
            current_page = context.user_data.get(PAGE_KEY, 0)
            if current_page > 0:
                context.user_data[PAGE_KEY] = current_page - 1
                await show_player_selection(update, context)

        elif action == "next":
            # Go to next page
            current_page = context.user_data.get(PAGE_KEY, 0)
            context.user_data[PAGE_KEY] = current_page + 1
            await show_player_selection(update, context)

        elif action == "page":
            # Do nothing for page number display
            pass

        elif action == "submit":
            # Handle squad submission
            await handle_squad_submission(update, context)

        elif action == "edit":
            # Handle edit squad
            await handle_edit_squad(update, context)

        else:
            logger.warning(f"Unknown action: {action}")

    except json.JSONDecodeError:
        logger.error(f"Failed to parse callback data: {callback_data}")
    except Exception as e:
        logger.error(f"Error in handle_squad_callback_query: {e}")
        logger.exception("Detailed traceback:")


async def handle_edit_squad(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the edit squad callback."""
    logger.info("handle_edit_squad called")
    query = update.callback_query
    await query.answer()

    # Get active gully ID
    active_gully_id = ctx_manager.get_active_gully_id(context)

    if not active_gully_id:
        logger.error("Active gully ID not found in context")
        await query.answer(
            "⚠️ Active gully information not found. Please use /squad to start over.",
            show_alert=True,
        )
        return ConversationHandler.END

    # Reset page to 0 when starting edit
    context.user_data[PAGE_KEY] = 0

    # Clear the selected player IDs in gully-specific context
    ctx_manager.set_selected_player_ids(context, [], active_gully_id)
    logger.info("Cleared selected players for fresh squad selection")

    # Show a message to the user
    await query.answer(
        "Starting fresh squad selection. Please select 18 players.", show_alert=True
    )

    # Show player selection with empty selection
    return await show_player_selection(update, context)


async def handle_squad_submission(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle squad submission."""
    logger.info("handle_squad_submission called")

    # Get active gully ID
    active_gully_id = ctx_manager.get_active_gully_id(context)

    # Get selected player IDs from gully-specific context
    selected_player_ids = ctx_manager.get_selected_player_ids(context, active_gully_id)
    logger.info(f"Submitting squad with {len(selected_player_ids)} players")

    # Validate squad size
    if len(selected_player_ids) != SQUAD_SIZE:
        logger.warning(f"Invalid squad size: {len(selected_player_ids)}/{SQUAD_SIZE}")

        error_message = (
            f"⚠️ You must select exactly {SQUAD_SIZE} players. "
            f"You have selected {len(selected_player_ids)} players."
        )

        if update.callback_query:
            await update.callback_query.answer(error_message, show_alert=True)
            return SELECTING_PLAYERS
        else:
            await update.message.reply_text(error_message)
            return await show_player_selection(update, context)

    # Get participant ID for this specific gully
    participant_id = ctx_manager.get_participant_id(context, active_gully_id)
    logger.info(f"Participant ID: {participant_id}")

    if not participant_id:
        logger.error("Participant ID not found in context")
        error_message = "⚠️ Participant ID not found. Please use /squad to start over."

        if update.callback_query:
            await update.callback_query.answer(error_message, show_alert=True)
            return ConversationHandler.END
        else:
            await update.message.reply_text(error_message)
            return ConversationHandler.END

    # Submit squad
    logger.info(f"Submitting squad for participant {participant_id}")
    squad_client = await get_initialized_squad_client()
    result = await squad_client.update_draft_squad(participant_id, selected_player_ids)

    if not result.get("success"):
        error_msg = result.get("error", "Unknown error")
        logger.error(f"Failed to submit squad: {error_msg}")

        if update.callback_query:
            await update.callback_query.answer(
                f"⚠️ Failed to submit squad: {error_msg}", show_alert=True
            )
            return SELECTING_PLAYERS
        else:
            await update.message.reply_text(f"⚠️ Failed to submit squad: {error_msg}")
            return ConversationHandler.END

    # Clear squad selection from gully-specific context
    ctx_manager.clear_squad_selection(context, active_gully_id)
    logger.info("Squad selection cleared from context")

    # Clear cached players and page with gully-specific keys
    if f"all_players_{active_gully_id}" in context.user_data:
        del context.user_data[f"all_players_{active_gully_id}"]
    if PAGE_KEY in context.user_data:
        del context.user_data[PAGE_KEY]

    # Get the updated squad
    squad_data = await squad_client.get_draft_squad(participant_id)
    squad_players = squad_data.get("players", [])
    logger.info(f"Updated squad has {len(squad_players)} players")

    # Store current squad in gully-specific context
    ctx_manager.set_current_squad(context, squad_players, active_gully_id)

    # Show success message with squad details
    squad_text = "✅ Your squad has been updated successfully!\n\n"

    for i, player in enumerate(squad_players, 1):
        squad_text += f"{i}. {player['name']} - {player['team']} - {player.get('base_price', 0)} Cr\n"

    logger.info("Sending success message")

    if update.callback_query:
        await update.callback_query.edit_message_text(squad_text)
    else:
        await update.message.reply_text(squad_text)

    return ConversationHandler.END


async def show_gully_selection(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_gullies: List[Dict[str, Any]],
):
    """Show gully selection when user has multiple gullies."""
    logger.info("Showing gully selection options")

    # Create a keyboard with gully options
    keyboard = []
    for gully in user_gullies:
        gully_id = gully.get("id")
        gully_name = gully.get("name", "Unknown Gully")
        button_text = f"🏏 {gully_name}"

        # Create a callback for selecting this gully
        callback_data = create_feature_callback_data(
            "squad", "select_gully", {"id": gully_id}
        )
        keyboard.append(
            [InlineKeyboardButton(button_text, callback_data=callback_data)]
        )

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "You are part of multiple gullies. Please select one to view/manage your squad:",
        reply_markup=reply_markup,
    )

    # Return to a state that will handle this selection
    return SELECTING_PLAYERS


def get_handlers():
    """Get all handlers for squad management features."""
    logger.info("Registering squad handlers")

    # Create a standalone command handler for /squad
    squad_handler = CommandHandler("squad", squad_command)

    # Create the conversation handler for player selection with a catch-all callback query handler
    squad_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(handle_squad_callback_query),
        ],
        states={
            SELECTING_PLAYERS: [
                CallbackQueryHandler(handle_squad_callback_query),
            ]
        },
        fallbacks=[CommandHandler("squad", squad_command)],
        per_message=False,
        name="squad_conversation",
    )

    return [squad_handler, squad_conv_handler]
