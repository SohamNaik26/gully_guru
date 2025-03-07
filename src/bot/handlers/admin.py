from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from typing import Dict, Any, List, Optional

from src.bot.client import api_client
from src.bot.utils import format_message, get_active_gully_id


# Admin panel command
async def admin_panel_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle the /admin_panel command to access admin functionality."""
    user = update.effective_user

    # Get user from database
    db_user = await api_client.get_user(user.id)
    if not db_user:
        await update.message.reply_text(
            "You need to register first. Use /start to register."
        )
        return

    # Get active gully
    active_gully_id = await get_active_gully_id(user.id, context)
    if not active_gully_id:
        await update.message.reply_text(
            "You need to have an active gully to use the admin panel. "
            "Use /my_gullies to view and select a gully."
        )
        return

    # Check if user is an admin in this gully
    is_admin = await check_admin_status(user.id, active_gully_id)
    if not is_admin:
        await update.message.reply_text(
            "You don't have admin permissions in this gully."
        )
        return

    # Create admin panel keyboard
    keyboard = [
        [
            InlineKeyboardButton(
                "User Management", callback_data=f"admin_users_{active_gully_id}"
            ),
            InlineKeyboardButton(
                "Team Management", callback_data=f"admin_teams_{active_gully_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                "Auction Management", callback_data=f"admin_auction_{active_gully_id}"
            ),
            InlineKeyboardButton(
                "Match Management", callback_data=f"admin_matches_{active_gully_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                "Gully Settings", callback_data=f"admin_settings_{active_gully_id}"
            ),
            InlineKeyboardButton(
                "Admin Roles", callback_data=f"admin_roles_{active_gully_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                "Generate Invite Link", callback_data=f"admin_invite_{active_gully_id}"
            )
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Get gully info
    gully = await api_client.get_gully(active_gully_id)

    message = (
        f"🛠️ *Admin Panel - {gully.get('name')}* 🛠️\n\n"
        f"Welcome to the admin panel for this gully. "
        f"Select an option below to manage your gully:\n\n"
        f"• User Management: Add/remove users, assign roles\n"
        f"• Team Management: Manage teams and players\n"
        f"• Auction Management: Configure auction settings\n"
        f"• Match Management: Set up matches and tournaments\n"
        f"• Gully Settings: Configure gully settings\n"
        f"• Admin Roles: Manage admin permissions\n"
        f"• Generate Invite Link: Create invite links for new users"
    )

    await update.message.reply_text(
        message, reply_markup=reply_markup, parse_mode="Markdown"
    )


# Add admin command
async def add_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /add_admin command to assign admin role to a user."""
    user = update.effective_user

    # Check if command has username parameter
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "Please provide a username. Usage: /add_admin @username"
        )
        return

    # Get target username
    target_username = context.args[0].replace("@", "")

    # Get user from database
    db_user = await api_client.get_user(user.id)
    if not db_user:
        await update.message.reply_text(
            "You need to register first. Use /start to register."
        )
        return

    # Get active gully or group gully
    gully_id = None
    if update.effective_chat.type == "private":
        gully_id = await get_active_gully_id(user.id, context)
    else:
        # In group chat, get the gully linked to this group
        gully = await api_client.get_gully_by_telegram_group(update.effective_chat.id)
        if gully:
            gully_id = gully.get("id")

    if not gully_id:
        await update.message.reply_text(
            "No active gully found. Please select a gully first or use this command in a gully group."
        )
        return

    # Check if user is an admin in this gully
    is_admin = await check_admin_status(user.id, gully_id)
    if not is_admin:
        await update.message.reply_text(
            "You don't have admin permissions in this gully."
        )
        return

    # Find target user by username
    target_user = await api_client.get_user_by_username(target_username)
    if not target_user:
        await update.message.reply_text(
            f"User @{target_username} not found. Make sure they have registered with the bot."
        )
        return

    # Assign admin role
    try:
        result = await api_client.assign_admin_role(
            user_id=target_user.get("id"), gully_id=gully_id
        )

        if result.get("success"):
            await update.message.reply_text(
                f"✅ @{target_username} has been assigned admin role in this gully."
            )
        else:
            await update.message.reply_text(
                f"Failed to assign admin role: {result.get('detail', 'Unknown error')}"
            )
    except Exception as e:
        await update.message.reply_text(f"Error assigning admin role: {str(e)}")


# Remove admin command
async def remove_admin_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle the /remove_admin command to remove admin role from a user."""
    user = update.effective_user

    # Check if command has username parameter
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "Please provide a username. Usage: /remove_admin @username"
        )
        return

    # Get target username
    target_username = context.args[0].replace("@", "")

    # Get user from database
    db_user = await api_client.get_user(user.id)
    if not db_user:
        await update.message.reply_text(
            "You need to register first. Use /start to register."
        )
        return

    # Get active gully or group gully
    gully_id = None
    if update.effective_chat.type == "private":
        gully_id = await get_active_gully_id(user.id, context)
    else:
        # In group chat, get the gully linked to this group
        gully = await api_client.get_gully_by_telegram_group(update.effective_chat.id)
        if gully:
            gully_id = gully.get("id")

    if not gully_id:
        await update.message.reply_text(
            "No active gully found. Please select a gully first or use this command in a gully group."
        )
        return

    # Check if user is an admin in this gully
    is_admin = await check_admin_status(user.id, gully_id)
    if not is_admin:
        await update.message.reply_text(
            "You don't have admin permissions in this gully."
        )
        return

    # Find target user by username
    target_user = await api_client.get_user_by_username(target_username)
    if not target_user:
        await update.message.reply_text(
            f"User @{target_username} not found. Make sure they have registered with the bot."
        )
        return

    # Remove admin role
    try:
        result = await api_client.remove_admin_role(
            user_id=target_user.get("id"), gully_id=gully_id
        )

        if result.get("success"):
            await update.message.reply_text(
                f"✅ Admin role has been removed from @{target_username}."
            )
        else:
            await update.message.reply_text(
                f"Failed to remove admin role: {result.get('detail', 'Unknown error')}"
            )
    except Exception as e:
        await update.message.reply_text(f"Error removing admin role: {str(e)}")


# Nominate admin command
async def nominate_admin_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle the /nominate_admin command to nominate a new admin."""
    user = update.effective_user

    # Check if command has username parameter
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "Please provide a username. Usage: /nominate_admin @username"
        )
        return

    # Get target username
    target_username = context.args[0].replace("@", "")

    # Get user from database
    db_user = await api_client.get_user(user.id)
    if not db_user:
        await update.message.reply_text(
            "You need to register first. Use /start to register."
        )
        return

    # Get active gully or group gully
    gully_id = None
    if update.effective_chat.type == "private":
        gully_id = await get_active_gully_id(user.id, context)
    else:
        # In group chat, get the gully linked to this group
        gully = await api_client.get_gully_by_telegram_group(update.effective_chat.id)
        if gully:
            gully_id = gully.get("id")

    if not gully_id:
        await update.message.reply_text(
            "No active gully found. Please select a gully first or use this command in a gully group."
        )
        return

    # Check if user is an admin in this gully
    is_admin = await check_admin_status(user.id, gully_id)
    if not is_admin:
        await update.message.reply_text(
            "You don't have admin permissions in this gully."
        )
        return

    # Find target user by username
    target_user = await api_client.get_user_by_username(target_username)
    if not target_user:
        await update.message.reply_text(
            f"User @{target_username} not found. Make sure they have registered with the bot."
        )
        return

    # Nominate admin
    try:
        result = await api_client.nominate_admin(
            nominee_id=target_user.get("id"), gully_id=gully_id
        )

        if result.get("success"):
            # Send message to group chat
            await update.message.reply_text(
                f"✅ @{target_username} has been nominated as an admin for this gully."
            )

            # Send private message to nominee
            if update.effective_chat.type != "private":
                try:
                    await context.bot.send_message(
                        chat_id=target_user.get("telegram_id"),
                        text=(
                            f"🎉 *Congratulations!* 🎉\n\n"
                            f"You have been nominated as an admin for the gully "
                            f"*{result.get('gully_name', 'Unknown')}*.\n\n"
                            f"You now have additional permissions to manage users, teams, and settings."
                        ),
                        parse_mode="Markdown",
                    )
                except Exception:
                    # Failed to send private message, just continue
                    pass
        else:
            await update.message.reply_text(
                f"Failed to nominate admin: {result.get('detail', 'Unknown error')}"
            )
    except Exception as e:
        await update.message.reply_text(f"Error nominating admin: {str(e)}")


# Gully settings command
async def gully_settings_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle the /gully_settings command to configure gully settings."""
    user = update.effective_user

    # Get user from database
    db_user = await api_client.get_user(user.id)
    if not db_user:
        await update.message.reply_text(
            "You need to register first. Use /start to register."
        )
        return

    # Get active gully or group gully
    gully_id = None
    if update.effective_chat.type == "private":
        gully_id = await get_active_gully_id(user.id, context)
    else:
        # In group chat, get the gully linked to this group
        gully = await api_client.get_gully_by_telegram_group(update.effective_chat.id)
        if gully:
            gully_id = gully.get("id")

    if not gully_id:
        await update.message.reply_text(
            "No active gully found. Please select a gully first or use this command in a gully group."
        )
        return

    # Check if user is an admin in this gully
    is_admin = await check_admin_status(user.id, gully_id)
    if not is_admin:
        await update.message.reply_text(
            "You don't have admin permissions in this gully."
        )
        return

    # Get gully info
    gully = await api_client.get_gully(gully_id)

    # Create settings keyboard
    keyboard = [
        [
            InlineKeyboardButton(
                "Edit Name", callback_data=f"settings_name_{gully_id}"
            ),
            InlineKeyboardButton(
                "Edit Dates", callback_data=f"settings_dates_{gully_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                "Auction Settings", callback_data=f"settings_auction_{gully_id}"
            ),
            InlineKeyboardButton(
                "Transfer Settings", callback_data=f"settings_transfer_{gully_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                "Match Settings", callback_data=f"settings_match_{gully_id}"
            ),
            InlineKeyboardButton(
                "Notification Settings", callback_data=f"settings_notify_{gully_id}"
            ),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    message = (
        f"⚙️ *Gully Settings - {gully.get('name')}* ⚙️\n\n"
        f"Configure settings for your gully:\n\n"
        f"*Current Settings:*\n"
        f"• Name: {gully.get('name')}\n"
        f"• Start Date: {gully.get('start_date')}\n"
        f"• End Date: {gully.get('end_date')}\n"
        f"• Status: {gully.get('status')}\n\n"
        f"Select an option below to modify settings:"
    )

    await update.message.reply_text(
        message, reply_markup=reply_markup, parse_mode="Markdown"
    )


# Invite link command
async def invite_link_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle the /invite_link command to generate a custom invite link."""
    user = update.effective_user

    # Get user from database
    db_user = await api_client.get_user(user.id)
    if not db_user:
        await update.message.reply_text(
            "You need to register first. Use /start to register."
        )
        return

    # Get active gully
    active_gully_id = await get_active_gully_id(user.id, context)
    if not active_gully_id:
        await update.message.reply_text(
            "You need to have an active gully to generate an invite link. "
            "Use /my_gullies to view and select a gully."
        )
        return

    # Check if user is an admin in this gully
    is_admin = await check_admin_status(user.id, active_gully_id)
    if not is_admin:
        await update.message.reply_text(
            "You don't have admin permissions in this gully."
        )
        return

    # Parse expiration time if provided
    expiration_hours = 24  # Default
    if context.args and len(context.args) > 0:
        try:
            expiration_hours = int(context.args[0])
            if expiration_hours < 1 or expiration_hours > 168:  # Max 1 week
                raise ValueError("Invalid expiration time")
        except ValueError:
            await update.message.reply_text(
                "Invalid expiration time. Please provide a number of hours between 1 and 168."
            )
            return

    # Generate invite link
    try:
        result = await api_client.generate_invite_link(
            gully_id=active_gully_id, expiration_hours=expiration_hours
        )

        if result.get("invite_link"):
            await update.message.reply_text(
                f"🔗 *Invite Link Generated* 🔗\n\n"
                f"Gully: *{result.get('gully_name')}*\n"
                f"Expires in: *{result.get('expires_in')}*\n\n"
                f"Link: {result.get('invite_link')}\n\n"
                f"Share this link with users you want to invite to your gully.",
                parse_mode="Markdown",
            )
        else:
            await update.message.reply_text(
                f"Failed to generate invite link: {result.get('detail', 'Unknown error')}"
            )
    except Exception as e:
        await update.message.reply_text(f"Error generating invite link: {str(e)}")


