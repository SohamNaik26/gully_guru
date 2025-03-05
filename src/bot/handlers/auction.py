from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from typing import Dict, Any, List, Optional
from decimal import Decimal
import logging
import random
from datetime import datetime
import pytz

from src.bot.bot import api_client
from src.bot.keyboards.auction import get_auction_keyboard, get_bid_keyboard
from src.bot.utils.formatting import format_player_card
from src.bot.utils.auction import (
    calculate_min_bid_increment,
    calculate_max_bid,
    validate_team_composition,
)

# Conversation states
BID_AMOUNT = 1

logger = logging.getLogger(__name__)


async def auction_status_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle the /auction command to show current auction status."""
    user = update.effective_user

    # Get user from database
    db_user = await api_client.get_user(user.id)

    if not db_user:
        await update.message.reply_text(
            "You need to register first. Use /start to register."
        )
        return

    # Get auction status
    auction = await api_client.get_auction_status()

    if not auction or auction.get("status") != "active":
        await update.message.reply_text("There is no active auction at the moment.")
        return

    # Get current player
    current_player = auction.get("current_player")
    if not current_player:
        await update.message.reply_text("No player is currently being auctioned.")
        return

    # Format message
    message = "*Current Auction*\n\n"
    message += format_player_card(current_player)
    message += f"\n*Current Bid:* ₹{auction.get('current_bid', 0)} cr\n"

    if auction.get("highest_bidder"):
        message += f"*Highest Bidder:* {auction.get('highest_bidder')}\n\n"
    else:
        message += "*No bids yet*\n\n"

    # Add user's remaining budget
    message += f"*Your Remaining Budget:* ₹{db_user.get('budget', 0)} cr\n\n"

    # Add time remaining if available
    if auction.get("time_remaining"):
        message += f"*Time Remaining:* {auction.get('time_remaining')} seconds\n\n"

    # Create keyboard
    keyboard = get_auction_keyboard(auction, db_user.get("id"))

    # Send message
    if update.callback_query:
        await update.callback_query.edit_message_text(
            message, reply_markup=keyboard, parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            message, reply_markup=keyboard, parse_mode="Markdown"
        )


async def auction_history_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle the /auctionhistory command to show recent auction results."""
    user = update.effective_user

    # Get auction history
    history = await api_client.get_auction_history(limit=10)

    if not history:
        await update.message.reply_text("No auction history available yet.")
        return

    # Format history message
    message = "*Recent Auction Results*\n\n"

    for item in history:
        message += f"*{item['player_name']}* ({item['team']})\n"
        message += f"Sold for: ₹{item['sold_price']} cr\n"
        message += f"Bought by: {item['buyer_name']}\n\n"

    # Create keyboard
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("« Back to Menu", callback_data="nav_back_main")]]
    )

    await update.message.reply_text(
        message, reply_markup=keyboard, parse_mode="Markdown"
    )


