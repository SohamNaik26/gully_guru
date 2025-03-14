"""
Onboarding feature module for GullyGuru bot.
Handles user registration, team setup, and automatic Gully creation.
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

from src.bot.api_client.onboarding import get_onboarding_client

# Configure logging
logger = logging.getLogger(__name__)

# Define conversation states
TEAM_NAME_BUTTON = 1
TEAM_NAME_INPUT = 2


async def bot_added_to_group(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle when the bot is added to a group.
    Automatically creates a new Gully and sets the user who added the bot as admin.
    """
    # Check if this is a new chat member event and if the bot was added
    if not update.message or not update.message.new_chat_members:
        return

    # Check if the bot was added
    bot = context.bot
    if not any(member.id == bot.id for member in update.message.new_chat_members):
        return

    # Get group information
    chat = update.effective_chat
    if not chat or chat.type not in ["group", "supergroup"]:
        return

    # Get the user who added the bot
    user = update.effective_user
    if not user:
        return

    logger.info(f"Bot was added to group {chat.id} ({chat.title}) by user {user.id}")

    # Get API client
    client = await get_onboarding_client()

    # Check if user exists, create if not
    db_user = await client.get_user(user.id)
    if not db_user:
        db_user = await client.create_user(
            telegram_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
        )
        if not db_user:
            logger.error(f"Failed to create user {user.id} when adding bot to group")
            await update.message.reply_text(
                "❌ There was an error setting up the Gully. Please try again later."
            )
            return

    # Check if gully already exists for this group
    existing_gully = await client.get_gully_by_telegram_id(chat.id)

    # Generate deep link for registration
    deep_link = f"https://t.me/{bot.username}?start=group_{chat.id}"
    register_button = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Register to Play", url=deep_link)]]
    )

    if existing_gully:
        logger.info(f"Gully already exists for group {chat.id}")
        # Send welcome message for existing gully
        await update.message.reply_text(
            f"Hello everyone! This group is already set up as Gully \"{existing_gully['name']}\".\n\n"
            f"To participate in the game, please open a private chat with me:",
            reply_markup=register_button,
        )
        return

    # Create new gully
    gully = await client.create_gully(
        name=chat.title, telegram_group_id=chat.id, creator_id=db_user["id"]
    )

    if not gully:
        logger.error(f"Failed to create gully for group {chat.id}")
        await update.message.reply_text(
            "❌ There was an error setting up the Gully. Please try again later."
        )
        return

    # Add the user who added the bot as admin
    await client.join_gully(user_id=db_user["id"], gully_id=gully["id"], role="admin")

    # Send welcome message for new gully
    await update.message.reply_text(
        f"Hello everyone! This group is now set up as Gully \"{gully['name']}\".\n\n"
        f"@{user.username or user.first_name} is the admin.\n\n"
        f"To participate in the game, please open a private chat with me:",
        reply_markup=register_button,
    )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle /start command in private chat.
    Initiates user registration and team setup.
    """
    user = update.effective_user
    chat = update.effective_chat

    # Only allow in private chats
    if chat.type != "private":
        return ConversationHandler.END

    # Get API client
    client = await get_onboarding_client()

    # Check if user came from deep link
    args = context.args
    telegram_group_id = None

    if args and args[0].startswith("group_"):
        try:
            telegram_group_id = int(args[0].split("_")[1])
            logger.info(
                f"User {user.id} started registration from group {telegram_group_id}"
            )
            context.user_data["telegram_group_id"] = telegram_group_id
        except (ValueError, IndexError):
            logger.warning(f"Invalid deep link parameter: {args[0]}")

    # Check if user exists in database
    db_user = await client.get_user(user.id)

    if not db_user:
        # New user, create user in database
        db_user = await client.create_user(
            telegram_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
        )

        if not db_user:
            await update.message.reply_text(
                "❌ Sorry, there was an error creating your account. Please try again later."
            )
            return ConversationHandler.END

        # Welcome message for new user with team name buttons
        keyboard = [
            [InlineKeyboardButton("Enter Team Name", callback_data="enter_team_name")],
            [InlineKeyboardButton("Cancel", callback_data="cancel_registration")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"👋 Welcome to GullyGuru, {user.first_name}!\n\n"
            f"Let's set up your team. Please choose an option:",
            reply_markup=reply_markup,
        )
        return TEAM_NAME_BUTTON

    # Existing user
    if telegram_group_id:
        # User came from a group, check if the gully exists
        gully = await client.get_gully_by_telegram_id(telegram_group_id)
        if not gully:
            await update.message.reply_text(
                "❌ The gully you're trying to join doesn't exist."
            )
            return ConversationHandler.END

        # Check if user is already in this gully
        participation = await client.get_user_gully_participation(
            user_id=db_user["id"], gully_id=gully["id"]
        )

        if participation:
            # User is already in this gully
            if participation.get("team_name"):
                # User already has a team name, show welcome back message
                context.user_data["active_gully_id"] = gully["id"]

                # Show different message based on role
                if participation.get("role") == "admin":
                    keyboard = [
                        [
                            InlineKeyboardButton(
                                "Manage Gully",
                                callback_data=f"admin_manage_{gully['id']}",
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
                            InlineKeyboardButton(
                                "Help / Commands", callback_data="help"
                            ),
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
                    keyboard = [
                        [
                            InlineKeyboardButton(
                                "Build Squad", callback_data=f"team_build_{gully['id']}"
                            ),
                            InlineKeyboardButton(
                                "Help / Commands", callback_data="help"
                            ),
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)

                    await update.message.reply_text(
                        f"Welcome back to Gully '{gully['name']}'!\n\n"
                        f"Your team '{participation['team_name']}' is ready.",
                        reply_markup=reply_markup,
                    )

                # Show main menu
                from src.bot.bot import show_main_menu

                await show_main_menu(update, context)
                return ConversationHandler.END
            else:
                # User is in gully but needs to set team name
                # Show different message based on role with team name buttons
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Enter Team Name", callback_data="enter_team_name"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Cancel", callback_data="cancel_registration"
                        )
                    ],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                if participation.get("role") == "admin":
                    await update.message.reply_text(
                        f"Welcome to Gully '{gully['name']}'!\n\n"
                        f"You're also the admin.\n"
                        f"But let's set up your team as well!\n\n"
                        f"Please choose an option:",
                        reply_markup=reply_markup,
                    )
                else:
                    await update.message.reply_text(
                        f"Welcome to Gully '{gully['name']}'!\n\n"
                        f"Let's set up your fantasy team.\n\n"
                        f"Please choose an option:",
                        reply_markup=reply_markup,
                    )
                return TEAM_NAME_BUTTON
        else:
            # User is not in this gully yet, ask for team name with buttons
            keyboard = [
                [
                    InlineKeyboardButton(
                        "Enter Team Name", callback_data="enter_team_name"
                    )
                ],
                [InlineKeyboardButton("Cancel", callback_data="cancel_registration")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"Welcome to Gully '{gully['name']}'!\n\n"
                f"Let's set up your fantasy team.\n\n"
                f"Please choose an option:",
                reply_markup=reply_markup,
            )
            return TEAM_NAME_BUTTON
    else:
        # No telegram_group_id, show user's gullies
        try:
            # Get user's gullies
            user_gullies = await client.get_user_gullies(db_user["id"])

            # Debug log to see the structure
            logger.debug(f"User gullies response: {user_gullies}")

            if user_gullies and len(user_gullies) > 0:
                # User has gullies, show selection
                keyboard = []

                # Check the structure of the response
                for gully in user_gullies:
                    # Debug log for each gully
                    logger.debug(f"Gully data: {gully}")

                    # Check if this is a direct gully object or needs to be fetched
                    if "id" in gully and "name" in gully:
                        # Direct gully object
                        gully_id = gully["id"]
                        gully_name = gully["name"]
                        keyboard.append(
                            [
                                InlineKeyboardButton(
                                    gully_name,
                                    callback_data=f"select_gully_{gully_id}",
                                )
                            ]
                        )
                    elif "gully_id" in gully:
                        # This is a participation object, need to fetch the gully
                        gully_id = gully["gully_id"]
                        gully_obj = await client.get_gully(gully_id)
                        if gully_obj:
                            keyboard.append(
                                [
                                    InlineKeyboardButton(
                                        gully_obj["name"],
                                        callback_data=f"select_gully_{gully_id}",
                                    )
                                ]
                            )
                    elif "gully" in gully and isinstance(gully["gully"], dict):
                        # This is a participation with embedded gully
                        gully_obj = gully["gully"]
                        gully_id = gully_obj.get("id")
                        if gully_id:
                            keyboard.append(
                                [
                                    InlineKeyboardButton(
                                        gully_obj.get("name", f"Gully {gully_id}"),
                                        callback_data=f"select_gully_{gully_id}",
                                    )
                                ]
                            )
                    else:
                        # Unknown structure, log it
                        logger.warning(f"Unknown gully structure: {gully}")

                if keyboard:
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.message.reply_text(
                        "Please select a gully to continue:",
                        reply_markup=reply_markup,
                    )
                    return ConversationHandler.END
                else:
                    # No valid gullies found, ask for team name with buttons
                    keyboard = [
                        [
                            InlineKeyboardButton(
                                "Enter Team Name", callback_data="enter_team_name"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "Cancel", callback_data="cancel_registration"
                            )
                        ],
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)

                    await update.message.reply_text(
                        "You haven't joined any gullies yet. "
                        "Please join a gully first by clicking the link in a group chat.\n\n"
                        "But let's set up your team name first:",
                        reply_markup=reply_markup,
                    )
                    return TEAM_NAME_BUTTON
            else:
                # User has no gullies, prompt to join one with team name buttons
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Enter Team Name", callback_data="enter_team_name"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Cancel", callback_data="cancel_registration"
                        )
                    ],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await update.message.reply_text(
                    "You haven't joined any gullies yet. "
                    "Please join a gully first by clicking the link in a group chat.\n\n"
                    "But let's set up your team name first:",
                    reply_markup=reply_markup,
                )
                return TEAM_NAME_BUTTON
        except Exception as e:
            # Log the error
            logger.error(f"Error getting user gullies: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ Sorry, there was an error retrieving your gullies. Please try again later."
            )
            return ConversationHandler.END


async def enter_team_name_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle the 'Enter Team Name' button click."""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "Please enter a name for your team (3-30 characters):"
    )
    return TEAM_NAME_INPUT


