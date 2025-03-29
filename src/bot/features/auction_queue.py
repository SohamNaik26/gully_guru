"""
Simplified auction queue features for the GullyGuru bot.
Handles the auction process for players, including bidding and skipping.
"""

import logging
import asyncio
from datetime import datetime
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
import re
import unicodedata

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


AUCTION_TIMER_KEY = "auction_timer"  # Timer for auction finalization
BID_INCREMENT = 0.5  # Fixed increment of 0.5 CR

# 1. Add constants for different timeout values
NO_BID_TIMEOUT = 15  # Default timeout (15 seconds)
LOW_BID_TIMEOUT = 30  # Timeout for auctions with 1-9 bids
HIGH_BID_TIMEOUT = 40  # Timeout for auctions with 10+ bids


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
    """Get auction data from context for a specific gully with improved handling."""
    # If no gully_id provided, try to get from chat_data first
    if gully_id is None:
        gully_id = context.chat_data.get("active_gully_id")
        if gully_id:
            logger.info(f"Found gully_id {gully_id} in chat_data")

        # If not found in chat_data, try context manager
        if not gully_id:
            gully_id = ctx_manager.get_active_gully_id(context)
            if gully_id:
                logger.info(f"Found gully_id {gully_id} from context manager")
            else:
                logger.error("No active gully_id found")
                return None

    # CRITICAL FIX: Convert string gully_id to int if needed
    if isinstance(gully_id, str) and gully_id.isdigit():
        gully_id = int(gully_id)

    # Try both string and int versions of gully_id to be safe
    gully_data = context.bot_data.get("gullies", {}).get(gully_id, None)
    if gully_data is None and isinstance(gully_id, int):
        # Try string version as fallback
        gully_data = context.bot_data.get("gullies", {}).get(str(gully_id), {})
    elif gully_data is None and isinstance(gully_id, str):
        # Try int version as fallback
        try:
            gully_data = context.bot_data.get("gullies", {}).get(int(gully_id), {})
        except ValueError:
            pass

    if not gully_data:
        logger.error(f"No gully data found for gully {gully_id}")
        return None

    auction_data = gully_data.get("auction")

    if not auction_data:
        logger.error(f"No auction data found for gully {gully_id}")
    elif not auction_data.get("auction_active"):
        logger.info(f"Auction for gully {gully_id} is not active")

    return auction_data


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
    Get the next player for auction with detailed team information including squad size.
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

        # Format the player info
        player_name = player_data.get("name", "Unknown Player")
        player_team = player_data.get("team", "Unknown Team")
        player_type = player_data.get("player_type", "Unknown Type")
        sold_price = player_data.get("sold_price", 0)

        # Create the message with detailed team information
        message_text = (
            f"🏏 <b>{player_name}</b> ({player_team})\n"
            f"Type: {player_type}\n"
            f"Base: {base_price} CR\n"
            f"Sold Price 2025: {sold_price} CR\n\n"
        )

        # Add team budget information section WITH PLAYER COUNT
        message_text += "<b>TEAM BUDGETS:</b>\n"
        participants_sorted = sorted(
            participants, key=lambda p: p.get("team_name", "Unknown")
        )

        for p in participants_sorted:
            team_name = p.get("team_name", "Unknown Team")
            budget = p.get("budget", 0)
            players_owned = p.get("players_owned", 0)  # Get players owned
            message_text += f"• {team_name}: {budget} CR (Squad: {players_owned}/18)\n"

        message_text += "\n<b>BIDDING OPEN</b> - Base price: {base_price} CR"

        # Create inline keyboard
        inline_keyboard = [
            [
                InlineKeyboardButton("🏏 BID 🏏", callback_data=f"bid_{gully_id}"),
                InlineKeyboardButton("⏭️ SKIP ⏭️", callback_data=f"skip_{gully_id}"),
            ]
        ]

        # Send announcement with inline keyboard
        try:
            announcement_message = await update.message.reply_text(
                message_text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard),
            )

            # Store the announcement message ID and message object for updating
            auction_data["announcement_message_id"] = announcement_message.message_id
            auction_data["last_bid_amount"] = base_price
            auction_data["last_bidder_name"] = "None"
            set_auction_data(context, gully_id, auction_data)

            # Try to pin the message, but handle permission errors gracefully
            try:
                await context.bot.pin_chat_message(
                    chat_id=chat_id,
                    message_id=announcement_message.message_id,
                    disable_notification=True,
                )
                logger.info(
                    f"Pinned auction announcement message {announcement_message.message_id}"
                )
            except Exception as e:
                logger.warning(f"Failed to pin message: {e}")
                logger.info("Continuing without pinning - this is not critical")

        except Exception as e:
            logger.error(f"Error sending auction announcement: {e}")
            await update.message.reply_text("Error starting auction. Please try again.")
            return ConversationHandler.END

        # Start the timer
        timer = asyncio.create_task(
            scheduled_finalize_auction(context, chat_id, gully_id, NO_BID_TIMEOUT)
        )
        context.chat_data[AUCTION_TIMER_KEY] = timer

        # Store active_gully_id in chat_data
        context.chat_data["active_gully_id"] = gully_id

        return BIDDING_STATE

    except Exception as e:
        logger.error(f"Error in next_player_command: {e}")
        logger.exception("Detailed error traceback:")
        await update.message.reply_text(
            "⚠️ Something went wrong while retrieving the next player. Please try again later."
        )
        return ConversationHandler.END


