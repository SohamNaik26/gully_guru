from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.bot.api_client_instance import api_client
from src.bot.utils import get_active_gully_id


# Admin panel command
async def admin_panel_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle the /admin_panel command to access auction-related admin functionality."""
    user = update.effective_user

    # Check if this is a private chat
    if update.effective_chat.type != "private":
        await update.message.reply_text(
            "Admin commands are only available in private chat. Please message me directly."
        )
        return

    # Get user from database
    db_user = await api_client.get_user(user.id)
    if not db_user:
        await update.message.reply_text(
            "You need to register first. Use /start to register."
        )
        return

    # Check if user is an admin anywhere
    is_admin = await api_client.is_admin_anywhere(user.id)
    if not is_admin:
        await update.message.reply_text(
            "You don't have admin permissions in any gully. "
            "You need to be an admin in at least one gully to access admin functionality."
        )
        return

    # Get active gully
    active_gully_id = await get_active_gully_id(user.id, context)
    if not active_gully_id:
        # Show list of gullies where user is admin
        gullies = await api_client.get_user_games(user.id)
        admin_gullies = []

        for gully in gullies:
            # Check if user is admin in this gully
            is_admin_in_gully = await check_admin_status(user.id, gully.get("id"))
            if is_admin_in_gully:
                admin_gullies.append(gully)

        if not admin_gullies:
            await update.message.reply_text(
                "You don't have admin permissions in any gully. "
                "You need to be an admin in at least one gully to access admin functionality."
            )
            return

        # Create keyboard with admin gullies
        keyboard = []
        for gully in admin_gullies:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        gully.get("name"),
                        callback_data=f"admin_select_gully_{gully.get('id')}",
                    )
                ]
            )

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Please select a gully to manage:", reply_markup=reply_markup
        )
        return

    # Check if user is admin in active gully
    is_admin_in_gully = await check_admin_status(user.id, active_gully_id)
    if not is_admin_in_gully:
        await update.message.reply_text(
            "You don't have admin permissions in the active gully. "
            "Please select a different gully where you have admin permissions."
        )
        return

    # Get gully details
    gully = await api_client.get_gully(active_gully_id)
    if not gully:
        await update.message.reply_text(
            "Failed to get gully details. Please try again later."
        )
        return

    # Create admin panel keyboard
    keyboard = [
        [
            InlineKeyboardButton(
                "Start Round 0", callback_data=f"admin_start_round_0_{active_gully_id}"
            ),
            InlineKeyboardButton(
                "End Round 0", callback_data=f"admin_end_round_0_{active_gully_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                "Start Round 1", callback_data=f"admin_start_round_1_{active_gully_id}"
            ),
            InlineKeyboardButton(
                "End Round 1", callback_data=f"admin_end_round_1_{active_gully_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                "Next Player", callback_data=f"admin_next_player_{active_gully_id}"
            ),
            InlineKeyboardButton(
                "End Auction", callback_data=f"admin_end_auction_{active_gully_id}"
            ),
        ],
        [
            InlineKeyboardButton("Switch Gully", callback_data="admin_switch_gully"),
            InlineKeyboardButton("Back to Main", callback_data="admin_back_to_main"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"Admin Panel for {gully.get('name')}\n\n"
        f"Status: {gully.get('status')}\n"
        f"Members: {gully.get('member_count', 0)}\n\n"
        f"Select an action:",
        reply_markup=reply_markup,
    )


async def check_admin_status(user_id: int, gully_id: int) -> bool:
    """Check if a user is an admin in a specific gully."""
    try:
        return await api_client.is_admin_in_gully(user_id, gully_id)
    except Exception:
        return False


async def create_gully_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle the /create_gully command.
    This command allows admins to create a new gully and link it to the current group.
    """
    user = update.effective_user
    chat = update.effective_chat

    # Check if this is a group chat
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text(
            "This command can only be used in group chats. Please add me to a group first."
        )
        return

    # Check if user is an admin in the group
    chat_member = await context.bot.get_chat_member(chat.id, user.id)
    if chat_member.status not in ["creator", "administrator"]:
        await update.message.reply_text("Only group administrators can create gullies.")
        return

    # Check if the group is already linked to a gully
    existing_gully = await api_client.get_gully_by_chat_id(chat.id)
    if existing_gully:
        await update.message.reply_text(
            f"This group is already linked to the gully '{existing_gully.get('name')}'. "
            f"You cannot create another gully for this group."
        )
        return

    # Start the gully creation process
    await update.message.reply_text(
        "Let's create a new gully! Please provide a name for your gully:"
    )

    # Store the chat ID in user data for the conversation handler
    context.user_data["creating_gully_for_chat"] = chat.id

    # Note: The actual conversation handler for gully creation would be defined elsewhere
    # and would handle the rest of the flow