async def cancel_registration_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle the 'Cancel' button click."""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "Registration cancelled. You can restart by typing /start or clicking the registration link again."
    )
    return ConversationHandler.END


async def team_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle team name input."""
    user = update.effective_user
    team_name = update.message.text.strip()

    # Validate team name
    if len(team_name) < 3 or len(team_name) > 30:
        await update.message.reply_text(
            "Team name must be between 3 and 30 characters. Please try again:"
        )
        return TEAM_NAME_INPUT

    # Get API client
    client = await get_onboarding_client()

    # Get user from database
    db_user = await client.get_user(user.id)
    if not db_user:
        await update.message.reply_text(
            "❌ Sorry, there was an error with your account. Please try again later."
        )
        return ConversationHandler.END

    # Check if user came from a group (deep link)
    telegram_group_id = context.user_data.get("telegram_group_id")

    if telegram_group_id:
        # Try to join the gully
        gully = await client.get_gully_by_telegram_id(telegram_group_id)

        if gully:
            # Join the gully
            result = await client.join_gully(
                user_id=db_user["id"], gully_id=gully["id"], team_name=team_name
            )

            if result:
                # Set as active gully
                context.user_data["active_gully_id"] = gully["id"]

                # Get participation to check role
                participation = await client.get_user_gully_participation(
                    user_id=db_user["id"], gully_id=gully["id"]
                )

                if participation and participation.get("role") == "admin":
                    keyboard = [
                        [
                            InlineKeyboardButton(
                                "Manage Gully",
                                callback_data=f"admin_manage_{gully['id']}",
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
                            InlineKeyboardButton(
                                "Help / Commands", callback_data="help"
                            ),
                        ],
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)

                    await update.message.reply_text(
                        f"✅ Team '{team_name}' created successfully!\n\n"
                        f"You have joined the gully '{gully['name']}'.\n\n"
                        f"As an admin, you can manage the gully or participate as a player.",
                        reply_markup=reply_markup,
                    )
                else:
                    keyboard = [
                        [
                            InlineKeyboardButton(
                                "Build Squad", callback_data=f"team_build_{gully['id']}"
                            ),
                            InlineKeyboardButton(
                                "Help / Commands", callback_data="help"
                            ),
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)

                    await update.message.reply_text(
                        f"✅ Team '{team_name}' created successfully!\n\n"
                        f"You have joined the gully '{gully['name']}'.",
                        reply_markup=reply_markup,
                    )

                # Show main menu
                from src.bot.bot import show_main_menu

                await show_main_menu(update, context)
                return ConversationHandler.END
            else:
                await update.message.reply_text(
                    "❌ Failed to join the gully. Please try again later."
                )
                return ConversationHandler.END
        else:
            await update.message.reply_text(
                "❌ The gully you're trying to join doesn't exist."
            )
            return ConversationHandler.END
    else:
        # No gully specified, just save the team name for future use
        context.user_data["team_name"] = team_name
        await update.message.reply_text(
            f"✅ Team '{team_name}' created successfully!\n\n"
            f"You haven't joined any gullies yet. Please join a gully by clicking the link in a group chat."
        )

        # Show main menu
        from src.bot.bot import show_main_menu

        await show_main_menu(update, context)
        return ConversationHandler.END


async def select_gully_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle gully selection callback."""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    data = query.data

    # Get API client
    client = await get_onboarding_client()

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
    gully = await client.get_gully(gully_id)
    if not gully:
        await query.edit_message_text(
            "This gully no longer exists. Please join a group with our bot first."
        )
        return ConversationHandler.END

    # Get user from database
    db_user = await client.get_user(user.id)
    if not db_user:
        await query.edit_message_text(
            "❌ Sorry, there was an error with your account. Please try again later."
        )
        return ConversationHandler.END

    # Check if user is already in gully
    participation = await client.get_user_gully_participation(
        user_id=db_user["id"], gully_id=gully_id
    )

    # If user already has a team name, show welcome back message
    if participation and participation.get("team_name"):
        # Set as active gully
        context.user_data["active_gully_id"] = gully_id

        # Show different message based on role
        if participation.get("role") == "admin":
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
    else:
        # User needs to set team name
        context.user_data["telegram_group_id"] = gully["telegram_group_id"]

        # Show team name buttons
        keyboard = [
            [InlineKeyboardButton("Enter Team Name", callback_data="enter_team_name")],
            [InlineKeyboardButton("Cancel", callback_data="cancel_registration")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Show different message based on role
        if participation and participation.get("role") == "admin":
            await query.edit_message_text(
                f"Welcome to Gully '{gully['name']}'!\n\n"
                f"You're also the admin.\n"
                f"But let's set up your team as well!\n\n"
                f"Please choose an option:",
                reply_markup=reply_markup,
            )
        else:
            await query.edit_message_text(
                f"Welcome to Gully '{gully['name']}'!\n\n"
                f"Let's set up your fantasy team.\n\n"
                f"Please choose an option:",
                reply_markup=reply_markup,
            )

        return TEAM_NAME_BUTTON


# Create conversation handler
onboarding_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start_command)],
    states={
        TEAM_NAME_BUTTON: [
            CallbackQueryHandler(enter_team_name_callback, pattern="^enter_team_name$"),
            CallbackQueryHandler(
                cancel_registration_callback, pattern="^cancel_registration$"
            ),
        ],
        TEAM_NAME_INPUT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, team_name_handler),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(select_gully_callback, pattern="^select_gully_"),
    ],
)


# Register handlers
def register_onboarding_handlers(application, skip_new_chat_members=False):
    """Register onboarding handlers."""
    application.add_handler(onboarding_conv_handler)

    # Add handler for when bot is added to a group, but only if not skipped
    if not skip_new_chat_members:
        application.add_handler(
            MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, bot_added_to_group)
        )

    logger.info("Onboarding handlers registered successfully")