async def bid_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> Optional[int]:
    """Handle the /bid command to place a bid in the auction."""
    user = update.effective_user

    # Get user from database
    db_user = await api_client.get_user(user.id)

    if not db_user:
        await update.message.reply_text(
            "You need to register first. Use /start to register."
        )
        return ConversationHandler.END

    # Get auction status
    auction = await api_client.get_auction_status()

    if not auction or auction.get("status") != "active":
        await update.message.reply_text("There is no active auction at the moment.")
        return ConversationHandler.END

    # Check if bid amount was provided
    if not context.args:
        # Show bid options
        current_player = auction.get("current_player")
        if not current_player:
            await update.message.reply_text("No player is currently being auctioned.")
            return ConversationHandler.END

        current_bid = Decimal(str(auction.get("current_bid", 0)))
        base_price = Decimal(str(current_player.get("base_price", 0)))

        # Calculate minimum bid based on current bid
        min_bid = calculate_min_bid(current_bid, base_price)

        message = (
            f"*Place a bid for {current_player['name']}*\n\n"
            f"Current Bid: ₹{current_bid} cr\n"
            f"Minimum Bid: ₹{min_bid} cr\n\n"
            f"Your Budget: ₹{db_user.get('budget', 0)} cr\n\n"
            f"Enter your bid amount using:\n/bid [amount]"
        )

        # Create keyboard with quick bid options
        keyboard = get_bid_keyboard(
            current_bid, base_price, Decimal(str(db_user.get("budget", 0)))
        )

        await update.message.reply_text(
            message, reply_markup=keyboard, parse_mode="Markdown"
        )
        return BID_AMOUNT

    # Process bid amount
    try:
        bid_amount = Decimal(context.args[0])
    except (ValueError, IndexError):
        await update.message.reply_text(
            "Invalid bid amount. Please enter a valid number."
        )
        return ConversationHandler.END

    # Get current player
    current_player = auction.get("current_player")
    if not current_player:
        await update.message.reply_text("No player is currently being auctioned.")
        return ConversationHandler.END

    # Validate bid
    current_bid = Decimal(str(auction.get("current_bid", 0)))
    base_price = Decimal(str(current_player.get("base_price", 0)))

    # Calculate minimum bid based on current bid
    min_bid = calculate_min_bid(current_bid, base_price)

    if bid_amount < min_bid:
        await update.message.reply_text(
            f"Your bid (₹{bid_amount} cr) is below the minimum bid (₹{min_bid} cr)."
        )
        return ConversationHandler.END

    if bid_amount > Decimal(str(db_user.get("budget", 0))):
        await update.message.reply_text(
            f"Your bid (₹{bid_amount} cr) exceeds your budget (₹{db_user.get('budget', 0)} cr)."
        )
        return ConversationHandler.END

    # Place bid
    result = await api_client.place_bid(
        user_id=db_user.get("id"),
        player_id=current_player.get("id"),
        bid_amount=float(bid_amount),
    )

    if result.get("success"):
        await update.message.reply_text(
            f"Your bid of ₹{bid_amount} cr has been placed successfully!"
        )

        # Notify group about new bid
        if update.effective_chat.type in ["group", "supergroup"]:
            await update.effective_chat.send_message(
                f"🔔 *New Bid Alert*\n\n"
                f"{user.username or user.first_name} has bid ₹{bid_amount} cr for {current_player['name']}!"
            )
    else:
        await update.message.reply_text(
            f"Failed to place bid: {result.get('error', 'Unknown error')}"
        )

    return ConversationHandler.END