# Setup wizard command
async def setup_wizard_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle the /setup_wizard command to launch or resume the gully setup wizard."""
    user = update.effective_user

    # Get user from database
    db_user = await api_client.get_user(user.id)
    if not db_user:
        await update.message.reply_text(
            "You need to register first. Use /start to register."
        )
        return

    # Get active gully
    active_gully_id = await get_active_gully_id(user.id, context)
    if not active_gully_id:
        await update.message.reply_text(
            "You need to have an active gully to use the setup wizard. "
            "Use /my_gullies to view and select a gully."
        )
        return

    # Check if user is an admin in this gully
    is_admin = await check_admin_status(user.id, active_gully_id)
    if not is_admin:
        await update.message.reply_text(
            "You don't have admin permissions in this gully."
        )
        return

    # Start the setup wizard
    # Store the current step in context.user_data
    context.user_data["setup_wizard"] = {
        "gully_id": active_gully_id,
        "step": 1,
        "total_steps": 5,
    }

    # Show first step
    await show_setup_wizard_step(update, context)


# Admin roles command
async def admin_roles_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle the /admin_roles command to manage granular admin permissions."""
    user = update.effective_user

    # Get user from database
    db_user = await api_client.get_user(user.id)
    if not db_user:
        await update.message.reply_text(
            "You need to register first. Use /start to register."
        )
        return

    # Get active gully
    active_gully_id = await get_active_gully_id(user.id, context)
    if not active_gully_id:
        await update.message.reply_text(
            "You need to have an active gully to manage admin roles. "
            "Use /my_gullies to view and select a gully."
        )
        return

    # Check if user is an admin in this gully
    is_admin = await check_admin_status(user.id, active_gully_id)
    if not is_admin:
        await update.message.reply_text(
            "You don't have admin permissions in this gully."
        )
        return

    # Get all admins for this gully
    try:
        admins = await api_client.get_gully_admins(active_gully_id)

        # Create keyboard with admin usernames
        keyboard = []
        for admin in admins:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"{admin.get('username')} ({admin.get('role')})",
                        callback_data=f"admin_perm_{active_gully_id}_{admin.get('user_id')}",
                    )
                ]
            )

        # Add button to add new admin
        keyboard.append(
            [
                InlineKeyboardButton(
                    "Add New Admin", callback_data=f"admin_add_{active_gully_id}"
                )
            ]
        )

        reply_markup = InlineKeyboardMarkup(keyboard)

        # Get gully info
        gully = await api_client.get_gully(active_gully_id)

        message = (
            f"👥 *Admin Roles - {gully.get('name')}* 👥\n\n"
            f"Select an admin to view or modify their permissions:\n\n"
        )

        await update.message.reply_text(
            message, reply_markup=reply_markup, parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"Error fetching admin roles: {str(e)}")


# Helper functions


async def check_admin_status(user_id: int, gully_id: int) -> bool:
    """Check if a user is an admin in a specific gully."""
    try:
        # Get user permissions
        permissions = await api_client.get_user_permissions(user_id, gully_id)

        # If any permissions exist, user is an admin
        return len(permissions) > 0
    except Exception:
        # If API call fails, assume not an admin
        return False


