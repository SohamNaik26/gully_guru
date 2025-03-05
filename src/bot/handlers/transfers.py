from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler
from typing import Dict, Any, List, Optional
from decimal import Decimal
import logging
from datetime import datetime, timedelta
import pytz

from src.bot.bot import api_client
from src.bot.keyboards.transfers import (
    get_transfer_menu_keyboard,
    get_player_listing_keyboard,
    get_bid_confirmation_keyboard
)
from src.bot.utils.formatting import format_player_card, format_transfer_listing

# Conversation states
LISTING_PRICE = 1
BID_AMOUNT = 2

logger = logging.getLogger(__name__)

async def transfers_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /transfers command to show transfer menu."""
    user = update.effective_user
    
    # Get user from database
    db_user = await api_client.get_user(user.id)
    
    if not db_user:
        await update.message.reply_text(
            "You need to register first. Use /start to register."
        )
        return
    
    # Get current transfer window
    transfer_window = await api_client.get_current_transfer_window()
    
    if not transfer_window:
        await update.message.reply_text(
            "There is no active transfer window at the moment."
        )
        return
    
    # Format message based on window status
    if transfer_window.get("status") == "active":
        # Calculate time remaining
        end_time = datetime.fromisoformat(transfer_window.get("end_time").replace("Z", "+00:00"))
        now = datetime.now(pytz.UTC)
        time_remaining = end_time - now
        
        hours, remainder = divmod(time_remaining.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)
        
        message = (
            "🔄 *Transfer Window Open* 🔄\n\n"
            f"Week {transfer_window.get('week_number')}\n"
            f"Time Remaining: {int(hours)}h {int(minutes)}m\n\n"
            f"Your Budget: ₹{db_user.get('budget')} cr\n"
            f"Free Bids Used: {db_user.get('free_bids_used', 0)}/4\n\n"
            "Use the options below to navigate the transfer market:"
        )
    elif transfer_window.get("status") == "pending":
        # Calculate time until window opens
        start_time = datetime.fromisoformat(transfer_window.get("start_time").replace("Z", "+00:00"))
        now = datetime.now(pytz.UTC)
        time_until = start_time - now
        
        days, remainder = divmod(time_until.total_seconds(), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, _ = divmod(remainder, 60)
        
        message = (
            "🔜 *Transfer Window Opens Soon* 🔜\n\n"
            f"Week {transfer_window.get('week_number')}\n"
            f"Opens in: {int(days)}d {int(hours)}h {int(minutes)}m\n\n"
            f"Your Budget: ₹{db_user.get('budget')} cr\n\n"
            "The transfer window will open on Friday at 11 PM and remain open for 48 hours."
        )
    else:  # closed
        message = (
            "🔒 *Transfer Window Closed* 🔒\n\n"
            f"Week {transfer_window.get('week_number')}\n\n"
            f"Your Budget: ₹{db_user.get('budget')} cr\n\n"
            "The next transfer window will open on Friday at 11 PM."
        )
    
    # Create keyboard based on window status
    keyboard = get_transfer_menu_keyboard(transfer_window.get("status"))
    
    await update.message.reply_text(
        message, reply_markup=keyboard, parse_mode="Markdown"
    )

async def handle_transfer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[int]:
    """Handle transfer-related callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = update.effective_user
    
    # Get user from database
    db_user = await api_client.get_user(user.id)
    
    if not db_user:
        await query.edit_message_text(
            "You need to register first. Use /start to register."
        )
        return
    
    # Get current transfer window
    transfer_window = await api_client.get_current_transfer_window()
    
    if not transfer_window:
        await query.edit_message_text(
            "There is no active transfer window at the moment."
        )
        return
    
    if data == "view_available_players":
        # Show available players for transfer
        listings = await api_client.get_transfer_listings(status="available")
        
        if not listings:
            await query.edit_message_text(
                "There are no players available for transfer at the moment.\n\n"
                "You can list your own players for sale or check back later.",
                reply_markup=get_transfer_menu_keyboard(transfer_window.get("status"))
            )
            return
        
        # Format message
        message = "*Available Players for Transfer*\n\n"
        
        for i, listing in enumerate(listings, 1):
            player = listing.get("player", {})
            seller = listing.get("seller", {})
            
            message += (
                f"{i}. *{player.get('name')}* ({player.get('team')})\n"
                f"   Role: {player.get('player_type')}\n"
                f"   Min Price: ₹{listing.get('min_price')} cr\n"
                f"   Seller: {seller.get('username') or seller.get('first_name')}\n\n"
            )
        
        message += "Select a player to place a bid:"
        
        # Create keyboard
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{i}. {listing.get('player', {}).get('name')}", 
                                 callback_data=f"view_player_listing_{listing.get('id')}")] 
            for i, listing in enumerate(listings, 1)
        ] + [
            [InlineKeyboardButton("« Back to Transfers", callback_data="nav_transfers")]
        ])
        
        await query.edit_message_text(
            message, reply_markup=keyboard, parse_mode="Markdown"
        )
    
    elif data == "list_player_for_sale":
        # Show user's team to select a player to list
        team = await api_client.get_user_team(user.id)
        
        if not team or not team.get("players"):
            await query.edit_message_text(
                "You don't have any players to list for sale.",
                reply_markup=get_transfer_menu_keyboard(transfer_window.get("status"))
            )
            return
        
        # Format message
        message = "*Select a Player to List for Sale*\n\n"
        
        for i, player in enumerate(team.get("players", []), 1):
            message += (
                f"{i}. *{player.get('name')}* ({player.get('team')})\n"
                f"   Role: {player.get('player_type')}\n"
                f"   Base Price: ₹{player.get('base_price')} cr\n\n"
            )
        
        # Create keyboard
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{i}. {player.get('name')}", 
                                 callback_data=f"list_player_{player.get('id')}")] 
            for i, player in enumerate(team.get("players", []), 1)
        ] + [
            [InlineKeyboardButton("« Back to Transfers", callback_data="nav_transfers")]
        ])
        
        await query.edit_message_text(
            message, reply_markup=keyboard, parse_mode="Markdown"
        )
    
    elif data == "view_my_listings":
        # Show user's active listings
        listings = await api_client.get_user_listings(user.id, status="available")
        
        if not listings:
            await query.edit_message_text(
                "You don't have any active listings.",
                reply_markup=get_transfer_menu_keyboard(transfer_window.get("status"))
            )
            return
        
        # Format message
        message = "*Your Transfer Listings*\n\n"
        
        for i, listing in enumerate(listings, 1):
            player = listing.get("player", {})
            
            message += (
                f"{i}. *{player.get('name')}* ({player.get('team')})\n"
                f"   Role: {player.get('player_type')}\n"
                f"   Min Price: ₹{listing.get('min_price')} cr\n"
                f"   Bids: {len(listing.get('bids', []))}\n\n"
            )
        
        message += "Select a listing to view bids or cancel:"
        
        # Create keyboard
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{i}. {listing.get('player', {}).get('name')}", 
                                 callback_data=f"view_listing_{listing.get('id')}")] 
            for i, listing in enumerate(listings, 1)
        ] + [
            [InlineKeyboardButton("« Back to Transfers", callback_data="nav_transfers")]
        ])
        
        await query.edit_message_text(
            message, reply_markup=keyboard, parse_mode="Markdown"
        )
    
    elif data.startswith("view_player_listing_"):
        # Show details of a specific player listing
        listing_id = int(data.split("_")[-1])
        
        # Get listing details
        listing = await api_client.get_transfer_listing(listing_id)
        
        if not listing:
            await query.edit_message_text(
                "This listing is no longer available.",
                reply_markup=get_transfer_menu_keyboard(transfer_window.get("status"))
            )
            return
        
        # Format message
        message = format_transfer_listing(listing)
        
        # Create keyboard for bidding
        keyboard = get_player_listing_keyboard(listing, db_user)
        
        await query.edit_message_text(
            message, reply_markup=keyboard, parse_mode="Markdown"
        )
    
    elif data.startswith("list_player_"):
        # Start conversation to list player for sale
        player_id = int(data.split("_")[-1])
        
        # Store player_id in context
        context.user_data["listing_player_id"] = player_id
        
        # Get player details
        player = await api_client.get_player(player_id)
        
        if not player:
            await query.edit_message_text(
                "Player not found.",
                reply_markup=get_transfer_menu_keyboard(transfer_window.get("status"))
            )
            return
        
        # Format message
        message = (
            f"*List {player.get('name')} for Sale*\n\n"
            f"{format_player_card(player)}\n\n"
            "Enter the minimum price you want for this player (in cr):"
        )
        
        # Create keyboard with suggested prices
        base_price = Decimal(str(player.get('base_price', 1.0)))
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(f"₹{base_price} cr", callback_data=f"set_price_{base_price}"),
                InlineKeyboardButton(f"₹{base_price + Decimal('0.5')} cr", callback_data=f"set_price_{base_price + Decimal('0.5')}"),
            ],
            [
                InlineKeyboardButton(f"₹{base_price + Decimal('1.0')} cr", callback_data=f"set_price_{base_price + Decimal('1.0')}"),
                InlineKeyboardButton(f"₹{base_price + Decimal('2.0')} cr", callback_data=f"set_price_{base_price + Decimal('2.0')}"),
            ],
            [InlineKeyboardButton("Cancel", callback_data="nav_transfers")]
        ])
        
        await query.edit_message_text(
            message, reply_markup=keyboard, parse_mode="Markdown"
        )
        
        return LISTING_PRICE
    
    elif data.startswith("set_price_"):
        # Handle price selection for listing
        price = Decimal(data.split("_")[-1])
        player_id = context.user_data.get("listing_player_id")
        
        if not player_id:
            await query.edit_message_text(
                "Something went wrong. Please try again.",
                reply_markup=get_transfer_menu_keyboard(transfer_window.get("status"))
            )
            return ConversationHandler.END
        
        # Create listing
        listing = await api_client.create_transfer_listing(
            player_id=player_id,
            min_price=price,
            transfer_window_id=transfer_window.get("id")
        )
        
        if not listing:
            await query.edit_message_text(
                "Failed to create listing. Please try again.",
                reply_markup=get_transfer_menu_keyboard(transfer_window.get("status"))
            )
            return ConversationHandler.END
        
        # Get player details
        player = await api_client.get_player(player_id)
        
        # Confirm listing creation
        await query.edit_message_text(
            f"✅ *Player Listed for Sale*\n\n"
            f"{player.get('name')} has been listed for sale at ₹{price} cr.\n\n"
            f"You will be notified if someone places a bid.",
            reply_markup=get_transfer_menu_keyboard(transfer_window.get("status")),
            parse_mode="Markdown"
        )
        
        return ConversationHandler.END
    
    elif data.startswith("bid_on_listing_"):
        # Start conversation to place a bid
        listing_id = int(data.split("_")[-1])
        
        # Store listing_id in context
        context.user_data["bidding_listing_id"] = listing_id
        
        # Get listing details
        listing = await api_client.get_transfer_listing(listing_id)
        
        if not listing:
            await query.edit_message_text(
                "This listing is no longer available.",
                reply_markup=get_transfer_menu_keyboard(transfer_window.get("status"))
            )
            return ConversationHandler.END
        
        # Check if user has free bids left
        free_bids_used = db_user.get("free_bids_used", 0)
        is_free_bid = free_bids_used < 4
        bid_cost = "0.0" if is_free_bid else "0.1"
        
        # Format message
        player = listing.get("player", {})
        min_price = Decimal(str(listing.get("min_price", 0)))
        
        message = (
            f"*Place a Bid for {player.get('name')}*\n\n"
            f"{format_player_card(player)}\n\n"
            f"Minimum Price: ₹{min_price} cr\n"
            f"Your Budget: ₹{db_user.get('budget')} cr\n\n"
            f"Bid Cost: ₹{bid_cost} cr ({free_bids_used}/4 free bids used)\n\n"
            "Enter your bid amount (in cr):"
        )
        
        # Create keyboard with suggested bid amounts
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(f"₹{min_price} cr", callback_data=f"set_bid_{min_price}"),
                InlineKeyboardButton(f"₹{min_price + Decimal('0.5')} cr", callback_data=f"set_bid_{min_price + Decimal('0.5')}"),
            ],
            [
                InlineKeyboardButton(f"₹{min_price + Decimal('1.0')} cr", callback_data=f"set_bid_{min_price + Decimal('1.0')}"),
                InlineKeyboardButton(f"₹{min_price + Decimal('2.0')} cr", callback_data=f"set_bid_{min_price + Decimal('2.0')}"),
            ],
            [InlineKeyboardButton("Cancel", callback_data=f"view_player_listing_{listing_id}")]
        ])
        
        await query.edit_message_text(
            message, reply_markup=keyboard, parse_mode="Markdown"
        )
        
        return BID_AMOUNT
    
    elif data.startswith("set_bid_"):
        # Handle bid amount selection
        bid_amount = Decimal(data.split("_")[-1])
        listing_id = context.user_data.get("bidding_listing_id")
        
        if not listing_id:
            await query.edit_message_text(
                "Something went wrong. Please try again.",
                reply_markup=get_transfer_menu_keyboard(transfer_window.get("status"))
            )
            return ConversationHandler.END
        
        # Get listing details
        listing = await api_client.get_transfer_listing(listing_id)
        
        if not listing:
            await query.edit_message_text(
                "This listing is no longer available.",
                reply_markup=get_transfer_menu_keyboard(transfer_window.get("status"))
            )
            return ConversationHandler.END
        
        # Check if user has enough budget
        free_bids_used = db_user.get("free_bids_used", 0)
        is_free_bid = free_bids_used < 4
        bid_cost = Decimal("0.0") if is_free_bid else Decimal("0.1")
        
        total_cost = bid_amount + bid_cost
        
        if total_cost > Decimal(str(db_user.get("budget", 0))):
            await query.edit_message_text(
                f"❌ *Insufficient Budget*\n\n"
                f"Your bid (₹{bid_amount} cr) plus the bid fee (₹{bid_cost} cr) "
                f"exceeds your available budget of ₹{db_user.get('budget')} cr.",
                reply_markup=get_transfer_menu_keyboard(transfer_window.get("status")),
                parse_mode="Markdown"
            )
            return ConversationHandler.END
        
        # Confirm bid placement
        player = listing.get("player", {})
        
        message = (
            f"*Confirm Your Bid*\n\n"
            f"Player: {player.get('name')}\n"
            f"Your Bid: ₹{bid_amount} cr\n"
            f"Bid Fee: ₹{bid_cost} cr\n"
            f"Total Cost: ₹{total_cost} cr\n\n"
            f"Your Budget After Bid: ₹{Decimal(str(db_user.get('budget', 0))) - total_cost} cr\n\n"
            "Are you sure you want to place this bid?"
        )
        
        keyboard = get_bid_confirmation_keyboard(listing_id, bid_amount, is_free_bid)
        
        await query.edit_message_text(
            message, reply_markup=keyboard, parse_mode="Markdown"
        )
        
        return ConversationHandler.END
    
    elif data.startswith("confirm_bid_"):
        # Handle bid confirmation
        parts = data.split("_")
        listing_id = int(parts[2])
        bid_amount = Decimal(parts[3])
        is_free_bid = parts[4] == "true"
        
        # Place bid
        bid = await api_client.place_transfer_bid(
            listing_id=listing_id,
            bid_amount=bid_amount,
            is_free_bid=is_free_bid
        )
        
        if not bid:
            await query.edit_message_text(
                "Failed to place bid. Please try again.",
                reply_markup=get_transfer_menu_keyboard(transfer_window.get("status"))
            )
            return
        
        # Get listing details
        listing = await api_client.get_transfer_listing(listing_id)
        player = listing.get("player", {})
        
        # Confirm bid placement
        await query.edit_message_text(
            f"✅ *Bid Placed Successfully*\n\n"
            f"You have bid ₹{bid_amount} cr for {player.get('name')}.\n\n"
            f"You will be notified if your bid is accepted or if you are outbid.",
            reply_markup=get_transfer_menu_keyboard(transfer_window.get("status")),
            parse_mode="Markdown"
        )
    
    elif data.startswith("view_listing_"):
        # Show details of user's own listing
        listing_id = int(data.split("_")[-1])
        
        # Get listing details
        listing = await api_client.get_transfer_listing(listing_id)
        
        if not listing:
            await query.edit_message_text(
                "Listing not found.",
                reply_markup=get_transfer_menu_keyboard(transfer_window.get("status"))
            )
            return
        
        # Check if this is user's listing
        if listing.get("seller_id") != db_user.get("id"):
            await query.edit_message_text(
                "This is not your listing.",
                reply_markup=get_transfer_menu_keyboard(transfer_window.get("status"))
            )
            return
        
        # Format message
        player = listing.get("player", {})
        bids = listing.get("bids", [])
        
        message = (
            f"*Your Listing: {player.get('name')}*\n\n"
            f"{format_player_card(player)}\n\n"
            f"Minimum Price: ₹{listing.get('min_price')} cr\n"
            f"Status: {listing.get('status').capitalize()}\n\n"
        )
        
        if bids:
            message += "*Bids Received:*\n\n"
            
            for i, bid in enumerate(sorted(bids, key=lambda x: Decimal(str(x.get("bid_amount", 0))), reverse=True), 1):
                bidder = bid.get("bidder", {})
                message += (
                    f"{i}. ₹{bid.get('bid_amount')} cr from "
                    f"{bidder.get('username') or bidder.get('first_name')}\n"
                )
            
            # Create keyboard with accept/reject options for highest bid
            highest_bid = sorted(bids, key=lambda x: Decimal(str(x.get("bid_amount", 0))), reverse=True)[0]
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    f"Accept Bid: ₹{highest_bid.get('bid_amount')} cr", 
                    callback_data=f"accept_bid_{highest_bid.get('id')}"
                )],
                [InlineKeyboardButton(
                    "Cancel Listing", 
                    callback_data=f"cancel_listing_{listing_id}"
                )],
                [InlineKeyboardButton("« Back to My Listings", callback_data="view_my_listings")]
            ])
        else:
            message += "*No bids received yet.*\n\n"
            
            # Create keyboard with cancel option
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    "Cancel Listing", 
                    callback_data=f"cancel_listing_{listing_id}"
                )],
                [InlineKeyboardButton("« Back to My Listings", callback_data="view_my_listings")]
            ])
        
        await query.edit_message_text(
            message, reply_markup=keyboard, parse_mode="Markdown"
        )
    
    elif data.startswith("accept_bid_"):
        # Accept a bid
        bid_id = int(data.split("_")[-1])
        
        # Accept bid
        result = await api_client.accept_transfer_bid(bid_id)
        
        if not result:
            await query.edit_message_text(
                "Failed to accept bid. Please try again.",
                reply_markup=get_transfer_menu_keyboard(transfer_window.get("status"))
            )
            return
        
        # Confirm bid acceptance
        await query.edit_message_text(
            "✅ *Bid Accepted*\n\n"
            "The transfer has been completed successfully.\n\n"
            "The player has been transferred to the buyer's team and "
            "the bid amount has been added to your budget.",
            reply_markup=get_transfer_menu_keyboard(transfer_window.get("status")),
            parse_mode="Markdown"
        )
    
    elif data.startswith("cancel_listing_"):
        # Cancel a listing
        listing_id = int(data.split("_")[-1])
        
        # Cancel listing
        result = await api_client.cancel_transfer_listing(listing_id)
        
        if not result:
            await query.edit_message_text(
                "Failed to cancel listing. Please try again.",
                reply_markup=get_transfer_menu_keyboard(transfer_window.get("status"))
            )
            return
        
        # Confirm cancellation
        await query.edit_message_text(
            "✅ *Listing Cancelled*\n\n"
            "Your listing has been cancelled and the player remains in your team.",
            reply_markup=get_transfer_menu_keyboard(transfer_window.get("status")),
            parse_mode="Markdown"
        )
    
    elif data == "nav_transfers":
        # Navigate back to transfers menu
        await transfers_command(update, context)
    
    elif data == "view_my_bids":
        # Show user's active bids
        bids = await api_client.get_user_bids(db_user.get("id"), status="pending")
        
        if not bids:
            await query.edit_message_text(
                "You don't have any active bids.",
                reply_markup=get_transfer_menu_keyboard("active")
            )
            return
        
        # Format message
        message = "*Your Active Bids*\n\n"
        
        for i, bid in enumerate(bids, 1):
            listing = bid.get("listing", {})
            player = listing.get("player", {})
            
            # Get highest bid for this listing
            all_bids = listing.get("bids", [])
            highest_bid = sorted(all_bids, key=lambda x: Decimal(str(x.get("bid_amount", 0))), reverse=True)[0]
            is_highest = highest_bid.get("id") == bid.get("id")
            
            message += (
                f"{i}. *{player.get('name')}* ({player.get('team')})\n"
                f"   Your Bid: ₹{bid.get('bid_amount')} cr\n"
                f"   Status: {'Highest Bid ✅' if is_highest else 'Outbid ❌'}\n"
            )
            
            if not is_highest:
                message += f"   Highest Bid: ₹{highest_bid.get('bid_amount')} cr\n"
            
            message += "\n"
        
        message += "Select a bid to update:"
        
        # Create keyboard
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{i}. {bid.get('listing', {}).get('player', {}).get('name')}", 
                                 callback_data=f"view_player_listing_{bid.get('listing', {}).get('id')}")] 
            for i, bid in enumerate(bids, 1)
        ] + [
            [InlineKeyboardButton("« Back to Transfers", callback_data="nav_transfers")]
        ])
        
        await query.edit_message_text(
            message, reply_markup=keyboard, parse_mode="Markdown"
        )
    
    return ConversationHandler.END