def validate_auction_state(auction_data, user_id):
    """Validate auction state before processing bid"""
    if not auction_data:
        return False, "No active auction"
    if not auction_data.get("auction_active"):
        return False, "Auction is not active"
    if user_id in auction_data.get("skipped_users", []):
        return False, "User has already skipped"
    return True, ""


# Modify handle_auction_message to log absolutely everything and be robust
async def handle_auction_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process ALL types of messages for bidding."""
    try:
        # Log the raw update at the very beginning
        logger.info(f"RAW UPDATE received: type={type(update)}")

        # Get user ID if available
        user_id = getattr(update.effective_user, "id", "Unknown")

        # Check if this is a message
        if not update.message:
            logger.info(f"Update from user {user_id} has no message")
            return

        # Check if message has text
        if not update.message.text:
            logger.info(f"Message from user {user_id} has no text")
            return

        # Get message text
        message_text = update.message.text.strip()
        chat_id = update.effective_chat.id

        # Log ALL message details for debugging
        logger.info(f"MESSAGE: '{message_text}' from user {user_id} in chat {chat_id}")

        # Check for any form of "BID" - extremely flexible matching
        contains_bid = "BID" in message_text.upper()
        if contains_bid:
            logger.info(f"BID detected in message from user {user_id}")

            # Get gully_id from chat_data
            gully_id = context.chat_data.get("active_gully_id")
            if not gully_id:
                logger.error(f"No active_gully_id in chat_data for chat {chat_id}")
                return

            logger.info(f"Found gully_id {gully_id} in chat_data")

            # Check auction state
            auction_data = get_auction_data(context, gully_id)
            if not auction_data:
                logger.error(f"No auction data found for gully {gully_id}")
                return

            if not auction_data.get("auction_active"):
                logger.error(f"Auction not active for gully {gully_id}")
                return

            # Process the bid
            logger.info(f"Processing bid for user {user_id}")
            await process_bid(update, context, gully_id)
    except Exception as e:
        # Catch ALL exceptions to ensure handler keeps working
        logger.error(f"Error in message handler: {e}")
        logger.exception("Detailed error traceback:")


# Streamlined bid processing - COMPLETE REPLACEMENT
async def process_bid(update: Update, context: ContextTypes.DEFAULT_TYPE, gully_id):
    """Process bid and ensure it's saved to auction state."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    try:
        logger.info(f"PROCESS_BID - START for user {user_id}")

        # Get auction data
        auction_data = get_auction_data(context, gully_id)
        if not auction_data:
            logger.error(f"No auction data found for gully {gully_id}")
            return

        if not auction_data.get("auction_active"):
            logger.error(f"Auction not active for gully {gully_id}")
            return

        # Check if user has already skipped
        if user_id in auction_data.get("skipped_users", []):
            logger.info(f"User {user_id} already skipped - rejecting bid")
            return

        # Find participant info
        participants = auction_data.get("all_participants", [])
        participant_user_map = ctx_manager.ensure_bot_gully_data(context, gully_id).get(
            "participant_user_map", {}
        )

        participant = get_participant_for_user(
            participants, user_id, participant_user_map
        )
        if not participant:
            logger.warning(f"No participant found for user {user_id}, using default")
            participant = {"team_name": "Unknown Team", "participant_id": None}

        # CRITICAL: Update bid count - THIS IS THE PART THAT'S FAILING
        current_bid_count = auction_data.get("bid_count", 0)
        new_bid_count = current_bid_count + 1

        logger.info(f"Updating bid count from {current_bid_count} to {new_bid_count}")

        # Calculate amount
        base_price = float(auction_data.get("base_price", 0))
        if new_bid_count == 1:
            current_amount = base_price
        else:
            current_amount = base_price + ((new_bid_count - 1) * BID_INCREMENT)
        current_amount = round(current_amount, 2)

        # Create bid info
        bid_info = {
            "user_id": user_id,
            "participant_id": participant.get("participant_id"),
            "team_name": participant.get("team_name", "Unknown Team"),
            "timestamp": datetime.now().isoformat(),
            "bid_number": new_bid_count,
            "amount": current_amount,
        }

        # Update auction data - CRITICAL PART
        auction_data["bid_count"] = new_bid_count
        auction_data["bids"].append(bid_info)
        auction_data["last_bidder"] = bid_info

        # CRITICAL: Save auction data BEFORE doing anything else
        set_auction_data(context, gully_id, auction_data)
        logger.info(f"✅ SAVED auction data with bid_count={new_bid_count}")

        # Get player name for message
        player_name = auction_data.get("current_player", {}).get(
            "name", "Unknown Player"
        )

        # Send confirmation
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🏏 {bid_info['team_name']} bids {current_amount} CR for {player_name}!",
        )

        # Extend timer
        await extend_auction_timer(context, chat_id, gully_id)

        logger.info(f"PROCESS_BID - COMPLETE for user {user_id}")

    except Exception as e:
        logger.error(f"Error in process_bid: {e}")
        logger.exception("Detailed error traceback:")


