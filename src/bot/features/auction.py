"""
Auction management features for the GullyGuru bot.
Handles auction start and queue management.
"""

import logging
import json
import asyncio
import time
from typing import Dict, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
)

# Use the centralized client initialization
from src.bot.api_client.init import (
    get_initialized_onboarding_client,
    get_initialized_auction_client,
)
from src.bot.context import manager as ctx_manager
from src.bot.features.player_release import (
    standardize_player_data,
    notify_participants_about_release,
    close_release_window,
    RELEASE_WINDOW_MINUTES,
    process_remaining_participants,
)
from src.bot.utils.callback_utils import (
    create_callback_data,
    parse_callback_data,
    create_callback_pattern,
)

# Configure logging
logger = logging.getLogger(__name__)

# Define module constants
MODULE_ID = "auction"  # Short but descriptive module ID
SELECTING_PLAYERS_TO_RELEASE = 1


def create_auction_callback(action: str, data: Dict[str, Any] = None) -> str:
    """Create a callback specific to the auction feature."""
    return create_callback_data(MODULE_ID, action, data)


async def wait_for_api(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Check if API is available for the current request.
    """
    try:
        client = await get_initialized_onboarding_client()
        if client is None:
            raise Exception("Failed to initialize onboarding client")
        return True
    except Exception as e:
        logger.error(f"API not available: {e}")
        await update.message.reply_text(
            "⚠️ The GullyGuru service is currently unavailable. Please try again later."
        )
        return False


async def start_auction_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle the /start_auction command.
    This command is admin-only and starts the auction process.
    """
    logger.info(
        f"Auction: Start auction command called by user {update.effective_user.id} in chat {update.effective_chat.id}"
    )

    # Check if API is available
    if not await wait_for_api(update, context):
        return

    # Get gully ID from telegram group ID
    telegram_group_id = update.effective_chat.id

    try:
        # Get gully by telegram group ID
        client = await get_initialized_onboarding_client()

        # Debug the client type
        logger.info(f"Client type: {type(client)}")

        # Use the correct method for the OnboardingApiClient
        gully = await client.get_gully_by_telegram_group_id(telegram_group_id)

        if not gully:
            logger.warning(f"No gully found for telegram group ID {telegram_group_id}")
            await update.message.reply_text(
                "⚠️ This group is not associated with any gully. Please create a gully for this group first."
            )
            return

        gully_id = gully.get("id")
        gully_name = gully.get("name", "Unknown Gully")
        gully_status = gully.get("status", "unknown").lower()

        logger.info(
            f"Found gully {gully_id} ({gully_name}) with status {gully_status} for telegram group {telegram_group_id}"
        )

        # Validate gully_id is not None
        if not gully_id:
            logger.error("Failed to get valid gully ID")
            await update.message.reply_text(
                "⚠️ Failed to identify a valid gully for this group. Please contact an administrator."
            )
            return

        # Store gully info in context for future use
        context.chat_data["gully_id"] = gully_id
        context.chat_data["gully_name"] = gully_name

        # Check if gully is already in auction state
        if gully_status == "auction":
            await update.message.reply_text(
                f"⚠️ Auction for {gully_name} is already in progress. You cannot start it again."
            )
            return

        # Check if gully is in a state other than draft
        if gully_status != "draft":
            await update.message.reply_text(
                f"⚠️ Cannot start auction for {gully_name} because it is in '{gully_status}' state. The gully must be in 'draft' state to start an auction."
            )
            return

    except Exception as e:
        logger.error(f"Error getting gully by telegram group ID: {e}")
        logger.exception("Detailed traceback:")
        await update.message.reply_text(
            "⚠️ Failed to retrieve gully information for this group. Please try again later."
        )
        return

    # Start the auction
    await update.message.reply_text(
        f"🚀 Starting auction process for {gully_name}... Please wait."
    )

    try:
        # Get the auction client
        auction_client = await get_initialized_auction_client()

        # Debug the auction client type
        logger.info(f"Auction client type: {type(auction_client)}")

        # Use the correct method for the AuctionApiClient
        try:
            auction_start_response = await auction_client.start_auction(gully_id)
            logger.info(f"Auction start response: {auction_start_response}")
        except Exception as api_error:
            error_message = str(api_error)

            # Check for specific error messages in the API response
            if "must be in draft state" in error_message:
                await update.message.reply_text(
                    f"⚠️ Cannot start auction for {gully_name}. The gully must be in 'draft' state, but it is currently in another state."
                )
            elif "already in progress" in error_message:
                await update.message.reply_text(
                    f"⚠️ Auction for {gully_name} is already in progress."
                )
            else:
                await update.message.reply_text(
                    f"⚠️ Failed to start auction: {error_message}"
                )

            logger.error(f"Error starting auction: {api_error}")
            logger.exception("Detailed API error:")
            return

        if not auction_start_response:
            await update.message.reply_text(
                "⚠️ Failed to start auction. Please try again later."
            )
            return

        # Extract data directly from the auction start response
        response_data = auction_start_response.get("data", {})

        # Check if there's a nested data structure
        if "data" in response_data:
            auction_data = response_data.get("data", {})
        else:
            auction_data = response_data

        contested_players = auction_data.get("contested_players", [])
        uncontested_players = auction_data.get("uncontested_players", [])
        contested_count = auction_data.get("contested_count", 0)
        uncontested_count = auction_data.get("uncontested_count", 0)

        logger.info(f"Contested players: {contested_players}")
        logger.info(f"Uncontested players: {uncontested_players}")

        # First display uncontested players assigned to each participant
        message = f"🏆 Auction has started for {gully_name}!\n\n"
        message += f"Uncontested players ({uncontested_count}) have been assigned to participants:\n\n"

        # Group uncontested players by participant
        participants_players = {}
        for player in uncontested_players:
            for participant in player.get("participants", []):
                participant_id = participant.get("participant_id")
                if participant_id not in participants_players:
                    participants_players[participant_id] = {
                        "team_name": participant.get("team_name", "Unknown Team"),
                        "players": [],
                    }
                participants_players[participant_id]["players"].append(
                    {
                        "name": player.get("player_name"),
                        "team": player.get("team"),
                        "role": player.get("role"),
                        "base_price": player.get("base_price", 0),
                    }
                )

        # Display each participant's uncontested players
        for participant_id, data in participants_players.items():
            message += f"📋 Participant: {data['team_name']}\n"
            for player in data["players"]:
                message += f"🏏 {player['name']} ({player['team']})\n"
            message += "\n"

        await update.message.reply_text(message)

        # Then display contested players that will go to auction queue
        if contested_count > 0:
            contest_message = f"⚔️ Contested players ({contested_count}) that will enter the auction queue:\n\n"
            for player in contested_players:
                player_name = player.get("name")
                team = player.get("team")
                contest_count = player.get("contest_count", 0)

                contest_message += f"🏏 {player_name} ({team})\n"
                contest_message += f"   Contested by {contest_count} participants: "

                contested_by = []
                for participant in player.get("contested_by", []):
                    contested_by.append(participant.get("team_name", "Unknown"))

                contest_message += f"{', '.join(contested_by)}\n\n"

            await update.message.reply_text(contest_message)

        # Send message about release window
        await update.message.reply_text(
            f"⏳ You now have {RELEASE_WINDOW_MINUTES} minutes to privately release unwanted players from your list."
        )

        # Store auction state in context with gully-specific keys
        ctx_manager.set_release_window_state(context, gully_id, True)
        ctx_manager.set_auction_start_time(context, gully_id, time.time())

        # Standardize and store auction data
        standardized_uncontested = [
            standardize_player_data(p) for p in uncontested_players
        ]
        standardized_contested = [standardize_player_data(p) for p in contested_players]

        # Store standardized data in context
        ctx_manager.set_uncontested_players(context, gully_id, standardized_uncontested)
        ctx_manager.set_contested_players(context, gully_id, standardized_contested)

        # Schedule the release window closure with processing of remaining participants
        asyncio.create_task(
            close_release_window(context, gully_id, update.effective_chat.id)
        )

        # Notify all participants privately
        await notify_participants_about_release(context, gully_id)

        # Update gully cache with fresh status
        try:
            # Get fresh gully data
            fresh_gully = await client.get_gully(gully_id)
            if fresh_gully:
                # Update cache
                if "gully_data" not in context.bot_data:
                    context.bot_data["gully_data"] = {}
                context.bot_data["gully_data"][gully_id] = fresh_gully

                logger.info(
                    f"Updated gully {gully_id} cache with fresh status: {fresh_gully.get('status')}"
                )
        except Exception as cache_error:
            logger.error(f"Error updating gully cache: {cache_error}")

    except Exception as e:
        logger.error(f"Error starting auction: {e}")
        logger.exception("Detailed traceback:")
        await update.message.reply_text(
            "⚠️ An error occurred while starting the auction. Please try again later."
        )


async def next_player_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle the /next_player command to move to the next player in the auction queue.
    This command is admin-only.
    """
    logger.info(
        f"Auction: Next player command called by user {update.effective_user.id} in chat {update.effective_chat.id}"
    )

    # Check if API is available
    if not await wait_for_api(update, context):
        return

    # Implementation for getting the next player
    await update.message.reply_text("Getting next player in auction queue...")

    # TODO: Implement API calls to get next player and display to group
    # This would involve:
    # 1. Get the gully ID for this group
    # 2. Call the auction API to get the next player
    # 3. Present that player with bid buttons

    # For now, we'll just add a placeholder to show how the callback would work
    keyboard = [
        [
            InlineKeyboardButton(
                "Start Bidding",
                callback_data=create_auction_callback("start_bid", {"player_id": 123}),
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Next player: Sample Player (Team) - 2.0 Cr\nReady to begin bidding?",
        reply_markup=reply_markup,
    )


async def handle_auction_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> Optional[bool]:
    """Handle callbacks specific to auction feature."""
    query = update.callback_query
    callback_data = parse_callback_data(query.data)

    # Only process callbacks for this module
    if not callback_data or callback_data["module"] != MODULE_ID:
        return None

    # Log the callback being handled
    logger.info(f"Auction: Processing callback with action {callback_data['action']}")

    # Process the action
    action = callback_data["action"]
    data = callback_data.get("data", {})

    try:
        # Answer the callback query to stop the loading indicator
        await query.answer()

        # Handle different actions
        if action == "start_bid":
            player_id = data.get("player_id")
            await query.edit_message_text(
                f"Starting bidding for player ID: {player_id}"
            )
            # TODO: Implement actual bidding logic
            return True

        # Add more action handlers as needed

        return True

    except Exception as e:
        logger.error(f"Error handling auction callback: {e}")
        logger.exception("Detailed traceback:")
        return None


async def reset_auction_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Command to reset auction state for a gully.
    Designed for use in private chats with the bot.

    Usage:
    /reset_auction [GULLY_ID] [--start]

    - GULLY_ID: Optional ID of gully to reset (uses active gully if not specified)
    - --start: Optional flag to restart auction after reset
    """
    logger.info(f"Reset auction command called by user {update.effective_user.id}")

    # Check if API is available
    if not await wait_for_api(update, context):
        return

    # Parse arguments
    args = context.args
    start_auction = False
    specified_gully_id = None

    # Process arguments
    for arg in args:
        if arg == "--start":
            start_auction = True
        elif arg.isdigit():
            specified_gully_id = int(arg)

    # Determine gully ID (from args or active gully)
    if specified_gully_id:
        gully_id = specified_gully_id
    else:
        # Get active gully from context
        gully_id = ctx_manager.get_active_gully_id(context)

        if not gully_id:
            await update.message.reply_text(
                "⚠️ No active gully selected. Please select a gully first with /gullies or specify a gully ID: /reset_auction GULLY_ID"
            )
            return

    # Get gully info to verify it exists
    try:
        client = await get_initialized_onboarding_client()
        gully = await client.get_gully(gully_id)

        if not gully:
            await update.message.reply_text(f"⚠️ No gully found with ID {gully_id}.")
            return

        gully_name = gully.get("name", "Unknown Gully")
        telegram_group_id = gully.get("telegram_group_id")

        if not telegram_group_id:
            await update.message.reply_text(
                f"⚠️ Gully {gully_name} doesn't have an associated Telegram group. Cannot reset auction."
            )
            return

    except Exception as e:
        logger.error(f"Error getting gully {gully_id}: {e}")
        await update.message.reply_text(
            f"⚠️ Failed to retrieve information for gully {gully_id}."
        )
        return

    # Reset auction state in the database using the stop endpoint
    await update.message.reply_text(
        f"🔄 Resetting auction for {gully_name}... Please wait."
    )

    # Get the auction client
    auction_client = await get_initialized_auction_client()

    # Call the API to stop the auction
    try:
        reset_response = await auction_client.stop_auction(gully_id, context)
        logger.info(f"Auction stop response: {reset_response}")

        if not reset_response or not reset_response.get("success", False):
            error_message = reset_response.get("message", "Unknown error")
            await update.message.reply_text(
                f"⚠️ Failed to reset auction: {error_message}"
            )
            return

    except Exception as api_error:
        error_message = str(api_error)
        await update.message.reply_text(f"⚠️ Failed to reset auction: {error_message}")
        logger.error(f"Error stopping auction: {api_error}")
        logger.exception("Detailed API error:")
        return

    # Reset all auction and release related context data to pre-auction state
    try:
        # Pre-auction state includes:
        # 1. Release window closed
        ctx_manager.set_release_window_state(context, gully_id, False)

        # 2. No selected players for release
        ctx_manager.set_selected_release_player_ids(context, [], gully_id)

        # 3. Release not submitted
        ctx_manager.set_release_submitted(context, False, gully_id)

        # 4. No uncontested players in cache
        ctx_manager.set_uncontested_players(context, gully_id, [])

        # 5. No contested players in cache
        ctx_manager.set_contested_players(context, gully_id, [])

        # 6. No auction start time
        ctx_manager.set_auction_start_time(context, gully_id, 0)

        logger.info(f"Reset all auction context for gully {gully_id}")

    except Exception as ctx_error:
        logger.error(f"Error resetting auction context: {ctx_error}")
        logger.exception("Detailed context error:")
        # Continue anyway since the DB reset is more important

    # Notify success with details about what was reset
    await update.message.reply_text(
        f"✅ Auction for {gully_name} has been reset successfully."
    )

    # If --start flag is provided, we need to consider how to start an auction from private chat
    if start_auction:
        # Since we're in private chat, we can't directly use start_auction_command
        # So we'll send a message about it
        await update.message.reply_text(
            f"To start the auction for {gully_name}, please go to the group chat and use the /start_auction command."
        )


def get_handlers():
    """Get all handlers for auction management features."""
    logger.info("Registering auction handlers")

    # Create command handlers
    start_auction_handler = CommandHandler("start_auction", start_auction_command)
    next_player_handler = CommandHandler("next_player", next_player_command)
    reset_auction_handler = CommandHandler("reset_auction", reset_auction_command)

    # Create dedicated auction callback handler
    auction_callback_handler = CallbackQueryHandler(
        handle_auction_callback, pattern=create_callback_pattern(MODULE_ID)
    )

    return [
        start_auction_handler,
        next_player_handler,
        reset_auction_handler,
        auction_callback_handler,
    ]
