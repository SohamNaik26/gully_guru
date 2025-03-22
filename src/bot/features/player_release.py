"""
Player release features for the GullyGuru bot.
Handles the release of uncontested players during the auction release window.
"""

import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
)

# Use the centralized client initialization
from src.bot.api_client.init import (
    get_initialized_onboarding_client,
    get_initialized_auction_client,
    wait_for_api,
)
from src.bot.context import manager as ctx_manager
from src.bot.utils.callback_utils import (
    create_callback_data,
    parse_callback_data,
    create_callback_pattern,
)

# Configure logging
logger = logging.getLogger(__name__)

# Conversation states
SELECTING_PLAYERS_TO_RELEASE = 1
RELEASE_WINDOW_MINUTES = 1

# Module identifier constant
MODULE_ID = "release"  # Short but descriptive


def create_release_callback(action: str, data: Dict[str, Any] = None) -> str:
    """Create a callback specific to the player release feature."""
    return create_callback_data(MODULE_ID, action, data)


async def can_release_players(context, gully_id, participant_id):
    """Check if the release window is open for the participant."""
    # Get gully data which should contain the context about timing
    gully_data = context.bot_data.get("gully_data", {}).get(gully_id)

    # If no gully data found, fetch it from API
    if not gully_data:
        api_client = await get_initialized_onboarding_client()
        gully_data = await api_client.get_gully(gully_id)
        if not gully_data:
            return False

        # Cache the gully data
        if "gully_data" not in context.bot_data:
            context.bot_data["gully_data"] = {}
        context.bot_data["gully_data"][gully_id] = gully_data

    # Check if gully is in release window using context manager
    is_open = ctx_manager.is_release_window_open(context, gully_id)
    if is_open:
        return True

    # If not explicitly open in context, check based on gully status
    gully_status = gully_data.get("status", "").lower()
    return gully_status in ["auction", "release"]