# Add this to the conversation handlers in main.py
transfer_listing_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(handle_transfer_callback, pattern=r"^list_player_\d+$")
    ],
    states={
        LISTING_PRICE: [
            CallbackQueryHandler(handle_transfer_callback, pattern=r"^set_price_\d+(\.\d+)?$"),
            CallbackQueryHandler(handle_transfer_callback, pattern=r"^nav_transfers$")
        ]
    },
    fallbacks=[
        CommandHandler("cancel", lambda u, c: ConversationHandler.END)
    ]
)

transfer_bid_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(handle_transfer_callback, pattern=r"^bid_on_listing_\d+$")
    ],
    states={
        BID_AMOUNT: [
            CallbackQueryHandler(handle_transfer_callback, pattern=r"^set_bid_\d+(\.\d+)?$"),
            CallbackQueryHandler(handle_transfer_callback, pattern=r"^view_player_listing_\d+$")
        ]
    },
    fallbacks=[
        CommandHandler("cancel", lambda u, c: ConversationHandler.END)
    ]
)

async def schedule_transfer_deadline_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Schedule a job to process transfers at the deadline."""
    # Get current transfer window
    transfer_window = await api_client.get_current_transfer_window()
    
    if not transfer_window or transfer_window.get("status") != "active":
        return
    
    # Calculate when the window ends
    end_time = datetime.fromisoformat(transfer_window.get("end_time").replace("Z", "+00:00"))
    now = datetime.now(pytz.UTC)
    
    if end_time <= now:
        # Window already ended, process immediately
        await process_transfer_deadline(context)
    else:
        # Schedule job for when window ends
        seconds_until_end = (end_time - now).total_seconds()
        
        context.job_queue.run_once(
            process_transfer_deadline,
            seconds_until_end,
            data={"window_id": transfer_window.get("id")}
        )
        
        logger.info(f"Scheduled transfer deadline job for {end_time} ({seconds_until_end} seconds from now)")

async def process_transfer_deadline(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process all transfers at the deadline."""
    job = context.job
    window_id = job.data.get("window_id") if job and job.data else None
    
    # Process transfers
    result = await api_client.process_transfer_deadline(window_id)
    
    if not result or not result.get("success"):
        logger.error(f"Failed to process transfer deadline: {result.get('error', 'Unknown error')}")
        return
    
    # Get all users
    users = await api_client.get_all_users()
    
    # Notify all users about the transfer results
    for user in users:
        try:
            # Get user's completed transfers (both buying and selling)
            transfers = await api_client.get_user_transfer_results(user.get("id"))
            
            if not transfers:
                # No transfers for this user
                await context.bot.send_message(
                    chat_id=user.get("telegram_id"),
                    text=(
                        "📊 *Transfer Window Closed* 📊\n\n"
                        "The transfer window has now closed.\n\n"
                        "You did not complete any transfers in this window.\n\n"
                        "The next transfer window will open on Friday at 11 PM."
                    ),
                    parse_mode="Markdown"
                )
                continue
            
            # Format message with transfer results
            message = (
                "📊 *Transfer Window Results* 📊\n\n"
                "The transfer window has now closed. Here's a summary of your transfers:\n\n"
            )
            
            # Add sold players
            sold = transfers.get("sold", [])
            if sold:
                message += "*Players Sold:*\n"
                for transfer in sold:
                    player = transfer.get("player", {})
                    buyer = transfer.get("buyer", {})
                    price = transfer.get("price", 0)
                    
                    message += (
                        f"• {player.get('name')} to {buyer.get('username')} for ₹{price} cr\n"
                    )
                message += "\n"
            
            # Add bought players
            bought = transfers.get("bought", [])
            if bought:
                message += "*Players Bought:*\n"
                for transfer in bought:
                    player = transfer.get("player", {})
                    seller = transfer.get("seller", {})
                    price = transfer.get("price", 0)
                    
                    message += (
                        f"• {player.get('name')} from {seller.get('username')} for ₹{price} cr\n"
                    )
                message += "\n"
            
            # Add budget update
            message += (
                f"*Updated Budget:* ₹{user.get('budget')} cr\n\n"
                "The next transfer window will open on Friday at 11 PM."
            )
            
            # Send notification
            await context.bot.send_message(
                chat_id=user.get("telegram_id"),
                text=message,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Error notifying user {user.get('id')} about transfer results: {e}") 

async def view_transfer_results_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /transfer_results command to show results of the last transfer window."""
    user = update.effective_user
    
    # Get user from database
    db_user = await api_client.get_user(user.id)
    
    if not db_user:
        await update.message.reply_text(
            "You need to register first. Use /start to register."
        )
        return
    
    # Get user's transfer results
    transfers = await api_client.get_user_transfer_results(db_user.get("id"))
    
    if not transfers:
        await update.message.reply_text(
            "You did not complete any transfers in the last window.",
            parse_mode="Markdown"
        )
        return
    
    # Format message with transfer results
    message = (
        "📊 *Your Last Transfer Window Results* 📊\n\n"
    )
    
    # Add sold players
    sold = transfers.get("sold", [])
    if sold:
        message += "*Players Sold:*\n"
        for transfer in sold:
            player = transfer.get("player", {})
            buyer = transfer.get("buyer", {})
            price = transfer.get("price", 0)
            
            message += (
                f"• {player.get('name')} to {buyer.get('username')} for ₹{price} cr\n"
            )
        message += "\n"
    
    # Add bought players
    bought = transfers.get("bought", [])
    if bought:
        message += "*Players Bought:*\n"
        for transfer in bought:
            player = transfer.get("player", {})
            seller = transfer.get("seller", {})
            price = transfer.get("price", 0)
            
            message += (
                f"• {player.get('name')} from {seller.get('username')} for ₹{price} cr\n"
            )
        message += "\n"
    
    # Add budget update
    message += f"*Current Budget:* ₹{db_user.get('budget')} cr\n"
    
    await update.message.reply_text(
        message,
        parse_mode="Markdown"
    ) 