# Streamlined skip processing
async def process_skip(update: Update, context: ContextTypes.DEFAULT_TYPE, gully_id):
    """Process skip with minimal state updates."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # Get auction data
    auction_data = get_auction_data(context, gully_id)
    if not auction_data or not auction_data.get("auction_active"):
        return

    # Check if already skipped
    skipped_users = auction_data.get("skipped_users", [])
    if user_id in skipped_users:
        logger.info(f"User {user_id} already skipped this player")
        return

    # Add to skipped users list
    skipped_users.append(user_id)
    auction_data["skipped_users"] = skipped_users

    # Save state
    set_auction_data(context, gully_id, auction_data)

    # Check if all participants have skipped
    participants = auction_data.get("all_participants", [])
    if len(skipped_users) >= len(participants):
        logger.info("All participants have skipped this player")
        clear_auction_timer(context)
        await finalize_auction_with_skip(context, chat_id, gully_id)


def record_bid(auction_data, user_id, participant, bid_amount):
    """Safely record a bid with validation"""
    try:
        bid_info = {
            "user_id": user_id,
            "participant_id": participant.get("participant_id"),
            "team_name": participant.get("team_name", "Unknown Team"),
            "timestamp": datetime.now().isoformat(),
            "bid_number": auction_data.get("bid_count", 0) + 1,
            "amount": bid_amount,
        }

        auction_data["bids"].append(bid_info)
        auction_data["last_bidder"] = bid_info
        auction_data["bid_count"] = bid_info["bid_number"]

        logger.info(
            f"Recorded bid #{bid_info['bid_number']}: {bid_info['team_name']} - {bid_amount} CR"
        )
        return True

    except Exception as e:
        logger.error(f"Error recording bid: {e}")
        return False


# 2. Update the extend_auction_timer function to use adaptive timeouts
async def extend_auction_timer(context, chat_id, gully_id):
    """Extend or restart the auction timer with improved error handling."""
    try:
        logger.info(f"Extending auction timer for gully {gully_id}")

        # Clear existing timer safely
        if AUCTION_TIMER_KEY in context.chat_data:
            old_timer = context.chat_data[AUCTION_TIMER_KEY]
            try:
                old_timer.cancel()
                logger.info("Cancelled existing timer")
            except Exception as timer_e:
                logger.error(f"Error cancelling timer: {timer_e}")
            context.chat_data.pop(AUCTION_TIMER_KEY, None)

        # Verify auction is still active with safe gets
        auction_data = get_auction_data(context, gully_id)
        if not auction_data:
            logger.error(f"Cannot extend timer - no auction data for gully {gully_id}")
            return

        if not auction_data.get("auction_active"):
            logger.error(
                f"Cannot extend timer - auction not active for gully {gully_id}"
            )
            return

        # Set timeout based on bid count with safe gets
        bid_count = auction_data.get("bid_count", 0)

        # Set adaptive timeouts
        if bid_count == 0:
            timeout = 15  # No bids - 15 seconds
        elif bid_count < 10:
            timeout = 30  # 1-9 bids - 30 seconds
        else:
            timeout = 40  # 10+ bids - 40 seconds

        logger.info(f"Setting timer for {timeout} seconds ({bid_count} bids)")

        # Create new timer
        timer = asyncio.create_task(
            scheduled_finalize_auction(context, chat_id, gully_id, timeout)
        )
        context.chat_data[AUCTION_TIMER_KEY] = timer

    except Exception as e:
        logger.error(f"Error in extend_auction_timer: {e}")
        logger.exception("Timer extension error details:")


async def scheduled_finalize_auction(context, chat_id, gully_id, delay):
    """Timer callback to finalize auction after timeout."""
    try:
        logger.info(f"Starting auction timer for {delay} seconds")
        await asyncio.sleep(delay)

        # Check if auction is still active
        auction_data = get_auction_data(context, gully_id)
        if not auction_data or not auction_data.get("auction_active"):
            logger.info("Auction already finished when timer expired")
            return

        # Get bid info
        bid_count = auction_data.get("bid_count", 0)
        announcement_message_id = auction_data.get("announcement_message_id")

        # Process based on whether there are bids
        if bid_count == 0:
            # Update message to show skipped status
            player_data = auction_data.get("current_player", {})
            player_name = player_data.get("name", "Unknown Player")

            try:
                # Update the original message to show skip
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=announcement_message_id,
                    text=f"⏭️ <b>{player_name} has been SKIPPED</b>\nNo bids were received.",
                    parse_mode="HTML",
                    reply_markup=None,  # Remove the buttons
                )

                # Unpin the message
                try:
                    await context.bot.unpin_chat_message(
                        chat_id=chat_id, message_id=announcement_message_id
                    )
                    logger.info(
                        f"Unpinned auction announcement message {announcement_message_id}"
                    )
                except Exception as e:
                    logger.warning(f"Failed to unpin message: {e}")
                    logger.info("Continuing without unpinning - this is not critical")

            except Exception as e:
                logger.error(f"Error updating message on skip: {e}")

            await finalize_auction_with_skip(context, chat_id, gully_id)
            return

        # There are bids - process the winner
        last_bidder = auction_data.get("last_bidder")
        if not last_bidder:
            logger.error("No last bidder found but bids exist")
            await finalize_auction_with_skip(context, chat_id, gully_id)
            return

        # Calculate final amount
        base_price = float(auction_data.get("base_price", 0))
        if bid_count == 1:
            total_amount = base_price
        else:
            total_amount = base_price + ((bid_count - 1) * BID_INCREMENT)
        total_amount = round(total_amount, 2)

        # Get details
        team_name = last_bidder.get("team_name", "Unknown Team")
        participant_id = last_bidder.get("participant_id")
        player_data = auction_data.get("current_player", {})
        player_name = player_data.get("name", "Unknown Player")

        # Update the announcement message with winner info
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=announcement_message_id,
                text=f"🎉 <b>{player_name} SOLD!</b>\n"
                f"Winner: {team_name}\n"
                f"Final Price: {total_amount} CR\n"
                f"Total Bids: {bid_count}",
                parse_mode="HTML",
                reply_markup=None,  # Remove the buttons
            )

            # Unpin the message
            try:
                await context.bot.unpin_chat_message(
                    chat_id=chat_id, message_id=announcement_message_id
                )
                logger.info(
                    f"Unpinned auction announcement message {announcement_message_id}"
                )
            except Exception as e:
                logger.warning(f"Failed to unpin message: {e}")
                logger.info("Continuing without unpinning - this is not critical")

        except Exception as e:
            logger.error(f"Error updating message with winner: {e}")

        # Call API to resolve with winning bid
        try:
            auction_client = await get_initialized_auction_client()
            result = await auction_client.resolve_contested_player(
                player_id=player_data.get("player_id"),
                winning_participant_id=participant_id,
                auction_queue_id=auction_data["auction_queue_id"],
                bid_amount=total_amount,
            )

            if not result.get("success"):
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


async def finalize_auction_with_skip(context, chat_id, gully_id):
    """Skip the current player and update the original message."""
    # Get auction data
    auction_data = get_auction_data(context, gully_id)
    if not auction_data:
        return

    player_data = auction_data.get("current_player", {})
    player_name = player_data.get("name", "Unknown Player")
    auction_queue_id = auction_data.get("auction_queue_id")
    announcement_message_id = auction_data.get("announcement_message_id")

    # Call API to skip player
    try:
        auction_client = await get_initialized_auction_client()
        skip_result = await auction_client.skip_player(
            gully_id=gully_id, auction_queue_id=auction_queue_id
        )

        if not skip_result.get("success"):
            logger.error(f"Error skipping player: {skip_result.get('message')}")
    except Exception as e:
        logger.error(f"Error in skip API call: {e}")

    # Update the original message
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=announcement_message_id,
            text=f"⏭️ <b>{player_name} has been SKIPPED</b>\nNo bids were received.",
            parse_mode="HTML",
            reply_markup=None,  # Remove the buttons
        )

        # Unpin the message
        try:
            await context.bot.unpin_chat_message(
                chat_id=chat_id, message_id=announcement_message_id
            )
            logger.info(
                f"Unpinned auction announcement message {announcement_message_id}"
            )
        except Exception as e:
            logger.warning(f"Failed to unpin message: {e}")
            logger.info("Continuing without unpinning - this is not critical")

    except Exception as e:
        logger.error(f"Error updating message on skip: {e}")

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
    """Get all handlers for auction queue features with inline keyboard."""
    logger.info("Registering auction handlers with inline keyboard")

    # Command handlers
    next_player_handler = CommandHandler("next_player", next_player_command)
    finalize_handler = CommandHandler("finalize", manual_finalize_command)

    # Callback handler for inline keyboard buttons
    auction_button_handler = CallbackQueryHandler(
        handle_auction_button, pattern=r"^(bid|skip)_\d+$"
    )

    # REMOVED: No longer needed as we use inline keyboard callbacks
    # bid_message_handler = MessageHandler(...)
    # debug_handler = MessageHandler(...)

    return [
        auction_button_handler,  # Process inline button presses
        next_player_handler,  # Handle /next_player command
        finalize_handler,  # Handle /finalize command
    ]


async def handle_auction_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses from the inline keyboard."""
    query = update.callback_query
    await query.answer()  # Acknowledge the button press to Telegram

    # Extract data
    callback_data = query.data
    user_id = update.effective_user.id

    logger.info(f"INLINE BUTTON PRESS: {callback_data} from user {user_id}")

    # Parse callback data
    try:
        action, gully_id_str = callback_data.split("_")
        # CRITICAL FIX: Convert gully_id to integer
        gully_id = int(gully_id_str)

        logger.info(f"Parsed callback data: action={action}, gully_id={gully_id}")

        # Validate gully_id
        if not gully_id:
            logger.error(f"Invalid gully_id in callback data: {callback_data}")
            return

        # CRITICAL FIX: Ensure gully_id is in chat_data for future reference
        context.chat_data["active_gully_id"] = gully_id

        # Check auction state
        auction_data = get_auction_data(context, gully_id)
        if not auction_data:
            logger.error(f"No auction data found for gully {gully_id}")
            await query.edit_message_reply_markup(reply_markup=None)  # Remove buttons
            return

        if not auction_data.get("auction_active"):
            logger.error(f"Auction not active for gully {gully_id}")
            await query.edit_message_reply_markup(reply_markup=None)  # Remove buttons
            return

        if action == "bid":
            logger.info(f"BID button pressed by user {user_id}")
            await process_bid_from_callback(update, context, gully_id)
        elif action == "skip":
            logger.info(f"SKIP button pressed by user {user_id}")
            await process_skip_from_callback(update, context, gully_id)
    except Exception as e:
        logger.error(f"Error processing callback: {e}")
        logger.exception("Detailed error traceback:")


async def process_bid_from_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE, gully_id
):
    """Process bid with detailed team and bid information including squad size."""
    query = update.callback_query
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    try:
        logger.info(f"PROCESS_BID_CALLBACK - START for user {user_id}")

        # Convert gully_id to integer if needed
        if isinstance(gully_id, str):
            gully_id = int(gully_id)

        # Get auction data
        auction_data = get_auction_data(context, gully_id)
        if not auction_data:
            logger.error(f"No auction data found for gully {gully_id}")
            return

        if not auction_data.get("auction_active"):
            logger.error(f"Auction not active for gully {gully_id}")
            return

        # Check if user has already skipped
        if user_id in auction_data.get("skipped_users", []):
            logger.info(f"User {user_id} already skipped - rejecting bid")
            await query.answer("You've already skipped this player")
            return

        # Find participant info
        participants = auction_data.get("all_participants", [])
        participant_user_map = ctx_manager.ensure_bot_gully_data(context, gully_id).get(
            "participant_user_map", {}
        )

        participant = get_participant_for_user(
            participants, user_id, participant_user_map
        )
        if not participant:
            logger.warning(f"No participant found for user {user_id}, using default")
            participant = {"team_name": "Unknown Team", "participant_id": None}

        team_name = participant.get("team_name", "Unknown Team")

        # Update bid count
        current_bid_count = auction_data.get("bid_count", 0)
        new_bid_count = current_bid_count + 1

        logger.info(f"Updating bid count from {current_bid_count} to {new_bid_count}")

        # Calculate amount
        base_price = float(auction_data.get("base_price", 0))
        if new_bid_count == 1:
            current_amount = base_price
        else:
            current_amount = base_price + ((new_bid_count - 1) * BID_INCREMENT)
        current_amount = round(current_amount, 2)

        # Create bid info
        bid_info = {
            "user_id": user_id,
            "participant_id": participant.get("participant_id"),
            "team_name": team_name,
            "timestamp": datetime.now().isoformat(),
            "bid_number": new_bid_count,
            "amount": current_amount,
        }

        # Update auction data
        auction_data["bid_count"] = new_bid_count
        auction_data["bids"].append(bid_info)
        auction_data["last_bidder"] = bid_info
        auction_data["last_bid_amount"] = current_amount
        auction_data["last_bidder_name"] = team_name

        # Save auction data
        set_auction_data(context, gully_id, auction_data)
        logger.info(f"✅ SAVED auction data with bid_count={new_bid_count}")

        # Get player info
        player_name = auction_data.get("current_player", {}).get(
            "name", "Unknown Player"
        )
        player_team = auction_data.get("current_player", {}).get("team", "Unknown Team")
        player_type = auction_data.get("current_player", {}).get(
            "player_type", "Unknown Type"
        )
        sold_price = auction_data.get("current_player", {}).get("sold_price", 0)
        announcement_message_id = auction_data.get("announcement_message_id")

        # Prepare updated message with team budgets, skipped teams and bid history
        message_text = (
            f"🏏 <b>{player_name}</b> ({player_team})\n"
            f"Type: {player_type}\n"
            f"Base: {base_price} CR\n"
            f"Sold Price 2025: {sold_price} CR\n\n"
        )

        # Add current bid info
        message_text += (
            f"<b>CURRENT BID:</b> {current_amount} CR by {team_name}\n"
            f"Total Bids: {new_bid_count}\n\n"
        )

        # Add team budget information WITH PLAYER COUNT
        message_text += "<b>TEAM BUDGETS:</b>\n"
        participants_sorted = sorted(
            participants, key=lambda p: p.get("team_name", "Unknown")
        )

        for p in participants_sorted:
            p_team_name = p.get("team_name", "Unknown Team")
            budget = p.get("budget", 0)
            players_owned = p.get("players_owned", 0)  # Get players owned

            # Highlight the current bidder
            if p_team_name == team_name:
                message_text += f"• <b>{p_team_name}:</b> {budget} CR (Squad: {players_owned}/18) ⭐\n"
            else:
                message_text += (
                    f"• {p_team_name}: {budget} CR (Squad: {players_owned}/18)\n"
                )

        # Add skipped teams
        skipped_users = auction_data.get("skipped_users", [])
        if skipped_users:
            message_text += "\n<b>SKIPPED TEAMS:</b>\n"
            for skip_user_id in skipped_users:
                skip_participant = get_participant_for_user(
                    participants, skip_user_id, participant_user_map
                )
                if skip_participant:
                    skip_team_name = skip_participant.get("team_name", "Unknown Team")
                    message_text += f"• {skip_team_name}\n"

        # Create updated inline keyboard
        inline_keyboard = [
            [
                InlineKeyboardButton("🏏 BID 🏏", callback_data=f"bid_{gully_id}"),
                InlineKeyboardButton("⏭️ SKIP ⏭️", callback_data=f"skip_{gully_id}"),
            ]
        ]

        # Update the original message
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=announcement_message_id,
            text=message_text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard),
        )

        # Extend timer
        await extend_auction_timer(context, chat_id, gully_id)

        # Provide feedback
        await query.answer(f"Your bid of {current_amount} CR has been placed!")

        logger.info(f"PROCESS_BID_CALLBACK - COMPLETE for user {user_id}")

    except Exception as e:
        logger.error(f"Error in process_bid_from_callback: {e}")
        logger.exception("Detailed error traceback:")

        # Provide error feedback
        await query.answer("Error processing bid. Please try again.")


