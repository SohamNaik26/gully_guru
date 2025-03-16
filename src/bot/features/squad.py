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
    callback_data = {"a": action}
    if data:
        callback_data.update(data)
    return json.dumps(callback_data)


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
    """Handle the /squad command."""
    logger.info(f"Squad command called by user {update.effective_user.id}")

    # Reset page to 0 when starting squad command
    context.user_data[PAGE_KEY] = 0

    # Check if API is available
    try:
        client = await get_initialized_onboarding_client()
        if not client:
            raise Exception("Failed to initialize client")
    except Exception as e:
        logger.error(f"API not available in command: {e}")
        await update.message.reply_text(
            "⚠️ The GullyGuru service is currently unavailable. Please try again later."
        )
        return ConversationHandler.END

    # Get user ID from context or fetch from API
    user_id = ctx_manager.get_user_id(context)
    logger.info(f"User ID from context: {user_id}")

    if not user_id:
        logger.info(
            f"User ID not found in context, fetching from API for Telegram ID {update.effective_user.id}"
        )
        client = await get_initialized_onboarding_client()
        db_user = await client.get_user_by_telegram_id(update.effective_user.id)

        if not db_user:
            logger.warning(
                f"User with Telegram ID {update.effective_user.id} not found in database"
            )
            await update.message.reply_text(
                "⚠️ Your account was not found. Please use /start to register."
            )
            return ConversationHandler.END

        user_id = db_user["id"]
        logger.info(f"User ID fetched from API: {user_id}")
        ctx_manager.set_user_id(context, user_id)

    # Get active gully and participant
    active_gully_id = ctx_manager.get_active_gully_id(context)
    participant_id = ctx_manager.get_participant_id(context)
    logger.info(f"Active gully ID: {active_gully_id}, Participant ID: {participant_id}")

    # If no active gully, check if user has any gullies
    if not active_gully_id or not participant_id:
        logger.info("No active gully or participant ID, checking user's gullies")
        client = await get_initialized_onboarding_client()
        user_gullies = await client.get_user_gullies(user_id)
        logger.info(f"User has {len(user_gullies)} gullies")

        if not user_gullies:
            logger.warning(f"User {user_id} has no gullies")
            await update.message.reply_text(
                "You are not part of any gullies yet. Ask your friends to add you to their gully "
                "or create a new one by adding this bot to a Telegram group."
            )
            return ConversationHandler.END

        # If user has only one gully, set it as active
        if len(user_gullies) == 1:
            gully = user_gullies[0]
            active_gully_id = gully["id"]
            logger.info(f"Setting active gully ID to {active_gully_id}")
            ctx_manager.set_active_gully_id(context, active_gully_id)

            # Get participant ID
            participant = await client.get_participant_by_user_and_gully(
                user_id=user_id, gully_id=active_gully_id
            )

            if participant:
                participant_id = participant["id"]
                logger.info(f"Setting participant ID to {participant_id}")
                ctx_manager.set_participant_id(context, participant_id)
            else:
                logger.warning(
                    f"User {user_id} is not a participant in gully {active_gully_id}"
                )
                await update.message.reply_text(
                    "⚠️ You are not a participant in this gully. Please use /start to register."
                )
                return ConversationHandler.END
        else:
            # User has multiple gullies, ask them to select one
            logger.info(f"User has multiple gullies, asking to select one")
            await update.message.reply_text(
                "Please select a gully first using /gullies command."
            )
            return ConversationHandler.END

    # Check gully status - only allow squad selection if gully is in draft status
    logger.info(f"Checking status for gully {active_gully_id}")
    gully = await client.get_gully(active_gully_id)

    if not gully:
        logger.error(f"Failed to fetch gully {active_gully_id}")
        await update.message.reply_text(
            "⚠️ Failed to fetch gully information. Please try again later."
        )
        return ConversationHandler.END

    gully_status = gully.get("status", "").lower()
    logger.info(f"Gully status: {gully_status}")

    if gully_status != "draft":
        logger.info(
            f"Squad selection not allowed for gully with status: {gully_status}"
        )
        await update.message.reply_text(
            "Squad selection process is completed, you can no longer select a squad."
        )
        return ConversationHandler.END

    # Get the squad for this participant
    logger.info(f"Fetching squad for participant {participant_id}")
    squad_client = await get_initialized_squad_client()
    squad_data = await squad_client.get_draft_squad(participant_id)

    # Check if squad exists and has players
    squad_players = squad_data.get("players", [])
    logger.info(f"Squad has {len(squad_players)} players")

    # Store current squad in context
    ctx_manager.set_current_squad(context, squad_players)

    # Set selected player IDs in context
    selected_player_ids = [player["id"] for player in squad_players]
    ctx_manager.set_selected_player_ids(context, selected_player_ids)

    # If squad is empty or incomplete, go directly to player selection
    if len(squad_players) < SQUAD_SIZE:
        logger.info(
            f"Squad is incomplete ({len(squad_players)}/{SQUAD_SIZE}), showing player selection"
        )
        return await show_player_selection(update, context)

    # Show current squad with edit option
    logger.info("Showing current squad with edit option")
    squad_text = "Your current squad:\n\n"

    for i, player in enumerate(squad_players, 1):
        squad_text += f"{i}. {player['name']} - {player['team']} - {player.get('base_price', 0)} Cr\n"

    # Create inline keyboard for squad actions
    keyboard = [
        [
            InlineKeyboardButton(
                "🏏 Edit Squad", callback_data=create_callback_data("edit")
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"{squad_text}\n\nYou have {len(squad_players)}/{SQUAD_SIZE} players selected.",
        reply_markup=reply_markup,
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

    # Get all available players
    all_players = context.user_data.get("all_players")
    if not all_players:
        squad_client = await get_initialized_squad_client()
        all_players = await squad_client.get_available_players(max_players=250)
        context.user_data["all_players"] = all_players
        logger.info(f"Fetched {len(all_players)} available players")

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

    # Get selected player IDs from context
    selected_player_ids = ctx_manager.get_selected_player_ids(context)
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


async def handle_callback_query(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> Optional[int]:
    """Handle callback queries from the inline keyboard."""
    query = update.callback_query
    callback_data = query.data
    logger.info(f"Raw callback data received: {callback_data}")

    # Parse the callback data
    data = parse_callback_data(callback_data)
    action = data.get("a", "unknown")
    logger.info(f"Parsed action: {action}")

    # Answer the callback query to stop the loading indicator
    await query.answer()

    # Get current page from context or default to 0
    current_page = context.user_data.get(PAGE_KEY, 0)

    # Handle different actions
    if action == "next":
        # Go to next page
        context.user_data[PAGE_KEY] = current_page + 1
        logger.info(f"Navigating to next page: {current_page + 1}")
        return await show_player_selection(update, context)

    elif action == "prev":
        # Go to previous page
        if current_page > 0:
            context.user_data[PAGE_KEY] = current_page - 1
            logger.info(f"Navigating to previous page: {current_page - 1}")
        return await show_player_selection(update, context)

    elif action == "page":
        # Page indicator (do nothing)
        logger.info("Page indicator clicked (no action)")
        return SELECTING_PLAYERS

    elif action == "submit":
        # Submit squad
        logger.info("Submit button pressed")
        return await handle_squad_submission(update, context)

    elif action == "toggle":
        # Toggle player selection
        player_id = data.get("id")
        if player_id is not None:
            logger.info(f"Toggling player with ID: {player_id}")

            # Toggle player selection
            selected_player_ids = ctx_manager.get_selected_player_ids(context)

            if player_id in selected_player_ids:
                # Remove player
                selected_player_ids.remove(player_id)
                logger.info(f"Removed player ID: {player_id}")
            else:
                # Check if adding this player would exceed the maximum squad size
                if len(selected_player_ids) >= SQUAD_SIZE:
                    logger.warning(
                        f"Cannot add more than {SQUAD_SIZE} players to squad"
                    )
                    await query.answer(
                        f"⚠️ You cannot select more than {SQUAD_SIZE} players. Please remove a player first.",
                        show_alert=True,
                    )
                    return SELECTING_PLAYERS

                # Add player
                selected_player_ids.append(player_id)
                logger.info(f"Added player ID: {player_id}")

            # Update context
            ctx_manager.set_selected_player_ids(context, selected_player_ids)
            logger.info(
                f"Updated selected players: {len(selected_player_ids)}/{SQUAD_SIZE}"
            )

            # Show updated player selection
            return await show_player_selection(update, context)
        else:
            logger.error("Player ID not found in callback data")

    elif action == "edit":
        # Edit squad
        logger.info("Edit squad button pressed")
        # Reset page to 0 when starting edit
        context.user_data[PAGE_KEY] = 0
        return await handle_edit_squad(update, context)

    else:
        logger.warning(f"Unknown action: {action}")

    return SELECTING_PLAYERS


async def handle_edit_squad(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the edit squad callback."""
    logger.info("handle_edit_squad called")
    query = update.callback_query
    await query.answer()

    # Reset page to 0 when starting edit
    context.user_data[PAGE_KEY] = 0

    # Get participant ID and active gully ID from context
    participant_id = ctx_manager.get_participant_id(context)
    active_gully_id = ctx_manager.get_active_gully_id(context)

    if not participant_id or not active_gully_id:
        logger.error("Participant ID or Gully ID not found in context")
        await query.answer(
            "⚠️ Participant or Gully information not found. Please use /squad to start over.",
            show_alert=True,
        )
        return ConversationHandler.END

    # Check gully status - only allow squad editing if gully is in draft status
    logger.info(f"Checking status for gully {active_gully_id}")
    client = await get_initialized_onboarding_client()
    gully = await client.get_gully(active_gully_id)

    if not gully:
        logger.error(f"Failed to fetch gully {active_gully_id}")
        await query.answer(
            "⚠️ Failed to fetch gully information. Please try again later.",
            show_alert=True,
        )
        return ConversationHandler.END

    gully_status = gully.get("status", "").lower()
    logger.info(f"Gully status: {gully_status}")

    if gully_status != "draft":
        logger.info(f"Squad editing not allowed for gully with status: {gully_status}")
        await query.edit_message_text(
            "Squad selection process is completed, you can no longer select a squad."
        )
        return ConversationHandler.END

    # Clear the selected player IDs in context to start fresh
    ctx_manager.set_selected_player_ids(context, [])
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

    # Get selected player IDs from context
    selected_player_ids = ctx_manager.get_selected_player_ids(context)
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

    # Get participant ID from context
    participant_id = ctx_manager.get_participant_id(context)
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

    # Clear selected player IDs from context
    ctx_manager.clear_squad_selection(context)
    logger.info("Squad selection cleared from context")

    # Clear cached players and page
    if "all_players" in context.user_data:
        del context.user_data["all_players"]
    if PAGE_KEY in context.user_data:
        del context.user_data[PAGE_KEY]

    # Get the updated squad
    squad_data = await squad_client.get_draft_squad(participant_id)
    squad_players = squad_data.get("players", [])
    logger.info(f"Updated squad has {len(squad_players)} players")

    # Store current squad in context
    ctx_manager.set_current_squad(context, squad_players)

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


def get_handlers():
    """Get all handlers for squad management features."""
    logger.info("Registering squad handlers")

    # Create a standalone command handler for /squad
    squad_handler = CommandHandler("squad", squad_command)

    # Create the conversation handler for player selection with a catch-all callback query handler
    squad_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(handle_callback_query),
        ],
        states={
            SELECTING_PLAYERS: [
                CallbackQueryHandler(handle_callback_query),
            ]
        },
        fallbacks=[CommandHandler("squad", squad_command)],
        per_message=False,
        name="squad_conversation",
    )

    return [squad_handler, squad_conv_handler]