async def release_players_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> Optional[int]:
    """
    Handle the /release_players command.
    This command allows participants to select players to release during the release window.
    """
    logger.info(f"Release: Command called by user {update.effective_user.id}")

    # Simply check if API is available without parameters
    if not await wait_for_api():
        await update.message.reply_text(
            "⚠️ API is currently unavailable. Please try again later."
        )
        return ConversationHandler.END

    # 1. Get the telegram user
    telegram_user_id = update.effective_user.id

    # Get active gully ID
    active_gully_id = ctx_manager.get_active_gully_id(context)

    # 2. Check if user has already submitted releases for this gully
    if ctx_manager.is_release_submitted(context, active_gully_id):
        await update.message.reply_text(
            "🚫 You have already submitted your player releases."
        )
        return ConversationHandler.END

    try:
        # 3. Get user from database
        client = await get_initialized_onboarding_client()
        db_user = await client.get_user_by_telegram_id(telegram_user_id)

        if not db_user:
            await update.message.reply_text(
                "⚠️ Your account was not found. Please use /start to register."
            )
            return ConversationHandler.END

        user_id = db_user["id"]

        # 4. Get gully ID - first try from context, then from available gullies
        if not active_gully_id:
            # Try to find an active gully for this user
            user_gullies = await client.get_user_gullies(user_id)

            if not user_gullies:
                await update.message.reply_text(
                    "⚠️ You are not a participant in any gully."
                )
                return ConversationHandler.END

            # Use the first gully (could be refined to use one that's in auction state)
            active_gully_id = user_gullies[0]["id"]
            ctx_manager.set_active_gully_id(context, active_gully_id)

        # 5. Get the participant ID for this user in this gully
        participant = await client.get_participant_by_user_and_gully(
            user_id=user_id, gully_id=active_gully_id
        )

        if not participant:
            await update.message.reply_text(
                "⚠️ You are not registered as a participant in the active gully."
            )
            return ConversationHandler.END

        participant_id = participant["id"]
        logger.info(
            f"Found participant_id: {participant_id} for user {user_id} in gully {active_gully_id}"
        )

        # Store participant ID in gully-specific context
        ctx_manager.set_participant_id(context, participant_id, active_gully_id)
        ctx_manager.set_team_name(
            context, participant.get("team_name", "Your Team"), active_gully_id
        )

        # 6. Check if release window is open for this gully
        if not await can_release_players(context, active_gully_id, participant_id):
            await update.message.reply_text(
                "⚠️ The release window is not currently open for your gully."
            )
            return ConversationHandler.END

        # Try to get uncontested players from context first
        uncontested_players = ctx_manager.get_uncontested_players(
            context, active_gully_id
        )
        logger.info(
            f"Retrieved {len(uncontested_players)} uncontested players from context"
        )

        # If no players in context, fetch from API
        if not uncontested_players:
            logger.info("No uncontested players in context, fetching from API")
            auction_client = await get_initialized_auction_client()
            uncontested_response = await auction_client.get_uncontested_players(
                active_gully_id
            )

            logger.info(f"Uncontested API response: {uncontested_response}")

            # Extract participant-specific players from the response
            participant_players = []

            if uncontested_response:
                # Navigate through nested structure: data -> data -> participants
                try:
                    data = uncontested_response.get("data", {})
                    logger.info(f"First level data: {data}")

                    # Check for nested data structure
                    if "data" in data:
                        nested_data = data.get("data", {})
                        logger.info(f"Second level data: {nested_data}")

                        # Extract participants list
                        participants_list = nested_data.get("participants", [])
                        logger.info(
                            f"Found {len(participants_list)} participants in response"
                        )

                        # Find current participant's data
                        for p in participants_list:
                            p_id = p.get("participant_id")
                            logger.info(
                                f"Checking participant {p_id} vs current {participant_id}"
                            )

                            if p_id == participant_id:
                                # Found the current participant's data
                                player_list = p.get("players", [])
                                logger.info(
                                    f"Found {len(player_list)} players for participant {participant_id}"
                                )

                                # Convert each player to standardized format
                                for player in player_list:
                                    standardized_player = standardize_player_data(
                                        player
                                    )
                                    # Add participant info to each player
                                    if not standardized_player.get("participants"):
                                        standardized_player["participants"] = [
                                            {
                                                "participant_id": participant_id,
                                                "team_name": participant.get(
                                                    "team_name", "Your Team"
                                                ),
                                            }
                                        ]
                                    participant_players.append(standardized_player)

                                break
                except Exception as e:
                    logger.error(f"Error extracting players from response: {e}")
                    logger.exception("Detailed extraction error:")

            # Store the extracted players in context
            if participant_players:
                logger.info(
                    f"Storing {len(participant_players)} player(s) for participant {participant_id}"
                )
                ctx_manager.set_uncontested_players(
                    context, active_gully_id, participant_players
                )
                uncontested_players = participant_players
            else:
                logger.warning(f"No players found for participant {participant_id}")

        # If we still don't have any players, inform the user
        if not uncontested_players:
            await update.message.reply_text(
                "You don't have any uncontested players available to release."
            )
            return ConversationHandler.END

        # Initialize selected players list
        ctx_manager.set_selected_release_player_ids(context, [], active_gully_id)

        # Now show the player selection interface
        return await show_player_release_selection(update, context)

    except Exception as e:
        logger.error(f"Error in release_players_command: {e}")
        logger.exception("Detailed error traceback:")
        await update.message.reply_text(
            "⚠️ Something went wrong while retrieving your players. Please try again later."
        )
        return ConversationHandler.END


