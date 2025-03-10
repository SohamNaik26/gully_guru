"""
Admin feature module for GullyGuru bot.
Handles admin panel and member management.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Replace bot services with direct API client import
from src.api.api_client_instance import api_client

# Configure logging
logger = logging.getLogger(__name__)


async def admin_panel_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle the /admin command.
    Shows admin options for gully management.
    Only works in personal chats.
    """
    user = update.effective_user
    chat = update.effective_chat

    # Only allow in private chats
    if chat.type != "private":
        return

    # Get user from database
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

    # Get all gullies where user participates
    participations = await api_client.get_user_gully_participations(db_user["id"])

    # Filter to only include gullies where user is admin
    admin_participations = [p for p in participations if p.get("role") == "admin"]

    if not admin_participations:
        await update.message.reply_text("You are not an admin in any gully.")
        return

    # Show list of gullies where user is admin
    keyboard = []
    for participation in admin_participations:
        gully_id = participation.get("gully_id")
        gully_name = participation.get("gully_name", f"Gully {gully_id}")
        keyboard.append(
            [
                InlineKeyboardButton(
                    f"🏏 {gully_name}", callback_data=f"admin_select_gully_{gully_id}"
                )
            ]
        )

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🛠️ *Admin* 🛠️\n\n" "Select a gully to manage:",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def prompt_members_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle the /prompt_members command.
    Sends a reminder to all members who haven't created a team yet.
    """
    # This command is now only accessible through the admin panel
    # Keep the implementation for backward compatibility
    await update.message.reply_text(
        "Please use the /admin_panel command to access this functionality."
    )


async def handle_admin_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle callbacks for admin panel."""
    query = update.callback_query
    await query.answer()  # Answer the callback query to stop the loading animation

    user = update.effective_user
    data = query.data

    # Ensure user exists in database
    db_user = await api_client.users.get_user(user.id)
    if not db_user:
        await query.edit_message_text(
            "❌ Sorry, there was an error with your account. Please try again later."
        )
        return

    # Handle gully selection from private chat
    if data.startswith("admin_select_gully_"):
        gully_id = int(data.replace("admin_select_gully_", ""))

        # Get the gully
        gully = await api_client.gullies.get_gully(gully_id)
        if not gully:
            await query.edit_message_text("❌ Sorry, this gully no longer exists.")
            return

        # Check if user is admin
        participation = await api_client.get_user_gully_participation(
            user_id=db_user["id"], gully_id=gully_id
        )

        is_admin = participation and participation.get("role") == "admin"

        if not is_admin:
            await query.edit_message_text(
                "You don't have admin privileges for this gully."
            )
            return

        # Show admin panel for selected gully
        keyboard = [
            [
                InlineKeyboardButton(
                    "Prompt Members", callback_data=f"admin_prompt_members_{gully_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "Manage Auction", callback_data=f"admin_manage_auction_{gully_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "Back to Gully List", callback_data="admin_back_to_gullies"
                )
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"🛠️ *Admin Panel for {gully['name']}* 🛠️\n\n"
            "Select an option to manage your gully:",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )
        return

    # Handle back to gully list
    if data == "admin_back_to_gullies":
        # Get all gullies where user participates
        participations = await api_client.get_user_gully_participations(db_user["id"])

        # Filter to only include gullies where user is admin
        admin_participations = [p for p in participations if p.get("role") == "admin"]

        if not admin_participations:
            await query.edit_message_text("You are not an admin in any gully.")
            return

        # Show list of gullies where user is admin
        keyboard = []
        for participation in admin_participations:
            gully_id = participation.get("gully_id")
            gully_name = participation.get("gully_name", f"Gully {gully_id}")
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"🏏 {gully_name}",
                        callback_data=f"admin_select_gully_{gully_id}",
                    )
                ]
            )

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "🛠️ *Admin Panel* 🛠️\n\n" "Select a gully to manage:",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )
        return

    # Extract gully_id from callback data if present
    gully_id = None
    if "_" in data and data.split("_")[-1].isdigit():
        parts = data.split("_")
        gully_id = int(parts[-1])
        # Remove gully_id from data to simplify further processing
        data = "_".join(parts[:-1])

    if gully_id is None:
        await query.edit_message_text(
            "❌ Error: Could not determine which gully to manage."
        )
        return

    # Get the gully
    gully = await api_client.gullies.get_gully(gully_id)
    if not gully:
        await query.edit_message_text("This gully no longer exists.")
        return

    # Check if user is admin
    participation = await api_client.get_user_gully_participation(
        user_id=db_user["id"], gully_id=gully_id
    )

    is_admin = participation and participation.get("role") == "admin"

    if not is_admin:
        await query.edit_message_text("You don't have admin privileges for this gully.")
        return

    # Handle different callback actions
    if data == "admin_prompt_members":
        # Ask for confirmation before sending prompts
        keyboard = [
            [
                InlineKeyboardButton(
                    "Yes, send reminders",
                    callback_data=f"admin_send_prompts_{gully_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    "Back to Admin Panel", callback_data=f"admin_back_{gully_id}"
                )
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"🔔 *Prompt Members in {gully['name']}* 🔔\n\n"
            "This will send a reminder to all members who haven't created their teams yet.\n\n"
            "Do you want to continue?",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )

    elif data == "admin_send_prompts":
        # Get members without teams
        members = await api_client.gullies.get_members_without_teams(gully_id)

        if not members:
            # Back button
            keyboard = [
                [
                    InlineKeyboardButton(
                        "Back to Admin Panel", callback_data=f"admin_back_{gully_id}"
                    )
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                "All members in this gully have created their teams already.",
                reply_markup=reply_markup,
            )
            return

        # Send reminder message
        message = (
            f"🔔 *Reminder from {gully['name']} Admin* 🔔\n\n"
            "You haven't created your team yet. Please use /submit_squad to create your team "
            "before the auction starts.\n\n"
        )

        # Send message to each member
        success_count = 0
        for member in members:
            try:
                telegram_id = member.get("telegram_id")
                if telegram_id:
                    await context.bot.send_message(
                        chat_id=telegram_id, text=message, parse_mode="Markdown"
                    )
                    success_count += 1
            except Exception as e:
                logger.error(
                    f"Failed to send reminder to user {member.get('id')}: {str(e)}"
                )

        # Back button
        keyboard = [
            [
                InlineKeyboardButton(
                    "Back to Admin Panel", callback_data=f"admin_back_{gully_id}"
                )
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"Reminder sent to {success_count} out of {len(members)} members without teams.",
            reply_markup=reply_markup,
        )

    elif data == "admin_manage_auction":
        # Show auction management options
        keyboard = [
            [
                InlineKeyboardButton(
                    "Start Auction", callback_data=f"start_auction_{gully_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "Back to Admin Panel", callback_data=f"admin_back_{gully_id}"
                )
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "🏏 *Auction Management* 🏏\n\n" "Select an option to manage the auction:",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )

    elif data == "admin_back":
        # Return to main admin panel for the selected gully
        keyboard = [
            [
                InlineKeyboardButton(
                    "Prompt Members", callback_data=f"admin_prompt_members_{gully_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "Manage Auction", callback_data=f"admin_manage_auction_{gully_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "Back to Gully List", callback_data="admin_back_to_gullies"
                )
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"🛠️ *Admin Panel for {gully['name']}* 🛠️\n\n"
            "Select an option to manage your gully:",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )
