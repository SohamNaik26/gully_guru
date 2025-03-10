"""
Auction feature module for GullyGuru bot.
Handles player auctions, bidding, and auction status.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Replace bot services with direct API client import
from src.api.api_client_instance import api_client

# Configure logging
logger = logging.getLogger(__name__)


def get_auction_controls_markup():
    """
    Create the inline keyboard markup for auction controls.

    Returns:
        InlineKeyboardMarkup: The markup with auction control buttons
    """
    keyboard = [
        [
            InlineKeyboardButton("Next Player", callback_data="next_player"),
            InlineKeyboardButton("End Auction", callback_data="end_auction"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


async def update_auction_message(query, auction_status, is_admin):
    """
    Update the auction message with current status.

    Args:
        query: The callback query
        auction_status: The current auction status
        is_admin: Whether the user is an admin
    """
    if not auction_status or auction_status.get("status") == "inactive":
        await query.edit_message_text("No active auction in this gully.")
        return

    current_player = auction_status.get("current_player", {})
    if not current_player:
        await query.edit_message_text("No player currently up for auction.")
        return

    # Format player info
    player_name = current_player.get("name", "Unknown Player")
    player_role = current_player.get("role", "Unknown")
    player_team = current_player.get("team", "Unknown")
    base_price = current_player.get("base_price", 0)
    current_bid = auction_status.get("current_bid", base_price)
    current_bidder = auction_status.get("current_bidder", {})
    bidder_name = current_bidder.get("name", "No bids yet")

    message = (
        f"🏏 *Current Auction Player* 🏏\n\n"
        f"*Player:* {player_name}\n"
        f"*Role:* {player_role}\n"
        f"*Team:* {player_team}\n"
        f"*Base Price:* {base_price} credits\n"
        f"*Current Bid:* {current_bid} credits\n"
        f"*Current Bidder:* {bidder_name}\n\n"
    )

    # Create bid buttons
    keyboard = []
    bid_increments = [5, 10, 25, 50]
    bid_buttons = []

    for increment in bid_increments:
        bid_amount = current_bid + increment
        bid_buttons.append(
            InlineKeyboardButton(
                f"+{increment} ({bid_amount})", callback_data=f"bid_{bid_amount}"
            )
        )

    keyboard.append(bid_buttons)

    # Add admin controls if user is admin
    if is_admin:
        admin_buttons = [
            InlineKeyboardButton("Next Player", callback_data="next_player"),
            InlineKeyboardButton("End Auction", callback_data="end_auction"),
        ]
        keyboard.append(admin_buttons)

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        message, reply_markup=reply_markup, parse_mode="Markdown"
    )


async def auction_status_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle the /auction_status command.
    Shows the current auction status for the gully.
    """
    user = update.effective_user
    chat = update.effective_chat

    # Check if command is used in a group chat
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text(
            "This command can only be used in a group chat."
        )
        return

    # Ensure user exists in database - using API client directly
    db_user = await api_client.users.get_user(user.id)
    if not db_user:
        # Create user if not exists
        db_user = await api_client.users.create_user(
            telegram_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
        )

    if not db_user:
        await update.message.reply_text(
            "❌ Sorry, there was an error with your account. Please try again later."
        )
        return

    # Get gully for this chat - using API client directly
    gully = await api_client.gullies.get_gully_by_group(chat.id)
    if not gully:
        await update.message.reply_text(
            "This group is not registered as a gully. Please create a gully first."
        )
        return

    # Get current auction status - using API client directly
    auction_status = await api_client.fantasy.get_auction_status(gully["id"])

    if not auction_status or auction_status.get("status") == "inactive":
        # No active auction
        is_admin = (
            await api_client.gullies.get_user_gully_participation(
                user_id=db_user["id"], gully_id=gully["id"]
            )
            and await api_client.gullies.get_user_gully_participation(
                user_id=db_user["id"], gully_id=gully["id"]
            ).get("role")
            == "admin"
        )

        message = "No active auction in this gully."

        # Show admin options if user is admin
        if is_admin:
            keyboard = [
                [InlineKeyboardButton("Start Auction", callback_data="start_auction")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(message, reply_markup=reply_markup)
        else:
            await update.message.reply_text(message)

        return

    # Active auction exists
    current_player = auction_status.get("current_player", {})
    current_bid = auction_status.get("current_bid", {})

    if not current_player:
        await update.message.reply_text(
            "Auction is active but no player is currently being auctioned."
        )
        return

    # Format auction status message
    message = "🏏 *Current Auction Status* 🏏\n\n"
    message += f"*Player:* {current_player.get('name')}\n"
    message += f"*Team:* {current_player.get('team')}\n"
    message += f"*Type:* {current_player.get('player_type')}\n"
    message += f"*Base Price:* {current_player.get('base_price')} credits\n\n"

    if current_bid:
        bidder = current_bid.get("bidder_name", "Unknown")
        amount = current_bid.get("amount", 0)
        message += f"*Current Bid:* {amount} credits by {bidder}\n"
    else:
        message += "*No bids yet*\n"

    # Add bid buttons
    keyboard = []

    # Get user's available credits
    user_credits = await api_client.users.get_user_credits(db_user["id"], gully["id"])

    # Calculate bid amounts
    current_amount = current_bid.get("amount", current_player.get("base_price", 0))
    bid_increments = [5, 10, 20]

    bid_buttons = []
    for increment in bid_increments:
        bid_amount = current_amount + increment
        if user_credits >= bid_amount:
            bid_buttons.append(
                InlineKeyboardButton(
                    f"Bid {bid_amount}", callback_data=f"bid_{bid_amount}"
                )
            )

    if bid_buttons:
        keyboard.append(bid_buttons)

    # Add admin controls if user is admin
    is_admin = (
        await api_client.gullies.get_user_gully_participation(
            user_id=db_user["id"], gully_id=gully["id"]
        )
        and await api_client.gullies.get_user_gully_participation(
            user_id=db_user["id"], gully_id=gully["id"]
        ).get("role")
        == "admin"
    )
    if is_admin:
        admin_buttons = [
            InlineKeyboardButton("Next Player", callback_data="next_player"),
            InlineKeyboardButton("End Auction", callback_data="end_auction"),
        ]
        keyboard.append(admin_buttons)

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        message, reply_markup=reply_markup, parse_mode="Markdown"
    )


async def handle_auction_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle callbacks for auction actions.
    """
    query = update.callback_query
    await query.answer()

    user = query.from_user
    chat = query.message.chat
    data = query.data

    # Ensure user exists in database - using API client directly
    db_user = await api_client.users.get_user(user.id)
    if not db_user:
        # Create user if not exists
        db_user = await api_client.users.create_user(
            telegram_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
        )

    if not db_user:
        await query.edit_message_text(
            "❌ Sorry, there was an error with your account. Please try again later."
        )
        return

    # Get gully for this chat - using API client directly
    gully = await api_client.gullies.get_gully_by_group(chat.id)
    if not gully:
        await query.edit_message_text(
            "This group is not registered as a gully. Please create a gully first."
        )
        return

    # Check if user is admin - using API client directly
    participation = await api_client.gullies.get_user_gully_participation(
        user_id=db_user["id"], gully_id=gully["id"]
    )

    is_admin = participation and participation.get("role") == "admin"

    # Handle different callback actions
    if data.startswith("start_auction") and is_admin:
        # Start auction - using API client directly
        result = await api_client.fantasy.start_auction(gully["id"])
        if result:
            await query.edit_message_text(
                "✅ Auction has been started! Use the buttons below to manage the auction.",
                reply_markup=get_auction_controls_markup(),
            )
        else:
            await query.edit_message_text(
                "❌ Failed to start the auction. Please try again later."
            )

    elif data.startswith("next_player") and is_admin:
        # Move to next player - using API client directly
        result = await api_client.fantasy.next_auction_player(gully["id"])
        if result:
            # Get updated auction status
            auction_status = await api_client.fantasy.get_auction_status(gully["id"])
            await update_auction_message(query, auction_status, is_admin)
        else:
            await query.edit_message_text(
                "❌ Failed to move to the next player. Please try again later."
            )

    elif data.startswith("end_auction") and is_admin:
        # End auction - using API client directly
        result = await api_client.fantasy.end_auction(gully["id"])
        if result:
            await query.edit_message_text(
                "✅ Auction has been ended! All players have been assigned to teams."
            )
        else:
            await query.edit_message_text(
                "❌ Failed to end the auction. Please try again later."
            )

    elif data.startswith("bid_"):
        # Handle bid - using API client directly
        try:
            bid_amount = int(data.split("_")[1])
            result = await api_client.fantasy.place_bid(
                gully_id=gully["id"], user_id=db_user["id"], bid_amount=bid_amount
            )

            if result:
                # Get updated auction status
                auction_status = await api_client.fantasy.get_auction_status(
                    gully["id"]
                )
                await update_auction_message(query, auction_status, is_admin)
            else:
                await query.answer("Failed to place bid. Try again.")
        except (ValueError, IndexError):
            await query.answer("Invalid bid amount")

    else:
        await query.answer("Invalid action or insufficient permissions")