async def process_skip_from_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE, gully_id
):
    """Process skip with updated team information including squad size."""
    query = update.callback_query
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    try:
        logger.info(f"PROCESS_SKIP_CALLBACK - START for user {user_id}")

        # Get auction data
        if isinstance(gully_id, str):
            gully_id = int(gully_id)

        auction_data = get_auction_data(context, gully_id)
        if not auction_data or not auction_data.get("auction_active"):
            logger.error(f"No active auction found for gully {gully_id}")
            await query.answer("No active auction found")
            return

        # Check if already skipped
        skipped_users = auction_data.get("skipped_users", [])
        if user_id in skipped_users:
            logger.info(f"User {user_id} already skipped this player")
            await query.answer("You've already skipped this player")
            return

        # Find participant info
        participants = auction_data.get("all_participants", [])
        participant_user_map = ctx_manager.ensure_bot_gully_data(context, gully_id).get(
            "participant_user_map", {}
        )

        participant = get_participant_for_user(
            participants, user_id, participant_user_map
        )
        team_name = (
            participant.get("team_name", "Unknown Team")
            if participant
            else "Unknown Team"
        )

        # Add to skipped users
        skipped_users.append(user_id)
        auction_data["skipped_users"] = skipped_users

        # Save state
        set_auction_data(context, gully_id, auction_data)
        logger.info(
            f"User {user_id} ({team_name}) skipped - total skips: {len(skipped_users)}"
        )

        # Get player info for updated message
        player_data = auction_data.get("current_player", {})
        player_name = player_data.get("name", "Unknown Player")
        player_team = player_data.get("team", "Unknown Team")
        player_type = player_data.get("player_type", "Unknown Type")
        base_price = auction_data.get("base_price", 0)
        sold_price = player_data.get("sold_price", 0)
        announcement_message_id = auction_data.get("announcement_message_id")

        # Current bid info
        last_bid_amount = auction_data.get("last_bid_amount", base_price)
        last_bidder_name = auction_data.get("last_bidder_name", "None")
        bid_count = auction_data.get("bid_count", 0)

        # Prepare updated message with team budgets, skipped teams and bid history
        message_text = (
            f"🏏 <b>{player_name}</b> ({player_team})\n"
            f"Type: {player_type}\n"
            f"Base: {base_price} CR\n"
            f"Sold Price 2025: {sold_price} CR\n\n"
        )

        # Add current bid info if there are bids
        if bid_count > 0:
            message_text += (
                f"<b>CURRENT BID:</b> {last_bid_amount} CR by {last_bidder_name}\n"
                f"Total Bids: {bid_count}\n\n"
            )
        else:
            message_text += "<b>NO BIDS YET</b>\n\n"

        # Add team budget information WITH PLAYER COUNT
        message_text += "<b>TEAM BUDGETS:</b>\n"
        participants_sorted = sorted(
            participants, key=lambda p: p.get("team_name", "Unknown")
        )

        for p in participants_sorted:
            p_team_name = p.get("team_name", "Unknown Team")
            budget = p.get("budget", 0)
            players_owned = p.get("players_owned", 0)  # Get players owned

            # Bold the current high bidder if there is one
            if bid_count > 0 and p_team_name == last_bidder_name:
                message_text += f"• <b>{p_team_name}:</b> {budget} CR (Squad: {players_owned}/18) ⭐\n"
            else:
                message_text += (
                    f"• {p_team_name}: {budget} CR (Squad: {players_owned}/18)\n"
                )

        # Add updated skipped teams
        message_text += "\n<b>SKIPPED TEAMS:</b>\n"
        for skip_user_id in skipped_users:
            skip_participant = get_participant_for_user(
                participants, skip_user_id, participant_user_map
            )
            if skip_participant:
                skip_team_name = skip_participant.get("team_name", "Unknown Team")
                message_text += f"• {skip_team_name}\n"

        # Update inline keyboard
        inline_keyboard = [
            [
                InlineKeyboardButton("🏏 BID 🏏", callback_data=f"bid_{gully_id}"),
                InlineKeyboardButton("⏭️ SKIP ⏭️", callback_data=f"skip_{gully_id}"),
            ]
        ]

        # Update original message
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=announcement_message_id,
            text=message_text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard),
        )

        # Provide feedback
        await query.answer(f"You ({team_name}) have skipped this player")

        # Check if all participants have skipped
        if len(skipped_users) >= len(participants):
            logger.info("All participants have skipped this player")
            clear_auction_timer(context)
            await finalize_auction_with_skip(context, chat_id, gully_id)

        logger.info(f"PROCESS_SKIP_CALLBACK - COMPLETE for user {user_id}")

    except Exception as e:
        logger.error(f"Error in process_skip_from_callback: {e}")
        logger.exception("Detailed error traceback:")
        await query.answer("Error processing skip. Please try again.")

        # Provide feedback
        await query.answer(f"You ({team_name}) have skipped this player")

        # Check if all participants have skipped
        if len(skipped_users) >= len(participants):
            logger.info("All participants have skipped this player")
            clear_auction_timer(context)
            await finalize_auction_with_skip(context, chat_id, gully_id)

        logger.info(f"PROCESS_SKIP_CALLBACK - COMPLETE for user {user_id}")