async def show_player_release_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Show the player release selection interface with inline keyboard.
    """
    logger.info("Release: show_player_release_selection called")

    # Get active gully ID
    active_gully_id = ctx_manager.get_active_gully_id(context)
    logger.info(f"Active gully ID: {active_gully_id}")

    # Get participant ID
    participant_id = ctx_manager.get_participant_id(context, active_gully_id)
    logger.info(f"Current participant ID: {participant_id}")

    # Get uncontested players from context
    all_uncontested_players = ctx_manager.get_uncontested_players(
        context, active_gully_id
    )

    # Filter to only include players owned by this participant
    uncontested_players = []
    for player in all_uncontested_players:
        # Check if this player belongs to the current participant
        for participant in player.get("participants", []):
            if participant.get("participant_id") == participant_id:
                uncontested_players.append(player)
                break

    logger.info(
        f"Filtered {len(uncontested_players)} players owned by participant {participant_id} from {len(all_uncontested_players)} total uncontested players"
    )

    # Debug log
    for i, player in enumerate(uncontested_players[:3]):
        logger.info(f"Player {i+1}: {player}")

    if not uncontested_players:
        await update.message.reply_text(
            "You don't have any uncontested players available to release."
        )
        return ConversationHandler.END

    # Get selected player IDs
    selected_player_ids = ctx_manager.get_selected_release_player_ids(
        context, active_gully_id
    )

    # Create inline keyboard
    keyboard = []

    for player in uncontested_players:
        player_id = player.get("player_id", player.get("id"))
        player_name = player.get("player_name", player.get("name", "Unknown Player"))
        team = player.get("team", "Unknown Team")

        # Remove base_price from the button text
        is_selected = player_id in selected_player_ids
        status = "✅" if is_selected else ""

        # Updated button text without price
        button_text = f"🏏 {player_name} - {team} {status}"

        # Use the standardized callback format
        callback_data = create_release_callback("toggle", {"id": player_id})

        keyboard.append(
            [InlineKeyboardButton(button_text, callback_data=callback_data)]
        )

    # Add submit button with standardized callback format
    keyboard.append(
        [
            InlineKeyboardButton(
                "✅ Submit Releases", callback_data=create_release_callback("submit")
            )
        ]
    )

    # Add a "Keep All Players" button for users who don't want to release any
    keyboard.append(
        [
            InlineKeyboardButton(
                "🔒 Keep All Players", callback_data=create_release_callback("keep_all")
            )
        ]
    )

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Build message text
    message_text = (
        f"Select players you wish to release:\n\n"
        f"Currently selected: {len(selected_player_ids)} players\n\n"
        f"Tap a player to select/deselect, then tap '✅ Submit Releases' when done.\n"
        f"Or tap '🔒 Keep All Players' if you don't want to release any players."
    )

    if isinstance(update, Update) and update.callback_query:
        await update.callback_query.edit_message_text(
            text=message_text, reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(text=message_text, reply_markup=reply_markup)

    return SELECTING_PLAYERS_TO_RELEASE


async def handle_release_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> Optional[int]:
    """Handle callbacks specific to player release feature."""
    query = update.callback_query
    callback_data = parse_callback_data(query.data)

    # Only process callbacks for this module
    if not callback_data or callback_data["module"] != MODULE_ID:
        return None

    # Get active gully ID
    active_gully_id = ctx_manager.get_active_gully_id(context)

    # Check if release window is still open
    if not ctx_manager.is_release_window_open(context, active_gully_id):
        await query.answer("Release window has closed")
        await query.edit_message_text(
            "⚠️ The release window has closed. No further changes allowed."
        )
        return ConversationHandler.END

    # Handle the specific action
    action = callback_data["action"]
    data = callback_data.get("data", {})

    try:
        # Answer the callback query to stop the loading indicator
        await query.answer()

        # Handle toggle_release action
        if action == "toggle":
            player_id = data.get("id")
            if player_id is not None:
                logger.info(f"Toggling player with ID: {player_id}")

                # Get the active gully ID
                active_gully_id = ctx_manager.get_active_gully_id(context)
                logger.info(f"Active gully ID for toggle: {active_gully_id}")

                # Toggle player selection
                selected_player_ids = ctx_manager.get_selected_release_player_ids(
                    context, active_gully_id
                )

                if player_id in selected_player_ids:
                    selected_player_ids.remove(player_id)
                    logger.info(f"Removed player ID: {player_id}")
                else:
                    selected_player_ids.append(player_id)
                    logger.info(f"Added player ID: {player_id}")

                # Update context
                ctx_manager.set_selected_release_player_ids(
                    context, selected_player_ids, active_gully_id
                )
                logger.info(f"Updated selected players: {selected_player_ids}")

                # Show updated selection
                await show_player_release_selection(update, context)
                return SELECTING_PLAYERS_TO_RELEASE

        # Handle keep_all action (new)
        elif action == "keep_all":
            logger.info("Keep all players button pressed")
            # Clear any selections to ensure empty list
            ctx_manager.set_selected_release_player_ids(context, [], active_gully_id)
            # Process empty submission
            return await handle_release_submission(update, context, keep_all=True)

        # Handle submit_releases action
        elif action == "submit":
            logger.info("Submit releases button pressed")
            return await handle_release_submission(update, context)

        return SELECTING_PLAYERS_TO_RELEASE

    except Exception as e:
        logger.error(f"Error handling release callback: {e}")
        logger.exception("Detailed traceback:")
        return None


async def handle_release_submission(
    update: Update, context: ContextTypes.DEFAULT_TYPE, keep_all: bool = False
) -> int:
    """
    Handle the submission of player releases.

    Args:
        keep_all: Flag indicating user explicitly chose to keep all players
    """
    logger.info("Release: handle_release_submission called")

    # Get active gully ID
    active_gully_id = ctx_manager.get_active_gully_id(context)

    # Check if release window is still open
    if not ctx_manager.is_release_window_open(context, active_gully_id):
        await update.callback_query.answer("Release window has closed")
        await update.callback_query.edit_message_text(
            "⚠️ The release window has closed. No further releases allowed."
        )
        return ConversationHandler.END

    # Get selected player IDs from gully-specific context
    selected_player_ids = ctx_manager.get_selected_release_player_ids(
        context, active_gully_id
    )
    logger.info(f"Submitting releases with {len(selected_player_ids)} players")

    # Get participant ID for this specific gully
    participant_id = ctx_manager.get_participant_id(context, active_gully_id)

    if not participant_id:
        logger.error("Participant ID not found in context")
        await update.callback_query.edit_message_text(
            "⚠️ Participant ID not found. Please use /release_players to start over."
        )
        return ConversationHandler.END

    # Check if there are any players to release
    if not selected_player_ids:
        if keep_all:
            message = "You have chosen to keep all your uncontested players."
        else:
            message = "No players selected for release. Your squad remains unchanged."

        await update.callback_query.edit_message_text(message)

        # Mark as submitted in gully-specific context - USE EXISTING METHOD
        ctx_manager.set_release_submitted(context, True, active_gully_id)

        # Also store in a separate structure that tracks by participant_id
        if "participant_releases" not in context.bot_data:
            context.bot_data["participant_releases"] = {}
        if active_gully_id not in context.bot_data["participant_releases"]:
            context.bot_data["participant_releases"][active_gully_id] = set()
        # Add this participant to the set of participants who have submitted
        context.bot_data["participant_releases"][active_gully_id].add(participant_id)

        # Send empty list to API to update player statuses
        try:
            auction_client = await get_initialized_auction_client()
            result = await auction_client.release_players(participant_id, [])
            logger.info(f"Empty release result: {result}")

            # Send message to group chat about keeping all players
            if active_gully_id:
                # Get team name for this specific gully
                team_name = (
                    ctx_manager.get_team_name(context, active_gully_id)
                    or "Unknown Team"
                )

                # Get group chat ID from context or gully info
                client = await get_initialized_onboarding_client()
                gully = await client.get_gully(active_gully_id)

                if gully and gully.get("telegram_group_id"):
                    group_chat_id = gully.get("telegram_group_id")

                    # Build message for group
                    group_message = f"📌 {team_name} has decided to keep all their uncontested players."

                    try:
                        logger.info(f"Sending keep-all group message: {group_message}")
                        await context.bot.send_message(
                            chat_id=group_chat_id, text=group_message
                        )
                    except Exception as e:
                        logger.error(f"Failed to send group message: {e}")

        except Exception as e:
            logger.error(f"Error submitting empty release list: {e}")
            # We don't need to show an error to the user here

        return ConversationHandler.END

    # Get uncontested players and validate the selected players
    uncontested_players = ctx_manager.get_uncontested_players(context, active_gully_id)

    # Create a set of valid player IDs that the participant actually owns
    valid_player_ids = set()
    # Also map player IDs to their full data for display later
    player_data_map = {}

    for player in uncontested_players:
        player_id = player.get("player_id", player.get("id"))
        # Check if this player belongs to the current participant
        for participant in player.get("participants", []):
            if participant.get("participant_id") == participant_id:
                valid_player_ids.add(player_id)
                # Store player data for later use
                player_data_map[player_id] = player
                break

    # Filter selected_player_ids to only include valid ones
    valid_selected_ids = [pid for pid in selected_player_ids if pid in valid_player_ids]

    if len(valid_selected_ids) != len(selected_player_ids):
        invalid_count = len(selected_player_ids) - len(valid_selected_ids)
        logger.warning(
            f"Removed {invalid_count} invalid player IDs that don't belong to this participant"
        )

        # If no valid IDs remain, inform the user and exit
        if not valid_selected_ids:
            await update.callback_query.edit_message_text(
                "⚠️ None of the selected players belong to your team. Please try again."
            )
            return SELECTING_PLAYERS_TO_RELEASE

    # Submit releases with validated player IDs
    try:
        auction_client = await get_initialized_auction_client()
        result = await auction_client.release_players(
            participant_id, valid_selected_ids  # Use validated IDs here
        )

        logger.info(f"Release result: {result}")

        if not result:
            await update.callback_query.edit_message_text(
                "⚠️ Failed to release players. Please try again."
            )
            return SELECTING_PLAYERS_TO_RELEASE

        # Get released player details for confirmation message
        # First try from API response
        released_players = result.get("released_players", [])

        # If empty or incomplete, fetch from API or use cached data
        if not released_players or any(
            not p.get("player_name") for p in released_players
        ):
            logger.info(
                "Released players data is missing or incomplete, fetching details"
            )

            # Try to fetch player details from API for each released player ID
            try:
                # We'll fetch the details for all the players we've successfully released
                complete_released_players = []

                # First try to get full data from our cache
                for player_id in valid_selected_ids:
                    if player_id in player_data_map:
                        complete_released_players.append(player_data_map[player_id])
                        logger.info(f"Got player {player_id} details from cache")
                    else:
                        # If not in cache, we might need to fetch from API
                        # This would require an API endpoint that can get player by ID
                        try:
                            # Assuming there's an API method to get player by ID
                            # If not available, you'll need to modify the API client
                            player_detail = await auction_client.get_player(player_id)
                            if player_detail:
                                complete_released_players.append(player_detail)
                                logger.info(f"Got player {player_id} details from API")
                        except Exception as player_error:
                            logger.warning(
                                f"Failed to fetch player {player_id} details: {player_error}"
                            )

                # If we got complete data, use it
                if complete_released_players:
                    released_players = complete_released_players
            except Exception as fetch_error:
                logger.error(
                    f"Error fetching detailed player information: {fetch_error}"
                )
                # We'll fall back to whatever we have

        # Ensure we have proper player data
        if not released_players and valid_selected_ids:
            # Create simple player objects from the IDs if we couldn't get full details
            logger.warning("Creating simple player objects from IDs as fallback")
            released_players = [
                {
                    "player_id": pid,
                    "player_name": f"Player {pid}",
                    "team": "Unknown",
                }
                for pid in valid_selected_ids
            ]

        # Build confirmation message for the user
        message = "✅ Your selected players have been successfully released:\n\n"

        for player in released_players:
            player_name = player.get("player_name", "Unknown Player")
            team = player.get("team", "Unknown Team")
            message += f"🏏 {player_name} ({team})\n"

        # Send confirmation to user
        await update.callback_query.edit_message_text(message)

        # Mark as submitted in gully-specific context - USE EXISTING METHOD
        ctx_manager.set_release_submitted(context, True, active_gully_id)

        # Also store in a separate structure that tracks by participant_id
        if "participant_releases" not in context.bot_data:
            context.bot_data["participant_releases"] = {}
        if active_gully_id not in context.bot_data["participant_releases"]:
            context.bot_data["participant_releases"][active_gully_id] = set()
        # Add this participant to the set of participants who have submitted
        context.bot_data["participant_releases"][active_gully_id].add(participant_id)

        # Clear selected player IDs in gully-specific context
        ctx_manager.set_selected_release_player_ids(context, [], active_gully_id)

        # Announce in group chat
        if active_gully_id:
            # Get team name for this specific gully
            team_name = (
                ctx_manager.get_team_name(context, active_gully_id) or "Unknown Team"
            )

            # Get group chat ID from context or gully info
            client = await get_initialized_onboarding_client()
            gully = await client.get_gully(active_gully_id)

            if gully and gully.get("telegram_group_id"):
                group_chat_id = gully.get("telegram_group_id")

                # Build group message without base prices
                group_message = f"📌 {team_name} released players:\n"

                # Make sure we have players to display
                if released_players:
                    for player in released_players:
                        player_name = player.get("player_name", "Unknown Player")
                        team = player.get("team", "Unknown Team")

                        # Simplified message without prices
                        group_message += f"🏏 {player_name} ({team})\n"
                else:
                    # Include a message when no players were actually released
                    group_message += "No players were released."

                try:
                    logger.info(f"Sending group message: {group_message}")
                    await context.bot.send_message(
                        chat_id=group_chat_id, text=group_message
                    )
                except Exception as e:
                    logger.error(f"Failed to send group message: {e}")

        return ConversationHandler.END

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error releasing players: {e}")
        logger.exception("Detailed traceback:")

        # Provide a more specific error message based on the error
        if "not owned by participant" in error_msg:
            await update.callback_query.edit_message_text(
                "⚠️ Some of the selected players don't belong to your team. Please refresh the list with /release_players."
            )
        else:
            await update.callback_query.edit_message_text(
                "⚠️ An error occurred while releasing players. Please try again later."
            )
        return ConversationHandler.END


def standardize_player_data(player):
    """Standardize player data to ensure consistent format."""
    if not isinstance(player, dict):
        logger.error(f"Cannot standardize non-dict player: {player}")
        # Return a minimal valid player object
        return {
            "player_id": 0,
            "player_name": "Unknown Player",
            "team": "Unknown",
            "role": "Unknown",
            "base_price": 0,
            "participants": [],
        }

    return {
        "player_id": player.get("player_id", player.get("id")),
        "player_name": player.get("player_name", player.get("name", "Unknown")),
        "team": player.get("team", "Unknown"),
        "role": player.get("role", "Unknown"),
        "base_price": player.get("base_price", 0),
        "participants": player.get("participants", []),
    }


async def close_release_window(
    context: ContextTypes.DEFAULT_TYPE, gully_id: int, chat_id: int
) -> None:
    """
    Close the release window after the specified time.
    """
    logger.info(f"Auction: Scheduling release window closure for gully {gully_id}")

    # Wait for the release window duration
    await asyncio.sleep(RELEASE_WINDOW_MINUTES * 60)

    # Check if the release window is still open for this specific gully
    if ctx_manager.is_release_window_open(context, gully_id):
        logger.info(f"Auction: Closing release window for gully {gully_id}")

        # Mark release window as closed for this gully
        ctx_manager.set_release_window_state(context, gully_id, False)

        # Send message to the group
        await context.bot.send_message(
            chat_id=chat_id,
            text="🔒 Release window closed. No further releases allowed.",
        )

        # Process participants who didn't submit any releases
        await process_remaining_participants(context, gully_id)

        await context.bot.send_message(
            chat_id=chat_id,
            text="🚀 Auction Queue finalized. The auction will now begin with available players in the queue.",
        )


async def notify_participants_about_release(
    context: ContextTypes.DEFAULT_TYPE, gully_id: int
) -> None:
    """
    Notify all participants privately about the release window.
    Improved error handling for Telegram API errors.
    """
    logger.info(
        f"Release: Notifying participants about release window for gully {gully_id}"
    )

    try:
        # Get all participants for this gully
        client = await get_initialized_onboarding_client()

        # Log the exact endpoint we're using
        logger.info(f"Fetching participants for gully {gully_id}")

        # Get participants with better error handling
        try:
            participants = await client.get_participants(gully_id)
            logger.info(f"Received participants data: {participants}")

            # Ensure participants is a list
            if not isinstance(participants, list):
                logger.error(f"Invalid participant data format: {type(participants)}")
                participants = []

        except Exception as e:
            logger.error(f"Error getting participants: {e}")
            participants = []

        logger.info(f"Processing {len(participants)} participants")

        for participant in participants:
            # Extract participant data
            user_id = participant.get("user_id")
            participant_id = participant.get("id")
            team_name = participant.get("team_name", "Your team")

            if user_id:
                try:
                    # Send private message to each participant
                    message = (
                        f"⏰ Release Window ({RELEASE_WINDOW_MINUTES} mins)\n\n"
                        f"Select any players you wish to release from your uncontested list for {team_name}. "
                        f"Once submitted, released players cannot be reclaimed.\n\n"
                        f"Use /release_players to select players to release."
                    )

                    # Store participant info in gully-specific context for this user
                    ctx_manager.set_active_gully_id(context, gully_id)
                    ctx_manager.set_participant_id(context, participant_id, gully_id)
                    ctx_manager.set_team_name(context, team_name, gully_id)

                    await context.bot.send_message(chat_id=user_id, text=message)
                    logger.info(
                        f"Sent notification to user {user_id} for team {team_name}"
                    )
                except Exception as e:
                    # More specific error handling for Telegram errors
                    if "Chat not found" in str(e):
                        logger.warning(
                            f"User {user_id} has not started a conversation with the bot. Cannot send message."
                        )
                    else:
                        logger.error(f"Failed to notify participant {user_id}: {e}")

    except Exception as e:
        logger.error(f"Error notifying participants: {e}")
        logger.exception("Detailed traceback:")


async def process_remaining_participants(
    context: ContextTypes.DEFAULT_TYPE, gully_id: int
) -> None:
    """
    Process remaining participants who haven't submitted any releases.
    This ensures their player statuses are updated to OWNED.
    Called automatically when the release window closes.
    """
    logger.info(f"Processing remaining participants for gully {gully_id}")

    try:
        # Get all participants for this gully
        client = await get_initialized_onboarding_client()
        participants = await client.get_participants(gully_id)

        if not participants:
            logger.warning(f"No participants found for gully {gully_id}")
            return

        # Get auction client for making release API calls
        auction_client = await get_initialized_auction_client()

        # Get the set of participants who have already submitted
        submitted_participants = context.bot_data.get("participant_releases", {}).get(
            gully_id, set()
        )
        logger.info(
            f"Found {len(submitted_participants)} participants who already submitted releases"
        )

        # Get group chat ID for announcements
        group_chat_id = None
        try:
            gully = await client.get_gully(gully_id)
            if gully and gully.get("telegram_group_id"):
                group_chat_id = gully.get("telegram_group_id")
        except Exception as e:
            logger.error(f"Failed to get group chat ID: {e}")

        # Process each participant who hasn't submitted
        processed_count = 0
        error_count = 0

        for participant in participants:
            participant_id = participant.get("id")
            team_name = participant.get("team_name", "Unknown Team")

            # Skip participants who have already submitted
            if participant_id in submitted_participants or not participant_id:
                continue

            logger.info(
                f"Auto-keeping all players for {team_name} (participant {participant_id})"
            )

            # Add a small delay between API calls to avoid overwhelming the server
            if processed_count > 0:
                await asyncio.sleep(0.5)  # 500ms delay between participants

            # --- USING THE SAME FLOW AS "KEEP ALL PLAYERS" BUTTON ---
            try:
                # 1. Call API with empty list (keep all players)
                result = await auction_client.release_players(participant_id, [])
                logger.info(
                    f"Auto-keep all success for {team_name} (participant {participant_id}): {result}"
                )
                processed_count += 1

                # 2. Mark as processed in our tracking structure
                if "participant_releases" not in context.bot_data:
                    context.bot_data["participant_releases"] = {}
                if gully_id not in context.bot_data["participant_releases"]:
                    context.bot_data["participant_releases"][gully_id] = set()
                context.bot_data["participant_releases"][gully_id].add(participant_id)

                # 3. Send message to group chat (just like in the keep_all flow)
                if group_chat_id:
                    group_message = f"📌 {team_name} has automatically kept all their uncontested players."
                    try:
                        await context.bot.send_message(
                            chat_id=group_chat_id, text=group_message
                        )
                        logger.info(f"Sent auto-keep message for {team_name} to group")
                    except Exception as msg_error:
                        logger.error(f"Failed to send group message: {msg_error}")

            except Exception as e:
                error_count += 1
                logger.error(
                    f"Failed to auto-keep players for {team_name} (participant {participant_id}): {e}"
                )
                # We'll continue to the next participant rather than stopping

        logger.info(
            f"Auto-keep process complete. Processed: {processed_count}, Errors: {error_count}"
        )

    except Exception as e:
        logger.error(f"Error processing remaining participants: {e}")
        logger.exception("Detailed traceback:")


def get_handlers():
    """Get all handlers for player release features."""
    logger.info("Registering player release handlers")

    # Create a dedicated release callback handler with a clear pattern
    release_callback_handler = CallbackQueryHandler(
        handle_release_callback, pattern=create_callback_pattern(MODULE_ID)
    )

    # Create conversation handler for the release process
    release_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("release_players", release_players_command)],
        states={SELECTING_PLAYERS_TO_RELEASE: [release_callback_handler]},
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
        name="player_release_conv",
        persistent=False,
    )

    return [
        release_conv_handler,
        # Add standalone callback handler to catch callbacks outside of conversation
        release_callback_handler,
    ]
