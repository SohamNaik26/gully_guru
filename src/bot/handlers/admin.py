from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging

from src.api.api_client_instance import api_client
from src.bot.services import user_service, gully_service, admin_service

# Configure logging
logger = logging.getLogger(__name__)


# Admin panel command
async def admin_panel_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle the /admin_panel command to access admin functionality."""
    user = update.effective_user

    # Check if this is a private chat
    if update.effective_chat.type != "private":
        await update.message.reply_text(
            "Admin commands are only available in private chat. Please message me directly."
        )
        return

    # Get user from database
    db_user = await api_client.users.get_user(user.id)
    if not db_user:
        await update.message.reply_text(
            "You need to register first. Use /join_gully to register."
        )
        return

    # Get all gullies the user is part of
    gullies = await gully_service.get_user_gully_participations(db_user["id"])
    if not gullies:
        await update.message.reply_text(
            "You are not a member of any gullies yet. Use /join_gully to join a gully."
        )
        return

    # Filter to only show gullies where the user is an admin
    admin_gullies = []
    for gully in gullies:
        # Check if user is admin in this gully using AdminService
        is_admin = await admin_service.check_admin_status(
            user.id, gully.get("gully_id")
        )
        if is_admin:
            admin_gullies.append(gully)

    if not admin_gullies:
        await update.message.reply_text(
            "You are not an admin in any gullies. Only gully admins can access the admin panel."
        )
        return

    # Create keyboard with admin gullies
    keyboard = []
    for gully in admin_gullies:
        gully_name = gully.get("gully", {}).get("name", "Unknown Gully")
        gully_id = gully.get("gully_id")
        keyboard.append(
            [
                InlineKeyboardButton(
                    f"🏏 {gully_name}", callback_data=f"admin_select_gully_{gully_id}"
                )
            ]
        )

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to the Admin Panel! Please select a gully to manage:",
        reply_markup=reply_markup,
    )


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

    # Check if a gully already exists for this group using GullyService
    existing_gully = await gully_service.get_gully_by_group(chat.id)
    if existing_gully:
        await update.message.reply_text(
            f"A gully already exists for this group: {existing_gully.get('name')}"
        )
        return

    # Get or create the user using UserService
    db_user = await api_client.users.get_user(user.id)
    if not db_user:
        db_user = await user_service.ensure_user_exists(user)
        if not db_user:
            await update.message.reply_text(
                "❌ Sorry, there was an error with your account. Please try again later."
            )
            return

    # Create a default gully name based on the group name
    default_name = chat.title or f"Gully {chat.id}"

    try:
        # Create the gully using GullyService
        new_gully = await gully_service.create_gully(
            name=default_name, telegram_group_id=chat.id, creator_telegram_id=user.id
        )

        if new_gully:
            await update.message.reply_text(
                f"✅ Successfully created gully '{default_name}' and assigned you as admin!"
            )
        else:
            await update.message.reply_text(
                "❌ Failed to create the gully. Please try again later."
            )

    except Exception as e:
        logger.error(f"Error creating gully: {str(e)}")
        await update.message.reply_text(
            "❌ An error occurred while creating the gully. Please try again later."
        )


async def add_member_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle the /add_member command.
    This command allows admins to add a user to the current gully.

    Usage: /add_member <user_id>
    """
    user = update.effective_user
    chat = update.effective_chat

    # Check if this is a group chat
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text(
            "This command can only be used in a group chat."
        )
        return

    # Check if the user provided a user ID
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text(
            "Please provide a valid user ID. Usage: `/add_member <user_id>`",
            parse_mode="Markdown",
        )
        return

    target_user_id = int(context.args[0])

    # Get the current gully using the GullyService
    gully = await gully_service.get_gully_by_group(chat.id)
    if not gully:
        await update.message.reply_text(
            "This group is not registered as a gully yet. Use /join_gully to create one."
        )
        return

    # Get the current user using the UserService
    db_user = await api_client.users.get_user(user.id)
    if not db_user:
        # Create the user if they don't exist
        db_user = await user_service.ensure_user_exists(user)
        if not db_user:
            await update.message.reply_text(
                "❌ Sorry, there was an error with your account. Please try again later."
            )
            return

    # Check admin status using the AdminService
    is_admin = await admin_service.check_admin_status(db_user["id"], gully["id"])
    if not is_admin:
        # Check if user is a Telegram admin
        chat_member = await context.bot.get_chat_member(chat.id, user.id)
        is_telegram_admin = chat_member.status in ["creator", "administrator"]

        if is_telegram_admin:
            # Telegram admin but not gully admin - let's fix that using AdminService
            result = await admin_service.assign_admin_role(db_user["id"], gully["id"])
            if result.get("success", False):
                await update.message.reply_text(
                    "✅ You've been assigned as a gully admin because you're a Telegram admin."
                )
            else:
                await update.message.reply_text(
                    f"❌ Only gully admins can add members. Error: {result.get('error', 'Unknown error')}"
                )
                return
        else:
            await update.message.reply_text("❌ Only gully admins can add members.")
            return

    # Get the target user using the UserService
    target_user = None
    # First try as database ID
    if str(target_user_id).isdigit():
        target_user = await api_client.users.get_user_by_id(target_user_id)

    # If not found, try as Telegram ID
    if not target_user:
        target_user = await api_client.users.get_user(target_user_id)

    if not target_user:
        await update.message.reply_text(
            f"❌ User with ID {target_user_id} not found. Make sure they have interacted with the bot at least once."
        )
        return

    # Add the user to the gully using GullyService
    try:
        new_participant = await gully_service.add_user_to_gully(
            user_id=target_user["id"], gully_id=gully["id"], role="member"
        )

        if new_participant:
            user_name = target_user.get(
                "full_name", target_user.get("username", "Unknown")
            )
            await update.message.reply_text(
                f"✅ Successfully added {user_name} to the gully!"
            )
        else:
            await update.message.reply_text(
                "❌ Failed to add the user to the gully. Please try again later."
            )
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error adding user to gully: {error_msg}")

        if "403" in error_msg:
            await update.message.reply_text(
                "❌ Permission denied. You may not have the required permissions to add users."
            )
        else:
            await update.message.reply_text(
                "❌ An error occurred while adding the user. Please try again later."
            )


