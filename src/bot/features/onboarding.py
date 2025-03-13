"""
Onboarding feature module for GullyGuru bot.
Handles user registration and team setup.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.bot import api_client, initialize_api_client

# Configure logging
logger = logging.getLogger(__name__)

# States for conversation handler
TEAM_NAME = 1


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /start command in private chat."""
    user = update.effective_user
    chat = update.effective_chat

    # Only allow in private chats
    if chat.type != "private":
        return ConversationHandler.END

    # Ensure API client is initialized
    await initialize_api_client()

    # Check if user came from deep link
    args = context.args
    telegram_group_id = None

    if args and args[0].startswith("group_"):
        try:
            telegram_group_id = int(args[0].split("_")[1])
            logger.info(
                f"User {user.id} started registration from group {telegram_group_id}"
            )
        except (ValueError, IndexError):
            logger.warning(f"Invalid deep link parameter: {args[0]}")

    # Create or get user record
    db_user = await api_client.users.get_user(user.id)
    if not db_user:
        logger.info(f"Creating new user for {user.username} (ID: {user.id})")
        db_user = await api_client.users.create_user(
            {
                "telegram_id": user.id,
                "username": user.username or "",
                "full_name": f"{user.first_name} {user.last_name or ''}".strip(),
            }
        )

    if not db_user:
        await update.message.reply_text(
            "❌ Sorry, there was an error with your account. Please try again later."
        )
        return ConversationHandler.END

    # If no telegram_group_id, show list of available gullies
    if not telegram_group_id:
        # Get user's gullies
        participations = await api_client.gullies.get_user_gully_participations(
            db_user["id"]
        )

        if not participations:
            await update.message.reply_text(
                "You are not a member of any gully. Please join a group with our bot first."
            )
            return ConversationHandler.END

        # Show list of gullies
        keyboard = []
        for p in participations:
            gully = await api_client.gullies.get_gully(p["gully_id"])
            if gully:
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            gully["name"], callback_data=f"onboard_gully_{gully['id']}"
                        )
                    ]
                )

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Please select a gully to set up your team:", reply_markup=reply_markup
        )
        return ConversationHandler.END

    # Get gully by telegram_group_id
    gully = await api_client.gullies.get_gully_by_group(telegram_group_id)
    if not gully:
        await update.message.reply_text(
            "This gully no longer exists. Please join a group with our bot first."
        )
        return ConversationHandler.END

    # Check if user is already in gully
    participation = await api_client.gullies.get_user_gully_participation(
        user_id=db_user["id"], gully_id=gully["id"]
    )

    # If not in gully, add user to gully
    if not participation:
        # Default role is member
        role = "member"

        # Add user to gully
        logger.info(f"Adding user {db_user['id']} as member to gully {gully['id']}")
        participation = await api_client.gullies.add_user_to_gully(
            user_id=db_user["id"], gully_id=gully["id"], role=role
        )

    # If user already has a team name, show welcome back message
    if participation and participation.get("team_name"):
        # Show different message based on role
        if participation.get("role") == "admin":
            # Show admin message
            keyboard = [
                [
                    InlineKeyboardButton(
                        "Manage Gully", callback_data=f"admin_manage_{gully['id']}"
                    ),
                    InlineKeyboardButton(
                        "View Participants",
                        callback_data=f"admin_participants_{gully['id']}",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Build Squad", callback_data=f"team_build_{gully['id']}"
                    ),
                    InlineKeyboardButton("Help / Commands", callback_data="help"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"Welcome back to Gully '{gully['name']}'!\n\n"
                f"Your team '{participation['team_name']}' is ready.\n\n"
                f"As an admin, you can manage the gully or participate as a player.",
                reply_markup=reply_markup,
            )
        else:
            # Show member message
            keyboard = [
                [
                    InlineKeyboardButton(
                        "Build Squad", callback_data=f"team_build_{gully['id']}"
                    ),
                    InlineKeyboardButton("Help / Commands", callback_data="help"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"Welcome back to Gully '{gully['name']}'!\n\n"
                f"Your team '{participation['team_name']}' is ready.",
                reply_markup=reply_markup,
            )

        return ConversationHandler.END

    # Store gully_id in user_data for later use
    context.user_data["gully_id"] = gully["id"]

    # Ask for team name
    keyboard = [
        [
            InlineKeyboardButton("Enter Team Name", callback_data="enter_team_name"),
            InlineKeyboardButton("Cancel", callback_data="cancel"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Show different message based on role
    if participation and participation.get("role") == "admin":
        await update.message.reply_text(
            f"Welcome to Gully '{gully['name']}'!\n\n"
            f"You're also the admin.\n"
            f"But let's set up your team as well!",
            reply_markup=reply_markup,
        )
    else:
        await update.message.reply_text(
            f"Welcome to Gully '{gully['name']}'!\n\n"
            f"Let's set up your fantasy team.",
            reply_markup=reply_markup,
        )

    return TEAM_NAME


async def enter_team_name_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle enter_team_name callback."""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "Please enter a name for your team:", reply_markup=None
    )

    return TEAM_NAME


async def cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle cancel callback."""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "Registration cancelled. You can restart anytime with /start.",
        reply_markup=None,
    )

    return ConversationHandler.END


async def team_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle team name input."""
    user = update.effective_user
    team_name = update.message.text.strip()

    # Get gully_id from user_data
    gully_id = context.user_data.get("gully_id")
    if not gully_id:
        await update.message.reply_text(
            "Sorry, there was an error with your registration. Please try again with /start."
        )
        return ConversationHandler.END

    # Get user from database
    db_user = await api_client.users.get_user(user.id)
    if not db_user:
        await update.message.reply_text(
            "❌ Sorry, there was an error with your account. Please try again later."
        )
        return ConversationHandler.END

    # Get gully
    gully = await api_client.gullies.get_gully(gully_id)
    if not gully:
        await update.message.reply_text(
            "This gully no longer exists. Please join a group with our bot first."
        )
        return ConversationHandler.END

    # Update team name
    logger.info(
        f"Setting team name '{team_name}' for user {db_user['id']} in gully {gully_id}"
    )
    participation = await api_client.gullies.update_user_gully_participation(
        user_id=db_user["id"], gully_id=gully_id, team_name=team_name
    )

    if not participation:
        await update.message.reply_text(
            "❌ Sorry, there was an error updating your team name. Please try again later."
        )
        return ConversationHandler.END

    # Show different message based on role
    if participation.get("role") == "admin":
        # Show admin message
        keyboard = [
            [
                InlineKeyboardButton(
                    "Manage Gully", callback_data=f"admin_manage_{gully_id}"
                ),
                InlineKeyboardButton(
                    "View Participants", callback_data=f"admin_participants_{gully_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    "Build Squad", callback_data=f"team_build_{gully_id}"
                ),
                InlineKeyboardButton("Help / Commands", callback_data="help"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"Team '{team_name}' is set!\n\n"
            f"Admin Tools:\n"
            f"[ Manage Gully ]  [ View Participants ]\n\n"
            f"Also as a player, you can:\n"
            f"[ Build Squad ]  [ Help / Commands ]",
            reply_markup=reply_markup,
        )
    else:
        # Show member message
        keyboard = [
            [
                InlineKeyboardButton(
                    "Build Squad", callback_data=f"team_build_{gully_id}"
                ),
                InlineKeyboardButton("Help / Commands", callback_data="help"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"Your team '{team_name}' is set!\n\n"
            f"Next steps:\n"
            f"[ Build Squad ]\n"
            f"[ Help / Commands ]",
            reply_markup=reply_markup,
        )

    return ConversationHandler.END


async def onboard_gully_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle onboard_gully callback."""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    data = query.data

    # Extract gully_id from callback data
    try:
        gully_id = int(data.split("_")[2])
    except (ValueError, IndexError):
        await query.edit_message_text(
            "Invalid gully selection. Please try again with /start."
        )
        return ConversationHandler.END

    # Store gully_id in user_data
    context.user_data["gully_id"] = gully_id

    # Get gully
    gully = await api_client.gullies.get_gully(gully_id)
    if not gully:
        await query.edit_message_text(
            "This gully no longer exists. Please join a group with our bot first."
        )
        return ConversationHandler.END

    # Get user from database
    db_user = await api_client.users.get_user(user.id)
    if not db_user:
        await query.edit_message_text(
            "❌ Sorry, there was an error with your account. Please try again later."
        )
        return ConversationHandler.END

    # Check if user is already in gully
    participation = await api_client.gullies.get_user_gully_participation(
        user_id=db_user["id"], gully_id=gully_id
    )

    # If user already has a team name, show welcome back message
    if participation and participation.get("team_name"):
        # Show different message based on role
        if participation.get("role") == "admin":
            # Show admin message
            keyboard = [
                [
                    InlineKeyboardButton(
                        "Manage Gully", callback_data=f"admin_manage_{gully_id}"
                    ),
                    InlineKeyboardButton(
                        "View Participants",
                        callback_data=f"admin_participants_{gully_id}",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Build Squad", callback_data=f"team_build_{gully_id}"
                    ),
                    InlineKeyboardButton("Help / Commands", callback_data="help"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                f"Welcome back to Gully '{gully['name']}'!\n\n"
                f"Your team '{participation['team_name']}' is ready.\n\n"
                f"As an admin, you can manage the gully or participate as a player.",
                reply_markup=reply_markup,
            )
        else:
            # Show member message
            keyboard = [
                [
                    InlineKeyboardButton(
                        "Build Squad", callback_data=f"team_build_{gully_id}"
                    ),
                    InlineKeyboardButton("Help / Commands", callback_data="help"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                f"Welcome back to Gully '{gully['name']}'!\n\n"
                f"Your team '{participation['team_name']}' is ready.",
                reply_markup=reply_markup,
            )

        return ConversationHandler.END

    # Ask for team name
    keyboard = [
        [
            InlineKeyboardButton("Enter Team Name", callback_data="enter_team_name"),
            InlineKeyboardButton("Cancel", callback_data="cancel"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Show different message based on role
    if participation and participation.get("role") == "admin":
        await query.edit_message_text(
            f"Welcome to Gully '{gully['name']}'!\n\n"
            f"You're also the admin.\n"
            f"But let's set up your team as well!",
            reply_markup=reply_markup,
        )
    else:
        await query.edit_message_text(
            f"Welcome to Gully '{gully['name']}'!\n\n"
            f"Let's set up your fantasy team.",
            reply_markup=reply_markup,
        )

    return TEAM_NAME


# Create conversation handler
onboarding_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start_command)],
    states={
        TEAM_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, team_name_handler),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(enter_team_name_callback, pattern="^enter_team_name$"),
        CallbackQueryHandler(cancel_callback, pattern="^cancel$"),
        CallbackQueryHandler(onboard_gully_callback, pattern="^onboard_gully_"),
    ],
)


# Register handlers
def register_onboarding_handlers(application):
    """Register onboarding handlers."""
    application.add_handler(onboarding_conv_handler)
    logger.info("Onboarding handlers registered successfully")