async def quick_bid_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle quick bid button callback."""
    query = update.callback_query
    await query.answer()

    data = query.data
    user = update.effective_user

    # Extract bid amount
    bid_amount = Decimal(data.split("_")[-1])

    # Get user from database
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
    if not current_player:
        await query.edit_message_text("No player is currently being auctioned.")
        return

    # Validate bid
    if bid_amount > Decimal(str(db_user.get("budget", 0))):
        await query.edit_message_text(
            f"Your bid (₹{bid_amount} cr) exceeds your budget (₹{db_user.get('budget', 0)} cr)."
        )
        return

    # Place bid
    result = await api_client.place_bid(
        user_id=db_user.get("id"),
        player_id=current_player.get("id"),
        bid_amount=float(bid_amount),
    )

    if result.get("success"):
        # Show updated auction status
        await auction_status_command(update, context)

        # Notify group about new bid
        if update.effective_chat.type in ["group", "supergroup"]:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"🔔 *New Bid Alert*\n\n"
                f"{user.username or user.first_name} has bid ₹{bid_amount} cr for {current_player['name']}!",
                parse_mode="Markdown",
            )
    else:
        await query.edit_message_text(
            f"Failed to place bid: {result.get('error', 'Unknown error')}"
        )


async def auction_round_notification(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send notification about new auction round to all users."""
    job = context.job
    data = job.data

    player = data.get("player")
    user_ids = data.get("user_ids", [])
    group_id = data.get("group_id")

    if not player or not user_ids:
        logger.error("Missing data in auction round notification")
        return

    # Send notification to group
    if group_id:
        try:
            await context.bot.send_message(
                chat_id=group_id,
                text=f"🏏 *Auction Started for {player['name']}* 🏏\n\n"
                f"Base Price: ₹{player['base_price']} cr\n"
                f"Role: {player['player_type']}\n"
                f"Team: {player['team']}\n\n"
                f"You have 60 seconds to place your bids!\n"
                f"Use /auction to view details and place bids.",
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.error(f"Failed to send group notification: {e}")

    # Send private notifications to all users
    for user_id in user_ids:
        try:
            # Get user details
            user = await api_client.get_user_by_id(user_id)
            if not user:
                continue

            # Create personalized message with budget
            message = (
                f"🏏 *New Player Up for Auction* 🏏\n\n"
                f"{format_player_card(player)}\n\n"
                f"Base Price: ₹{player['base_price']} cr\n"
                f"Your Budget: ₹{user.get('budget', 0)} cr\n\n"
                f"Use the buttons below to place a bid:"
            )

            # Create keyboard with bid options based on user's budget
            keyboard = get_bid_keyboard(
                Decimal("0"),  # No bids yet
                Decimal(str(player["base_price"])),
                Decimal(str(user.get("budget", 0))),
            )

            # Send private message
            await context.bot.send_message(
                chat_id=user.get("telegram_id"),
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.error(f"Failed to notify user {user_id}: {e}")


async def auction_result_notification(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send notification about auction result to a user."""
    job = context.job
    data = job.data

    player = data.get("player")
    winner = data.get("winner")
    price = data.get("price", 0)
    user_id = data.get("user_id")
    remaining_budget = data.get("remaining_budget")

    if not player or not winner or not user_id:
        logger.error("Missing data in auction result notification")
        return

    try:
        # Get user details
        user = await api_client.get_user_by_id(user_id)
        if not user:
            return

        # Check if user is the winner
        is_winner = winner.get("id") == user_id

        # Create message
        if is_winner:
            message = (
                "🎉 *Congratulations!* 🎉\n\n"
                f"You won the auction for *{player['name']}*!\n"
                f"Final Price: ₹{price} cr\n\n"
                f"The amount has been deducted from your budget.\n"
                f"Remaining Budget: ₹{remaining_budget if remaining_budget is not None else user.get('budget', 0)} cr"
            )
        else:
            message = (
                "📢 *Auction Result* 📢\n\n"
                f"Player: *{player['name']}* ({player['team']})\n"
                f"Sold to: {winner.get('username', 'Unknown')}\n"
                f"Final Price: ₹{price} cr"
            )

        # Create keyboard
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("View My Team", callback_data="nav_team")],
                [InlineKeyboardButton("View Auction", callback_data="nav_auction")],
            ]
        )

        # Send notification
        await context.bot.send_message(
            chat_id=user.get("telegram_id"),
            text=message,
            reply_markup=keyboard,
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Failed to send auction result notification: {e}")


def calculate_min_bid(current_bid: Decimal, base_price: Decimal) -> Decimal:
    """Calculate minimum bid based on current bid and base price."""
    if current_bid == 0:
        return base_price

    # Apply bid increment rules
    if current_bid < 1:
        return current_bid + Decimal("0.10")  # +0.10 Cr for bids < 1 Cr
    elif current_bid < 2:
        return current_bid + Decimal("0.20")  # +0.20 Cr for bids < 2 Cr
    elif current_bid < 5:
        return current_bid + Decimal("0.50")  # +0.50 Cr for bids < 5 Cr
    else:
        return current_bid + Decimal("1.00")  # +1.00 Cr for bids >= 5 Cr


async def start_auction_rounds(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Start the auction rounds for contested players."""
    user = update.effective_user

    # Check if user is admin
    db_user = await api_client.get_user(user.id)

    if not db_user or not db_user.get("is_admin", False):
        await update.message.reply_text("Only admins can start auction rounds.")
        return

    # Get contested players
    contested_players = await api_client.get_contested_players()

    if not contested_players:
        await update.message.reply_text("No contested players found for auction.")
        return

    # Randomize the order of contested players
    random.shuffle(contested_players)

    # Store in context for later use
    context.bot_data["contested_players"] = contested_players
    context.bot_data["current_auction_index"] = 0

    # Start first auction round
    await start_next_auction_round(update, context)


async def start_next_auction_round(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Start the next auction round."""
    # Get contested players and current index
    contested_players = context.bot_data.get("contested_players", [])
    current_index = context.bot_data.get("current_auction_index", 0)

    # Check if we've auctioned all players
    if current_index >= len(contested_players):
        # All players auctioned
        if update.effective_chat.type in ["group", "supergroup"]:
            await update.effective_chat.send_message(
                "🎊 *Auction Complete!* 🎊\n\n"
                "All contested players have been auctioned.\n"
                "Use /myteam to view your final team."
            )
        return

    # Get next player
    player = contested_players[current_index]

    # Start auction for this player
    result = await api_client.start_auction_round(player["id"])

    if not result.get("success"):
        await update.effective_message.reply_text(
            f"Failed to start auction round: {result.get('error', 'Unknown error')}"
        )
        return

    # Increment index for next round
    context.bot_data["current_auction_index"] = current_index + 1

    # Get all users for notification
    users = await api_client.get_all_users()
    user_ids = [user["id"] for user in users]

    # Schedule notification
    context.job_queue.run_once(
        auction_round_notification,
        0,  # Send immediately
        data={
            "player": player,
            "user_ids": user_ids,
            "group_id": (
                update.effective_chat.id
                if update.effective_chat.type in ["group", "supergroup"]
                else None
            ),
        },
    )

    # Set timer for auction end
    context.job_queue.run_once(
        end_auction_round,
        60,  # 60 seconds for bidding
        data={"player_id": player["id"], "update": update, "context": context},
    )

    # Notify group
    if update.effective_chat.type in ["group", "supergroup"]:
        await update.effective_chat.send_message(
            f"🏏 *Auction Started for {player['name']}* 🏏\n\n"
            f"Base Price: ₹{player['base_price']} cr\n"
            f"Role: {player['player_type']}\n"
            f"Team: {player['team']}\n\n"
            f"You have 60 seconds to place your bids!\n"
            f"Use /auction to view details and place bids."
        )


async def end_auction_round(context: ContextTypes.DEFAULT_TYPE) -> None:
    """End the current auction round and process the result."""
    job = context.job
    data = job.data

    player_id = data.get("player_id")
    update = data.get("update")
    context_obj = data.get("context")

    if not player_id or not update or not context_obj:
        logger.error("Missing data in end_auction_round job")
        return

    # End the auction round
    result = await api_client.end_auction_round(player_id)

    if not result.get("success"):
        logger.error(
            f"Failed to end auction round: {result.get('error', 'Unknown error')}"
        )
        return

    # Get auction result
    auction_result = result.get("data", {})
    player = auction_result.get("player")
    winner = auction_result.get("winner")
    price = auction_result.get("price", 0)

    if not player or not winner:
        logger.error("Missing player or winner in auction result")
        return

    # Assign player to winner's team
    assign_result = await api_client.assign_player_to_user(
        user_id=winner.get("id"), player_id=player.get("id"), price=price
    )

    if not assign_result.get("success"):
        logger.error(
            f"Failed to assign player: {assign_result.get('error', 'Unknown error')}"
        )

    # Notify all users about the result
    users = await api_client.get_all_users()

    for user in users:
        context_obj.job_queue.run_once(
            auction_result_notification,
            0,  # Send immediately
            data={
                "player": player,
                "winner": winner,
                "price": price,
                "user_id": user["id"],
                "remaining_budget": user["id"] == winner.get("id")
                and user.get("budget", 0) - price,  # Show updated budget for winner
            },
        )

    # Notify group
    if update.effective_chat.type in ["group", "supergroup"]:
        await context_obj.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"🎉 *Auction Result* 🎉\n\n"
            f"Player: *{player['name']}* ({player['team']})\n"
            f"Sold to: {winner.get('username', 'Unknown')}\n"
            f"Final Price: ₹{price} cr",
            parse_mode="Markdown",
        )

    # Start next auction round after a delay
    context_obj.job_queue.run_once(
        lambda ctx: start_next_auction_round(update, context_obj),
        10,  # 10 second delay between rounds
    )


async def start_auction_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle the /start_auction command to begin the auction process."""
    user = update.effective_user

    # Check if user is admin
    db_user = await api_client.get_user(user.id)

    if not db_user or not db_user.get("is_admin", False):
        await update.message.reply_text("Only admins can start the auction.")
        return

    # Check if all users have submitted their initial squads
    status = await api_client.get_initial_squad_status(update.effective_chat.id)

    if not status or not status.get("all_submitted", False):
        await update.message.reply_text(
            "Not all users have submitted their initial squads. "
            "Please wait for all submissions before starting the auction."
        )
        return

    # Start the auction
    result = await api_client.start_auction(update.effective_chat.id)

    if not result or not result.get("success", False):
        await update.message.reply_text(
            f"Failed to start auction: {result.get('error', 'Unknown error')}"
        )
        return

    # Get auction details
    contested = result.get("data", {}).get("contested_players", [])
    uncontested = result.get("data", {}).get("uncontested_players", [])

    # Assign uncontested players to users
    for player_info in uncontested:
        player_id = player_info.get("player_id")
        user_id = player_info.get("user_id")
        price = player_info.get("price", 0)

        if player_id and user_id:
            assign_result = await api_client.assign_player_to_user(
                user_id=user_id, player_id=player_id, price=price
            )

            if not assign_result.get("success"):
                logger.error(
                    f"Failed to assign uncontested player: {assign_result.get('error')}"
                )

    # Send message to group
    message = (
        "🏏 *Fantasy Cricket Auction Starting* 🏏\n\n"
        f"Initial squad processing complete!\n\n"
        f"• *{len(uncontested)}* uncontested players have been assigned to their respective managers\n"
        f"• *{len(contested)}* contested players will now go to auction\n\n"
        "The auction will begin shortly. Get ready to bid!"
    )

    await update.message.reply_text(message, parse_mode="Markdown")

    # If there are contested players, start the auction rounds
    if contested:
        # Store contested players in context
        context.bot_data["contested_players"] = contested
        context.bot_data["current_auction_index"] = 0

        # Start auction rounds after a delay
        context.job_queue.run_once(
            lambda ctx: start_auction_rounds(update, context),
            10,  # 10 second delay before starting
        )
    else:
        await update.message.reply_text(
            "There are no contested players. The auction is complete!"
        )


async def extend_auction_timer(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Extend the auction timer by 15 seconds if a bid is placed near the end."""
    # Get current auction job
    current_jobs = context.job_queue.get_jobs_by_name("end_auction_round")

    if not current_jobs:
        logger.warning("No auction timer job found to extend")
        return

    # Get the first job (should be only one)
    job = current_jobs[0]

    # Calculate time remaining
    now = datetime.now(pytz.UTC)
    scheduled_time = job.next_t.replace(tzinfo=pytz.UTC)
    time_remaining = (scheduled_time - now).total_seconds()

    # If less than 15 seconds remaining, extend by 15 seconds
    if time_remaining < 15:
        # Remove current job
        job.schedule_removal()

        # Schedule new job 15 seconds from now
        new_time = 15
        context.job_queue.run_once(
            end_auction_round, new_time, name="end_auction_round", data=job.data
        )

        # Notify group about extension
        group_id = job.data.get("group_id")
        if group_id:
            await context.bot.send_message(
                chat_id=group_id,
                text="⏰ *Auction Extended*\n\n"
                "A new bid has been placed. The auction timer has been extended by 15 seconds.",
                parse_mode="Markdown",
            )

        logger.info(f"Auction timer extended by 15 seconds")


async def place_bid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Place a bid in the auction."""
    # Extract data from update
    if update.callback_query:
        query = update.callback_query
        await query.answer()

        # Extract bid amount from callback data
        data = query.data
        bid_amount = Decimal(data.split("_")[-1])
        user = query.from_user
    else:
        # Command-based bid
        message_parts = update.message.text.split()
        if len(message_parts) != 2:
            await update.message.reply_text("Please use the format: /bid [amount]")
            return

        try:
            bid_amount = Decimal(message_parts[1])
        except ValueError:
            await update.message.reply_text(
                "Invalid bid amount. Please enter a valid number."
            )
            return

        user = update.message.from_user

    # Get auction status
    auction = await api_client.get_auction_status()

    if not auction or auction.get("status") != "active":
        message = "There is no active auction at the moment."
        if update.callback_query:
            await update.callback_query.edit_message_text(message)
        else:
            await update.message.reply_text(message)
        return

    # Get current player
    current_player = auction.get("current_player")
    if not current_player:
        message = "No player is currently being auctioned."
        if update.callback_query:
            await update.callback_query.edit_message_text(message)
        else:
            await update.message.reply_text(message)
        return

    # Get user from database
    db_user = await api_client.get_user(user.id)

    if not db_user:
        message = "You need to register first. Use /start to register."
        if update.callback_query:
            await update.callback_query.edit_message_text(message)
        else:
            await update.message.reply_text(message)
        return

    # Check if user has enough budget
    if Decimal(str(db_user.get("budget", 0))) < bid_amount:
        message = f"You don't have enough budget to place this bid. Your budget: ₹{db_user.get('budget')} cr"
        if update.callback_query:
            await update.callback_query.edit_message_text(message)
        else:
            await update.message.reply_text(message)
        return

    # Get current bid and calculate minimum bid
    current_bid = Decimal(str(auction.get("current_bid", 0)))
    base_price = Decimal(str(current_player.get("base_price", 0)))
    min_bid = max(current_bid + calculate_min_bid_increment(current_bid), base_price)

    # Check if bid meets minimum requirement
    if bid_amount < min_bid:
        message = f"Your bid is too low. Minimum bid: ₹{min_bid} cr"
        if update.callback_query:
            await update.callback_query.edit_message_text(message)
        else:
            await update.message.reply_text(message)
        return

    # Get user's current team size
    user_team = await api_client.get_user_team(db_user.get("id"))
    remaining_slots = 18 - len(user_team)

    # Calculate max bid to ensure user can complete their squad
    max_possible_bid = calculate_max_bid(
        Decimal(str(db_user.get("budget", 0))), remaining_slots
    )

    if bid_amount > max_possible_bid:
        message = (
            f"This bid would leave you with insufficient funds to complete your squad.\n\n"
            f"Maximum recommended bid: ₹{max_possible_bid} cr\n"
            f"(This ensures you can acquire {remaining_slots-1} more players at minimum price)"
        )
        if update.callback_query:
            await update.callback_query.edit_message_text(message)
        else:
            await update.message.reply_text(message)
        return

    # Place bid
    result = await api_client.place_bid(
        user_id=db_user.get("id"),
        player_id=current_player.get("id"),
        bid_amount=float(bid_amount),
    )

    if not result.get("success"):
        message = f"Failed to place bid: {result.get('error', 'Unknown error')}"
        if update.callback_query:
            await update.callback_query.answer(message)
            await update.callback_query.edit_message_text(message)
        else:
            await update.message.reply_text(message)
        return

    # Confirm bid placement
    message = f"Your bid of ₹{bid_amount} cr has been placed successfully!"
    if update.callback_query:
        await update.callback_query.answer("Bid placed successfully!")
        await update.callback_query.edit_message_text(message)
    else:
        await update.message.reply_text(message)

    # Notify group about new bid
    if update.effective_chat.type in ["group", "supergroup"]:
        group_id = update.effective_chat.id
    else:
        group_id = context.bot_data.get("auction_group_id")

    if group_id:
        await context.bot.send_message(
            chat_id=group_id,
            text=f"🔔 *New Bid Alert*\n\n"
            f"{user.username or user.first_name} has bid ₹{bid_amount} cr for {current_player['name']}!",
            parse_mode="Markdown",
        )

    # Extend auction timer if bid is placed near the end
    await extend_auction_timer(context)
