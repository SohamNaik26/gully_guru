"""
Simplified auction queue features for the GullyGuru bot.
Handles the auction process for players, including bidding and skipping.
"""

import logging
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional, List, Set
from telegram import (
    Update,
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

# Use the centralized client initialization
from src.bot.api_client.init import (
    get_initialized_onboarding_client,
    get_initialized_auction_client,
)
from src.bot.context import manager as ctx_manager
from src.bot.utils.callback_utils import (
    create_callback_data,
    parse_callback_data,
    create_callback_pattern,
)

# Configure logging
logger = logging.getLogger(__name__)

# Module identifier constant
MODULE_ID = "que"

# Conversation states
BIDDING_STATE = 1

# Constants
BID_TIMEOUT_SECONDS = 15  # Auction timer (15 seconds)
AUCTION_TIMER_KEY = "auction_timer"  # Timer for auction finalization
BID_INCREMENT = 0.5  # Fixed increment of 0.5 CR


# ===== API AND CONTEXT MANAGEMENT FUNCTIONS =====


async def wait_for_api(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Check if API is available for the current request.
    Returns True if API is available, otherwise sends an error message and returns False.
    """
    try:
        client = await get_initialized_onboarding_client()
        if client is None:
            raise Exception("Failed to initialize onboarding client")
        return True
    except Exception as e:
        logger.error(f"API not available: {e}")
        if update and update.message:
            await update.message.reply_text(
                "⚠️ The GullyGuru service is currently unavailable. Please try again later."
            )
        return False


def ensure_auction_context(context, gully_id):
    """Ensure auction data exists in bot_data for the gully."""
    gully_data = ctx_manager.ensure_bot_gully_data(context, gully_id)

    if "auction" not in gully_data:
        gully_data["auction"] = {
            "current_player": None,
            "auction_queue_id": None,
            "bids": [],  # List to track all bids
            "all_participants": [],
            "auction_active": False,
            "has_base_bid": False,
            "bid_count": 0,  # Global bid counter for the gully
            "skipped_users": [],
            "base_price": 0,
            "last_bidder": None,
        }

    return gully_data["auction"]


def get_auction_data(context, gully_id=None):
    """Get auction data from context for a specific gully."""
    if gully_id is None:
        gully_id = ctx_manager.get_active_gully_id(context)
        if gully_id is None:
            return None

    gully_data = context.bot_data.get("gullies", {}).get(gully_id, {})
    return gully_data.get("auction")


def set_auction_data(context, gully_id, auction_data):
    """Set auction data in context for a specific gully."""
    gully_data = ctx_manager.ensure_bot_gully_data(context, gully_id)
    gully_data["auction"] = auction_data
    logger.info(f"Updated auction data for gully: {gully_id}")


def clear_auction_data(context, gully_id):
    """Clear auction data from context for a specific gully."""
    gully_data = context.bot_data.get("gullies", {}).get(gully_id, {})
    if "auction" in gully_data:
        del gully_data["auction"]
        logger.info(f"Cleared auction data for gully: {gully_id}")


def clear_auction_timer(context):
    """Clear any existing auction timer."""
    if AUCTION_TIMER_KEY in context.chat_data:
        try:
            timer = context.chat_data[AUCTION_TIMER_KEY]
            if not timer.done():
                timer.cancel()
            logger.info("Auction timer cancelled successfully")
        except Exception as e:
            logger.error(f"Error cancelling auction timer: {e}")
        finally:
            context.chat_data.pop(AUCTION_TIMER_KEY, None)


# ===== PARTICIPANT MANAGEMENT FUNCTIONS =====


async def initialize_auction_participants(
    update: Update, context: ContextTypes.DEFAULT_TYPE, gully_id
):
    """
    Initialize participants for the auction by combining data from:
    1. Participants API (gives participant_id and backend user_id)
    2. Users API (gives backend user_id and telegram_id)

    Returns a tuple of (success, participants, participant_user_map).
    """
    logger.info(f"Initializing participants for gully {gully_id}")

    try:
        # Get participants from the onboarding API
        onboarding_client = await get_initialized_onboarding_client()
        participants = await onboarding_client.get_participants(gully_id)

        # Validate participants
        if not participants:
            logger.warning(f"No participants found for gully {gully_id}")
            if update and update.message:
                await update.message.reply_text(
                    "⚠️ No participants found for this gully."
                )
            return False, None, None

        logger.info(f"Retrieved {len(participants)} participants for gully {gully_id}")

        # Get all users to build mapping between backend user_id and telegram_id
        users_response = await onboarding_client.get_users()
        users = (
            users_response.get("items", [])
            if isinstance(users_response, dict)
            else users_response
        )

        # Create a mapping of backend user_id to telegram_id
        backend_to_telegram_map = {}
        for user in users:
            backend_user_id = user.get("id")
            telegram_id = user.get("telegram_id")
            if backend_user_id and telegram_id:
                backend_to_telegram_map[backend_user_id] = telegram_id
                logger.info(
                    f"Mapped backend user_id {backend_user_id} to telegram_id {telegram_id}"
                )

        logger.info(
            f"Created backend-to-telegram mapping with {len(backend_to_telegram_map)} entries"
        )

        # IMPORTANT: Standardize participant data structure with telegram IDs
        standardized_participants = []
        participant_user_map = {}  # participant_id -> telegram_id mapping
        missing_mappings = []

        for p in participants:
            # Get backend and participant IDs
            participant_id = p.get("id")
            backend_user_id = p.get("user_id")
            team_name = p.get("team_name", "Unknown Team")

            # Look up telegram_id using backend_user_id
            telegram_id = backend_to_telegram_map.get(backend_user_id)

            # Create standardized participant object
            standardized_p = {
                "participant_id": participant_id,
                "backend_user_id": backend_user_id,
                "team_name": team_name,
                "role": p.get("role", "member"),
                "budget": 100.0,  # Default budget, will be updated from auction API
                "players_owned": 0,  # Default, will be updated from auction API
            }

            # Add telegram_id if found
            if telegram_id:
                standardized_p["user_id"] = (
                    telegram_id  # This is the key field used for messaging
                )
                participant_user_map[participant_id] = telegram_id
                logger.info(
                    f"Connected participant {participant_id} to telegram_id {telegram_id}"
                )
            else:
                missing_mappings.append(team_name)
                logger.warning(
                    f"No telegram_id found for participant {participant_id} (backend user {backend_user_id})"
                )

            standardized_participants.append(standardized_p)

        # Store the mapping in context
        gully_data = ctx_manager.ensure_bot_gully_data(context, gully_id)
        gully_data["participant_user_map"] = participant_user_map

        # Detailed logging of what we've found
        logger.info(
            f"Generated participant-telegram mapping with {len(participant_user_map)}/{len(participants)} entries"
        )
        if standardized_participants:
            logger.info(f"First participant: {standardized_participants[0]}")

        # Report missing mappings but continue
        if missing_mappings and update and update.message:
            missing_text = "⚠️ Some teams don't have Telegram user mappings:\n"
            for team_name in missing_mappings:
                missing_text += f"• {team_name}\n"
            missing_text += "\nThese teams may have trouble bidding. Each participant should start a private chat with the bot and join the gully."
            await update.message.reply_text(missing_text)

        logger.info(
            f"Successfully initialized {len(standardized_participants)} participants with {len(participant_user_map)} user mappings"
        )
        return True, standardized_participants, participant_user_map

    except Exception as e:
        logger.error(f"Error initializing participants: {e}")
        logger.exception("Detailed error traceback:")
        if update and update.message:
            await update.message.reply_text(
                "⚠️ Failed to initialize participants. Please try again later."
            )
        return False, None, None


def get_participant_for_user(participants, user_id, participant_user_map=None):
    """
    Find the participant associated with a user ID.
    Checks direct user_id in participant data first, then tries the mapping.
    Returns None if no participant is found.
    """
    # First check if any participant has direct user_id match
    for participant in participants:
        if participant.get("user_id") == user_id:
            return participant

    # If mapping is provided, try to find via participant_id
    if participant_user_map:
        # Create reverse mapping
        user_to_participant = {v: k for k, v in participant_user_map.items()}
        if user_id in user_to_participant:
            participant_id = user_to_participant[user_id]
            for participant in participants:
                if participant.get("participant_id") == participant_id:
                    return participant

    # No participant found
    return None


async def send_private_messages_to_participants(
    context, gully_id, participants, participant_user_map, player_data
):
    """
    Send private messages to all participants about the current player.
    Returns the number of successfully sent messages.
    """
    player_name = player_data.get("name", "Unknown Player")
    base_price = float(player_data.get("base_price", 0))
    success_count = 0

    for participant in participants:
        participant_id = participant.get("participant_id")
        user_id = participant.get("user_id")  # From direct data

        if not user_id and participant_id in participant_user_map:
            user_id = participant_user_map[participant_id]

        if not user_id:
            logger.warning(f"No user ID found for participant {participant_id}")
            continue

        try:
            budget = participant.get("budget", 0)
            players_owned = participant.get("players_owned", 0)
            total_players = 18  # Standard size
            min_remaining = 15 - players_owned
            team_name = participant.get("team_name", "Unknown Team")

            private_message = (
                f"🏏 <b>Player up for auction:</b> {player_name}\n"
                f"Base Price: {base_price} CR\n\n"
                f"<b>Your Team:</b> {team_name}\n"
                f"<b>Your Budget:</b> {budget} CR\n"
                f"<b>Team Status:</b> {players_owned}/{total_players} players\n"
                f"<b>Remaining Slots:</b> {min_remaining} minimum"
            )

            logger.info(
                f"Sending private message to user {user_id} for participant {participant_id}"
            )
            await context.bot.send_message(
                chat_id=user_id, text=private_message, parse_mode="HTML"
            )
            success_count += 1

        except Exception as e:
            logger.error(f"Failed to send private message to user {user_id}: {e}")

    logger.info(f"Sent {success_count}/{len(participants)} private messages")
    return success_count


# ===== AUCTION COMMAND HANDLERS =====


async def next_player_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Get the next player for auction.
    This command initializes participants, fetches the next player, and starts bidding.
    """
    logger.info(
        f"Queue: /next_player command called by user {update.effective_user.id}"
    )

    # Get chat ID and ensure we're in a group
    chat_id = update.effective_chat.id
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text(
            "⚠️ This command can only be used in a group chat."
        )
        return ConversationHandler.END

    # Check if API is available
    if not await wait_for_api(update, context):
        return ConversationHandler.END

    # Get or retrieve gully ID for this group
    gully_id = ctx_manager.get_active_gully_id(context)

    if not gully_id:
        # Get gully from the onboarding API
        await update.message.reply_text("🔍 Looking up gully for this group...")
        onboarding_client = await get_initialized_onboarding_client()
        gully_data = await onboarding_client.get_gully_by_telegram_group_id(chat_id)

        if not gully_data:
            await update.message.reply_text(
                "⚠️ This group is not associated with any gully. Please contact an administrator."
            )
            return ConversationHandler.END

        gully_id = gully_data["id"]
        # Store in context
        ctx_manager.update_gully_data(context, gully_id, gully_data)
        ctx_manager.set_active_gully_id(context, gully_id)

    # Check for active auction
    auction_data = get_auction_data(context, gully_id)
    if auction_data and auction_data.get("auction_active", False):
        await update.message.reply_text(
            "⚠️ An auction is already in progress. Please wait for it to complete or use /finalize."
        )
        return BIDDING_STATE

    # Cancel any existing auction timer
    clear_auction_timer(context)

    # Clear existing auction data
    clear_auction_data(context, gully_id)

    try:
        # Initialize participants
        success, participants, participant_user_map = (
            await initialize_auction_participants(update, context, gully_id)
        )
        if not success:
            return ConversationHandler.END

        # Get the next player from auction API
        await update.message.reply_text("🔍 Fetching next player from auction queue...")
        auction_client = await get_initialized_auction_client()
        next_player_response = await auction_client.get_next_player(gully_id)

        if not next_player_response.get("success", False):
            error_msg = next_player_response.get("message", "Unknown error")
            await update.message.reply_text(
                f"⚠️ Failed to retrieve the next player: {error_msg}"
            )
            return ConversationHandler.END

        # Extract player data
        player_data = next_player_response.get("data", {}).get("data", {}).get("player")
        if not player_data:
            await update.message.reply_text(
                "⚠️ No more players in the auction queue. The auction might be complete."
            )
            return ConversationHandler.END

        # Update participant budgets if available in the API response
        api_participants = (
            next_player_response.get("data", {}).get("data", {}).get("participants", [])
        )
        if api_participants:
            # Create lookup by participant_id
            participant_lookup = {
                p.get("participant_id"): p
                for p in participants
                if p.get("participant_id")
            }

            # Update budget information
            for api_participant in api_participants:
                participant_id = api_participant.get("participant_id")
                if participant_id in participant_lookup:
                    participant_lookup[participant_id]["budget"] = api_participant.get(
                        "budget", 0
                    )
                    participant_lookup[participant_id]["players_owned"] = (
                        api_participant.get("players_owned", 0)
                    )

        # Initialize auction data FIRST
        base_price = float(player_data.get("base_price", 0))
        auction_data = ensure_auction_context(context, gully_id)
        auction_data.update(
            {
                "current_player": player_data,
                "auction_queue_id": player_data.get("auction_queue_id"),
                "all_participants": participants,
                "bids": [],
                "auction_active": True,  # Set this true BEFORE sending messages
                "has_base_bid": False,
                "base_price": base_price,
                "last_bidder": None,
                "bid_count": 0,
                "skipped_users": [],
            }
        )
        # Save the auction data to context FIRST
        set_auction_data(context, gully_id, auction_data)
        logger.info(
            f"Auction initialized and ACTIVE for player {player_data.get('name')}"
        )

        # Extract player details for display
        player_name = player_data.get("name", "Unknown Player")
        player_team = player_data.get("team", "Unknown Team")
        player_type = player_data.get("player_type", "Unknown Type")
        sold_price = player_data.get("sold_price", 0)

        # THEN send private messages
        await send_private_messages_to_participants(
            context, gully_id, participants, participant_user_map, player_data
        )

        # THEN send group message with bidding UI
        keyboard = [["Bid", "Skip"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            f"🏏 <b>{player_name}</b> ({player_team})\n"
            f"Type: {player_type}\n"
            f"Base: {base_price} CR\n"
            f"Sold Price 2025: {sold_price} CR\n\n"
            f"<b>BIDDING OPEN</b> - Press Bid or Skip",
            parse_mode="HTML",
            reply_markup=reply_markup,
        )

        # FINALLY start the timer
        timer = asyncio.create_task(
            scheduled_finalize_auction(context, chat_id, gully_id, BID_TIMEOUT_SECONDS)
        )
        context.chat_data[AUCTION_TIMER_KEY] = timer

        return BIDDING_STATE

    except Exception as e:
        logger.error(f"Error in next_player_command: {e}")
        logger.exception("Detailed error traceback:")
        await update.message.reply_text(
            "⚠️ Something went wrong while retrieving the next player. Please try again later."
        )
        return ConversationHandler.END


async def handle_bid_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Ultra-simplified bid handling:
    - Just tracks last bidder
    - Increments bid count
    - NO private messages
    - NO validation except for skip check
    """
    message_text = update.message.text.strip().lower()
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # CRITICAL FIX: Get gully_id from chat_id instead of context
    gully_id = ctx_manager.get_active_gully_id(context)

    # CRITICAL FIX: If gully_id is None, try to find it based on chat_id
    if gully_id is None:
        logger.warning(
            f"No active gully found in context, looking up by chat ID {chat_id}"
        )
        # Look in bot_data for a gully with this chat ID
        for g_id, g_data in context.bot_data.get("gullies", {}).items():
            if g_data.get("telegram_group_id") == chat_id:
                gully_id = g_id
                # Store it back as active
                ctx_manager.set_active_gully_id(context, gully_id)
                logger.info(f"Recovered gully_id {gully_id} from chat_id {chat_id}")
                break

        # If still None after lookup attempt, try direct API call
        if gully_id is None:
            try:
                logger.info(f"Attempting API lookup for gully by chat_id {chat_id}")
                onboarding_client = await get_initialized_onboarding_client()
                gully_data = await onboarding_client.get_gully_by_telegram_group_id(
                    chat_id
                )
                if gully_data:
                    gully_id = gully_data["id"]
                    ctx_manager.update_gully_data(context, gully_id, gully_data)
                    ctx_manager.set_active_gully_id(context, gully_id)
                    logger.info(f"Recovered gully_id {gully_id} from API")
            except Exception as e:
                logger.error(f"Error recovering gully_id via API: {e}")

    logger.info(f"Processing bid with gully_id: {gully_id}")

    # Get current auction data
    auction_data = get_auction_data(context, gully_id)
    if not auction_data:
        logger.warning(
            f"NO AUCTION DATA found for gully {gully_id} - attempting recovery"
        )
        # Try to recover auction data
        gully_data = context.bot_data.get("gullies", {}).get(gully_id, {})
        if "auction" in gully_data:
            auction_data = gully_data["auction"]
            logger.info(f"Recovered auction data from gully_data")
        else:
            # Create new auction data as last resort
            auction_data = ensure_auction_context(context, gully_id)

    # Second check after recovery attempt
    if not auction_data or not auction_data.get("auction_active", False):
        logger.warning(f"User {user_id} tried to bid but no active auction found")
        return BIDDING_STATE

    logger.info(
        f"Active auction found for gully {gully_id}, processing {message_text} command"
    )

    # Get participants
    participants = auction_data.get("all_participants", [])
    participant_user_map = ctx_manager.ensure_bot_gully_data(context, gully_id).get(
        "participant_user_map", {}
    )

    # Handle "skip" message
    if message_text == "skip":
        skipped_users = auction_data.get("skipped_users", [])

        # Check if already skipped
        if user_id in skipped_users:
            logger.info(f"User {user_id} already skipped this player")
            return BIDDING_STATE

        # Add to skipped users
        skipped_users.append(user_id)
        auction_data["skipped_users"] = skipped_users
        set_auction_data(context, gully_id, auction_data)

        # NO private message for skip

        # Check if all participants have skipped
        if len(skipped_users) >= len(participants):
            logger.info("All participants have skipped this player")
            clear_auction_timer(context)
            await finalize_auction_with_skip(context, chat_id, gully_id)

        return BIDDING_STATE

    # Handle "bid" message
    if message_text == "bid":
        # Check if already skipped
        if user_id in auction_data.get("skipped_users", []):
            # No message for rejected bid
            logger.info(f"User {user_id} tried to bid after skipping - rejected")
            return BIDDING_STATE

        # Find participant for this user
        participant = get_participant_for_user(
            participants, user_id, participant_user_map
        )

        # If not found, use minimal info
        if not participant:
            logger.warning(
                f"No participant found for user {user_id}, using minimal info"
            )
            participant = {"team_name": "Unknown Team", "participant_id": None}

        # Increment global bid counter
        global_bid_count = auction_data.get("bid_count", 0) + 1
        auction_data["bid_count"] = global_bid_count

        # Track the bid details
        bid_info = {
            "user_id": user_id,
            "participant_id": participant.get("participant_id"),
            "team_name": participant.get("team_name", "Unknown Team"),
            "timestamp": datetime.now().isoformat(),
            "bid_number": global_bid_count,  # Add the global bid number to this bid
        }

        # Add to bids list
        auction_data["bids"].append(bid_info)

        # Update last bidder - this person will get the player if timer expires now
        auction_data["last_bidder"] = bid_info

        # Calculate current bid amount
        base_price = float(auction_data.get("base_price", 0))
        if global_bid_count == 1:
            # First bid is same as base price
            current_amount = base_price
        else:
            # After first bid, add one increment per additional bid
            current_amount = base_price + ((global_bid_count - 1) * BID_INCREMENT)

        # Round to 2 decimal places instead of 1
        current_amount = round(current_amount, 2)

        # Log clear bid information with global counter
        logger.info(
            f"GLOBAL BID #{global_bid_count}: User {user_id} ({bid_info['team_name']}) - Amount: {current_amount} CR"
        )

        # Send message to group about the bid
        player_name = auction_data.get("current_player", {}).get(
            "name", "Unknown Player"
        )
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🏏 {bid_info['team_name']} bids {current_amount} CR for {player_name}!",
            )
        except Exception as e:
            logger.error(f"Error sending bid notification to group: {e}")

        # Save auction data BEFORE extending timer - CRITICAL
        set_auction_data(context, gully_id, auction_data)

        # Reset the timer
        await extend_auction_timer(context, chat_id, gully_id)

        return BIDDING_STATE

    # Ignore other messages
    return BIDDING_STATE


async def extend_auction_timer(context, chat_id, gully_id):
    """Extend or restart the auction timer after a bid."""
    # Clear existing timer
    clear_auction_timer(context)

    # !!! CRITICAL: Verify auction is still active before creating new timer
    auction_data = get_auction_data(context, gully_id)
    if not auction_data or not auction_data.get("auction_active"):
        logger.error(f"Auction data MISSING after clearing timer for gully {gully_id}!")
        # Attempt recovery by setting it active again
        auction_data = ensure_auction_context(context, gully_id)
        auction_data["auction_active"] = True
        set_auction_data(context, gully_id, auction_data)
        logger.info(f"Recovered auction data for gully {gully_id}")

    # Schedule new timer
    timer = asyncio.create_task(
        scheduled_finalize_auction(context, chat_id, gully_id, BID_TIMEOUT_SECONDS)
    )
    context.chat_data[AUCTION_TIMER_KEY] = timer
    logger.info(f"Extended auction timer for {BID_TIMEOUT_SECONDS} seconds")


async def scheduled_finalize_auction(context, chat_id, gully_id, delay):
    """Timer callback to finalize auction after timeout with simplified logic."""
    try:
        # Wait for delay period
        await asyncio.sleep(delay)

        # IMPORTANT: Get fresh auction data after timeout
        auction_data = get_auction_data(context, gully_id)
        if not auction_data or not auction_data.get("auction_active"):
            logger.info("No active auction to finalize")
            return

        # Check if any bids were placed
        global_bid_count = auction_data.get("bid_count", 0)
        logger.info(f"Finalizing auction with {global_bid_count} bids")

        if global_bid_count == 0:
            # No bids - skip player
            await finalize_auction_with_skip(context, chat_id, gully_id)
            return

        # Get the global bid count
        global_bid_count = auction_data.get("bid_count", 0)

        if global_bid_count == 0:
            # No bids - skip player
            await finalize_auction_with_skip(context, chat_id, gully_id)
            return

        # Extract necessary data from auction state - CRITICAL FIX
        base_price = round(float(auction_data.get("base_price", 0)), 2)
        player_data = auction_data.get("current_player", {})
        player_name = player_data.get("name", "Unknown Player")

        # Log all bids for debugging
        logger.info(f"AUCTION ENDED with {global_bid_count} total global bids")
        all_bids = auction_data.get("bids", [])
        for i, bid in enumerate(all_bids):
            logger.info(
                f"BID #{bid.get('bid_number')}: {bid.get('team_name')} at {bid.get('timestamp')}"
            )

        # Get last bidder - person who placed the last bid
        last_bidder = auction_data.get("last_bidder")
        if not last_bidder:
            logger.error(
                "No last bidder found but bids exist - this should never happen"
            )
            await finalize_auction_with_skip(context, chat_id, gully_id)
            return

        # Calculate final amount with FIRST BID SPECIAL RULE
        # First bid is same as base price, then each additional bid adds BID_INCREMENT
        if global_bid_count == 1:
            # First bid is same as base price
            total_amount = round(base_price, 2)
        else:
            # After first bid, add one increment per additional bid
            total_amount = round(
                base_price + ((global_bid_count - 1) * BID_INCREMENT), 2
            )

        # Round to 2 decimal places instead of 1
        total_amount = round(total_amount, 2)

        # Log calculation details
        if global_bid_count == 1:
            logger.info(
                f"PRICE CALCULATION: {base_price} (base price) = {total_amount} CR"
            )
        else:
            logger.info(
                f"PRICE CALCULATION: {base_price} (base) + "
                f"{(global_bid_count - 1) * BID_INCREMENT} (additional bids) = {total_amount} CR"
            )

        # Get bidder details
        team_name = last_bidder.get("team_name", "Unknown Team")
        participant_id = last_bidder.get("participant_id")
        user_id = last_bidder.get("user_id")

        # Log all winner details for debugging
        logger.info(
            f"WINNER DETAILS: User {user_id}, Team {team_name}, Participant ID {participant_id}"
        )
        logger.info(
            f"BID DETAILS: Total global bids {global_bid_count}, Final Amount {total_amount} CR"
        )

        # Announce winner in group chat
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🎉 {team_name} wins {player_name} for {total_amount} CR",
                reply_markup=ReplyKeyboardRemove(),
            )
        except Exception as e:
            logger.error(f"Error sending winner message: {e}")

        # Call API to resolve with winning bid
        try:
            auction_client = await get_initialized_auction_client()
            result = await auction_client.resolve_contested_player(
                player_id=player_data.get("player_id"),
                winning_participant_id=participant_id,
                auction_queue_id=auction_data["auction_queue_id"],
                bid_amount=total_amount,
            )

            if result.get("success"):
                logger.info(
                    f"Successfully resolved auction: {participant_id} wins {player_data.get('player_id')}"
                )
            else:
                logger.error(f"API error: {result.get('message')}")
        except Exception as e:
            logger.error(f"Error resolving auction: {e}")

        # Clear auction state
        auction_data["auction_active"] = False
        set_auction_data(context, gully_id, auction_data)

    except asyncio.CancelledError:
        logger.info("Auction timer was cancelled")
    except Exception as e:
        logger.error(f"Error in finalize timer: {e}")
        logger.exception("Detailed error traceback:")

        # Always clean up auction state even on error
        try:
            auction_data = get_auction_data(context, gully_id)
            if auction_data:
                auction_data["auction_active"] = False
                set_auction_data(context, gully_id, auction_data)

            await context.bot.send_message(
                chat_id=chat_id,
                text="Auction ended due to technical issues.",
                reply_markup=ReplyKeyboardRemove(),
            )
        except Exception as cleanup_e:
            logger.error(f"Error during cleanup: {cleanup_e}")


async def finalize_auction_with_skip(context, chat_id, gully_id):
    """Skip the current player and finalize the auction."""
    # Get auction data
    auction_data = get_auction_data(context, gully_id)
    if not auction_data:
        return

    player_data = auction_data.get("current_player", {})
    player_name = player_data.get("name", "Unknown Player")
    auction_queue_id = auction_data.get("auction_queue_id")

    # Call API to skip player
    try:
        auction_client = await get_initialized_auction_client()
        skip_result = await auction_client.skip_player(
            gully_id=gully_id, auction_queue_id=auction_queue_id
        )

        if skip_result.get("success"):
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"⏭️ {player_name} has been skipped",
                reply_markup=ReplyKeyboardRemove(),
            )
        else:
            logger.error(f"Error skipping player: {skip_result.get('message')}")
    except Exception as e:
        logger.error(f"Error in skip API call: {e}")

    # Clear auction state
    auction_data["auction_active"] = False
    set_auction_data(context, gully_id, auction_data)


async def manual_finalize_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manually finalize the current auction."""
    gully_id = ctx_manager.get_active_gully_id(context)
    chat_id = update.effective_chat.id

    # Validate active auction
    auction_data = get_auction_data(context, gully_id)
    if not auction_data or not auction_data.get("auction_active"):
        await update.message.reply_text("No active auction to finalize.")
        return BIDDING_STATE

    # Clear timer
    clear_auction_timer(context)

    # Call finalization with zero delay
    await scheduled_finalize_auction(context, chat_id, gully_id, 0)

    return ConversationHandler.END


async def send_message_with_retry(
    context,
    chat_id,
    text,
    parse_mode=None,
    reply_markup=None,
    disable_notification=False,
    max_retries=3,
):
    """Send a message with retry logic for network errors."""
    for attempt in range(max_retries):
        try:
            return await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
                disable_notification=disable_notification,
            )
        except Exception as e:
            if "NetworkError" in str(e) and attempt < max_retries - 1:
                logger.warning(
                    f"Network error when sending message (attempt {attempt+1}): {e}"
                )
                await asyncio.sleep(1)  # Wait 1 second before retrying
            else:
                if attempt == max_retries - 1:
                    logger.error(f"Failed to send message after {max_retries} attempts")
                else:
                    logger.error(f"Error sending message: {e}")
                return None


def get_handlers():
    """Get all handlers for auction queue features."""
    logger.info("Registering simplified auction queue handlers")

    # Command handlers
    next_player_handler = CommandHandler("next_player", next_player_command)
    finalize_handler = CommandHandler("finalize", manual_finalize_command)

    # Conversation handler for bidding state
    auction_conv_handler = ConversationHandler(
        entry_points=[next_player_handler],
        states={
            BIDDING_STATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_bid_message),
                finalize_handler,
            ]
        },
        fallbacks=[
            CommandHandler("cancel", lambda u, c: ConversationHandler.END),
            next_player_handler,
        ],
        name="auction_conversation",
        persistent=False,
        allow_reentry=True,  # Allow multiple entries
        per_chat=True,  # Track conversation per chat
        per_user=False,  # Don't track per user - critical to allow multiple users
        per_message=False,  # Don't track per message
    )

    # CRITICAL: Add a backup global handler for bids
    # This handler will catch ALL bid messages regardless of conversation state
    global_bid_handler = MessageHandler(
        filters.Regex(r"^[Bb]id$") & filters.ChatType.GROUPS, handle_bid_message
    )

    return [
        global_bid_handler,
        auction_conv_handler,
    ]  # Order matters! Put global handler first
