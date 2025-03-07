from telegram import Update
from telegram.ext import ContextTypes
from decimal import Decimal

from src.bot.bot import api_client
from src.bot.handlers.auction import auction_status_command, quick_bid_callback
from src.bot.keyboards.auction import get_auction_history_keyboard


async def handle_auction_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle auction-related callbacks."""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "auction_refresh":
        # Refresh auction status
        await auction_status_command(update, context)

    elif data == "auction_history":
        # Show auction history
        history = await api_client.get_auction_history(limit=10)

        if not history:
            await query.edit_message_text(
                "No auction history available yet.",
                reply_markup=get_auction_history_keyboard(),
            )
            return

        # Format history message
        message = "*Recent Auction Results*\n\n"

        for item in history:
            message += f"*{item['player_name']}* ({item['team']})\n"
            message += f"Sold for: ₹{item['sold_price']} cr\n"
            message += f"Bought by: {item['buyer_name']}\n\n"

        await query.edit_message_text(
            message, reply_markup=get_auction_history_keyboard(), parse_mode="Markdown"
        )

    elif data.startswith("auction_bid_"):
        # Extract player_id
        player_id = int(data.split("_")[-1])

        # Get user
        user = update.effective_user
        db_user = await api_client.get_user(user.id)

        if not db_user:
            await query.edit_message_text(
                "You need to register first. Use /start to register."
            )
            return

        # Get auction status
        auction = await api_client.get_auction_status()

        if not auction or auction.get("status") != "active":
            await query.edit_message_text("There is no active auction at the moment.")
            return

        # Get current player
        current_player = auction.get("current_player")
        if not current_player or current_player["id"] != player_id:
            await query.edit_message_text(
                "This player is not currently being auctioned."
            )
            return

        # Show bid options
        current_bid = Decimal(str(auction.get("current_bid", 0)))
        base_price = Decimal(str(current_player.get("base_price", 0)))

        min_bid = max(current_bid + Decimal("0.5"), base_price)

        message = (
            f"*Place a bid for {current_player['name']}*\n\n"
            f"Current Bid: ₹{current_bid} cr\n"
            f"Minimum Bid: ₹{min_bid} cr\n\n"
            f"Your Budget: ₹{db_user['budget']} cr\n\n"
            f"Select a bid amount:"
        )

        # Create keyboard with quick bid options
        from src.bot.keyboards.auction import get_bid_keyboard

        keyboard = get_bid_keyboard(
            current_bid, base_price, Decimal(str(db_user["budget"]))
        )

        await query.edit_message_text(
            message, reply_markup=keyboard, parse_mode="Markdown"
        )

    elif data.startswith("auction_quick_bid_"):
        # Handle quick bid
        await quick_bid_callback(update, context)