async def manage_admins_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle the /manage_admins command.
    This command allows admins to view and manage other admins in the gully.
    """
    user = update.effective_user
    chat = update.effective_chat

    # Check if this is a group chat
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text(
            "This command can only be used in a group chat."
        )
        return

    # Get the current gully using the GullyService
    gully = await gully_service.get_gully_by_group(chat.id)
    if not gully:
        await update.message.reply_text(
            "This group is not registered as a gully yet. Use /join_gully to create one."
        )
        return

    # Get the current user using the UserService
    db_user = await api_client.users.get_user(user.id)
    if not db_user:
        db_user = await user_service.ensure_user_exists(user)
        if not db_user:
            await update.message.reply_text(
                "❌ Sorry, there was an error with your account. Please try again later."
            )
            return

    # Check admin status using the AdminService
    is_admin = await admin_service.check_admin_status(db_user["id"], gully["id"])
    if not is_admin:
        await update.message.reply_text("❌ Only gully admins can manage admins.")
        return

    # Get all admins for this gully
    admins = await admin_service.get_gully_admins(gully["id"])

    if not admins:
        await update.message.reply_text("No admins found for this gully.")
        return

    # Format the admin list
    admin_list = "Current Admins:\n\n"
    for admin in admins:
        admin_list += f"• {admin.get('full_name', admin.get('username', 'Unknown'))} - {admin.get('role', 'admin')}\n"

    # Create keyboard for admin management
    keyboard = [
        [InlineKeyboardButton("Add Admin", callback_data=f"admin_add_{gully['id']}")],
        [
            InlineKeyboardButton(
                "Remove Admin", callback_data=f"admin_remove_{gully['id']}"
            )
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"{admin_list}\n\nSelect an action to manage admins:",
        reply_markup=reply_markup,
    )