async def show_setup_wizard_step(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Show the current step of the setup wizard."""
    wizard_data = context.user_data.get("setup_wizard", {})
    step = wizard_data.get("step", 1)
    gully_id = wizard_data.get("gully_id")

    # Get gully info
    gully = await api_client.get_gully(gully_id)

    # Define steps
    steps = {
        1: {
            "title": "Basic Information",
            "description": "Configure basic gully information like name and description.",
            "callback": "wizard_basic",
        },
        2: {
            "title": "Dates and Schedule",
            "description": "Set start and end dates for your gully.",
            "callback": "wizard_dates",
        },
        3: {
            "title": "Auction Settings",
            "description": "Configure auction rules and schedule.",
            "callback": "wizard_auction",
        },
        4: {
            "title": "Team Settings",
            "description": "Configure team rules and requirements.",
            "callback": "wizard_teams",
        },
        5: {
            "title": "Notification Settings",
            "description": "Configure notification preferences for your gully.",
            "callback": "wizard_notify",
        },
    }

    current_step = steps.get(step, steps[1])

    # Create navigation keyboard
    keyboard = []

    # Add step-specific buttons
    if step == 1:
        keyboard.append(
            [
                InlineKeyboardButton(
                    "Edit Name",
                    callback_data=f"{current_step['callback']}_name_{gully_id}",
                ),
                InlineKeyboardButton(
                    "Edit Description",
                    callback_data=f"{current_step['callback']}_desc_{gully_id}",
                ),
            ]
        )
    elif step == 2:
        keyboard.append(
            [
                InlineKeyboardButton(
                    "Edit Start Date",
                    callback_data=f"{current_step['callback']}_start_{gully_id}",
                ),
                InlineKeyboardButton(
                    "Edit End Date",
                    callback_data=f"{current_step['callback']}_end_{gully_id}",
                ),
            ]
        )
    elif step == 3:
        keyboard.append(
            [
                InlineKeyboardButton(
                    "Edit Auction Type",
                    callback_data=f"{current_step['callback']}_type_{gully_id}",
                ),
                InlineKeyboardButton(
                    "Edit Budget",
                    callback_data=f"{current_step['callback']}_budget_{gully_id}",
                ),
            ]
        )
    elif step == 4:
        keyboard.append(
            [
                InlineKeyboardButton(
                    "Edit Team Size",
                    callback_data=f"{current_step['callback']}_size_{gully_id}",
                ),
                InlineKeyboardButton(
                    "Edit Team Rules",
                    callback_data=f"{current_step['callback']}_rules_{gully_id}",
                ),
            ]
        )
    elif step == 5:
        keyboard.append(
            [
                InlineKeyboardButton(
                    "Edit Group Notifications",
                    callback_data=f"{current_step['callback']}_group_{gully_id}",
                ),
                InlineKeyboardButton(
                    "Edit Private Notifications",
                    callback_data=f"{current_step['callback']}_private_{gully_id}",
                ),
            ]
        )

    # Add navigation buttons
    nav_buttons = []
    if step > 1:
        nav_buttons.append(
            InlineKeyboardButton("⬅️ Previous", callback_data=f"wizard_prev_{gully_id}")
        )

    nav_buttons.append(
        InlineKeyboardButton("Skip", callback_data=f"wizard_skip_{gully_id}")
    )

    if step < len(steps):
        nav_buttons.append(
            InlineKeyboardButton("Next ➡️", callback_data=f"wizard_next_{gully_id}")
        )
    else:
        nav_buttons.append(
            InlineKeyboardButton("Finish ✅", callback_data=f"wizard_finish_{gully_id}")
        )

    keyboard.append(nav_buttons)

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Create progress indicator
    progress = "🔘" * (step - 1) + "⚪" + "⚫" * (len(steps) - step)

    message = (
        f"🧙‍♂️ *Setup Wizard - {gully.get('name')}* 🧙‍♂️\n\n"
        f"Step {step}/{len(steps)}: *{current_step['title']}*\n"
        f"{progress}\n\n"
        f"{current_step['description']}\n\n"
        f"*Current Settings:*\n"
    )

    # Add step-specific current settings
    if step == 1:
        message += (
            f"• Name: {gully.get('name')}\n"
            f"• Description: {gully.get('description', 'Not set')}\n"
        )
    elif step == 2:
        message += (
            f"• Start Date: {gully.get('start_date')}\n"
            f"• End Date: {gully.get('end_date')}\n"
        )
    elif step == 3:
        message += (
            f"• Auction Type: {gully.get('auction_type', 'Standard')}\n"
            f"• Budget: {gully.get('budget', '100')} Cr\n"
        )
    elif step == 4:
        message += (
            f"• Team Size: {gully.get('team_size', '18')} players\n"
            f"• Team Rules: {gully.get('team_rules', 'Standard')}\n"
        )
    elif step == 5:
        message += (
            f"• Group Notifications: {gully.get('group_notifications', 'Enabled')}\n"
            f"• Private Notifications: {gully.get('private_notifications', 'Enabled')}\n"
        )

    await update.message.reply_text(
        message, reply_markup=reply_markup, parse_mode="Markdown"
    )
