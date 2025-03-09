"""
Handlers for the /join_gully command.
This is the entry point for users to join a gully.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from src.api.api_client_instance import api_client
from src.bot.services import user_service, gully_service

# Configure logging
logger = logging.getLogger(__name__)


async def join_gully_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the /join_gully command.
    This is the entry point for users to join a gully.

    In private chats: Provides information about available gullies.
    In gully chats: Adds the user to the current gully.
    """
    # Get the chat type
    chat_type = update.effective_chat.type

    # Handle gully chat scenario
    if chat_type in ["group", "supergroup"]:
        return await handle_gully_join(update, context)

    # Handle private chat scenario
    user = update.effective_user

    # Ensure user exists in database
    db_user = await user_service.ensure_user_exists(user)
    if not db_user:
        # User creation failed
        logger.error(f"Failed to create user {user.id} in database")
        await update.message.reply_text(
            "Sorry, there was an error registering your account. Please try again later."
        )
        return ConversationHandler.END

    # Check if this is a deep link from a gully invitation
    args = context.args
    from_gully = None
    if args and args[0].startswith("from_gully_"):
        try:
            from_gully = int(args[0].split("_")[2])
            logger.info(f"User {user.id} joining from gully {from_gully}")
        except (IndexError, ValueError) as e:
            logger.error(f"Error parsing from_gully parameter: {e}")

    # If from a gully, check if user is already in the gully
    if from_gully:
        gully = await api_client.gullies.get_gully_by_group(from_gully)
        if gully:
            gully_id = gully.get("id")
            gully_name = gully.get("name")

            # Check if user is already in the gully
            participant = await api_client.gullies.get_user_gully_participation(
                db_user["id"], gully_id
            )

            if participant:
                # User is already in the gully
                await update.message.reply_text(
                    f"You're already registered in *{gully_name}*.",
                    parse_mode="Markdown",
                )

                # Set this as the user's active gully if it's not already
                if not participant.get("is_active"):
                    await api_client.gullies.set_active_gully(participant["id"])
                    await update.message.reply_text(
                        "I've set this as your active gully."
                    )

                # Show next steps
                await show_next_steps(update, context, participant)
            else:
                # User is not in the gully, ask if they want to join
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Yes, join this gully",
                            callback_data=f"join_gully_{gully_id}",
                        ),
                        InlineKeyboardButton(
                            "No, thanks", callback_data="decline_gully"
                        ),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    f"Would you like to join the *{gully_name}* gully?",
                    reply_markup=reply_markup,
                    parse_mode="Markdown",
                )
        else:
            await update.message.reply_text(
                "Sorry, I couldn't find the gully you're trying to join. "
                "Please make sure you're using a valid invite link."
            )
    else:
        # No gully specified, show user's gullies
        participations = await api_client.gullies.get_user_gully_participations(
            db_user["id"]
        )

        if participations:
            # User is in at least one gully
            gully_list = "\n".join(
                [f"• *{p.get('gully_name')}*" for p in participations]
            )
            await update.message.reply_text(
                f"You're currently a member of the following gullies:\n\n{gully_list}\n\n"
                f"To join a new gully, you need to be added to a Telegram group with the GullyGuru bot.",
                parse_mode="Markdown",
            )

            # Show next steps for active gully
            active_gully = next((p for p in participations if p.get("is_active")), None)
            if active_gully:
                await show_next_steps(update, context, active_gully)
        else:
            # User is not in any gully
            await update.message.reply_text(
                "You're not currently a member of any gully. "
                "To join a gully, you need to be added to a Telegram group with the GullyGuru bot."
            )

    return ConversationHandler.END


async def handle_gully_join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the /join_gully command in a gully chat.
    This adds the user to the current gully.
    """
    chat = update.effective_chat
    user = update.effective_user
    chat_id = chat.id

    # Log the join command in a gully
    logger.info(
        f"Join command received in gully {chat.title} (ID: {chat_id}) from user {user.id}"
    )

    # Check if a gully exists for this chat
    gully = await api_client.gullies.get_gully_by_group(chat_id)

    if not gully:
        # No gully exists, create one
        await update.message.reply_text(
            "🏏 Welcome to GullyGuru! I'll help you set up a new fantasy cricket league for this group."
        )

        # Create a new gully with default settings
        gully_name = chat.title or f"Gully_{chat_id}"
        try:
            gully = await api_client.gullies.create_gully(
                name=gully_name,
                telegram_group_id=chat_id,
            )

            if not gully or not gully.get("id"):
                await update.message.reply_text(
                    "❌ Sorry, I couldn't create a new gully. Please try again later."
                )
                return ConversationHandler.END

            await update.message.reply_text(
                f"✅ Successfully created a new gully: *{gully_name}*",
                parse_mode="Markdown",
            )

            # Add the command sender as a regular member
            db_user = await user_service.ensure_user_exists(user)
            if db_user:
                # Add user to gully as a regular member
                participant = await gully_service.add_user_to_gully(
                    db_user["id"], gully["id"]
                )
                if participant:
                    # Set this as the user's active gully
                    await api_client.gullies.set_active_gully(participant["id"])

            # Set the group owner as admin
            owner_result = await gully_service.set_group_owner_as_admin(
                chat_id, gully["id"], context.bot
            )

            # If the command sender is the owner, inform them
            if (
                owner_result["success"]
                and owner_result["owner"]
                and owner_result["owner"].id == user.id
            ):
                await update.message.reply_text(
                    "As the group owner, you have been assigned as the gully admin.",
                    parse_mode="Markdown",
                )

        except Exception as e:
            logger.error(f"Error creating gully: {e}")
            await update.message.reply_text(
                "❌ Sorry, there was an error setting up the gully. Please try again later."
            )
            return ConversationHandler.END
    else:
        # Gully exists, welcome the user
        await update.message.reply_text(
            f"🏏 Welcome to the *{gully.get('name')}* fantasy cricket league!",
            parse_mode="Markdown",
        )

        # Auto-register the user who triggered the command
        db_user = await user_service.ensure_user_exists(user)
        if not db_user:
            await update.message.reply_text(
                "❌ Sorry, there was an error registering your account. Please try again later."
            )
            return ConversationHandler.END

        # Check if user is already part of the gully
        participant = await api_client.gullies.get_user_gully_participation(
            db_user["id"], gully["id"]
        )

        if participant:
            # User is already in the gully
            await update.message.reply_text(
                "You're already registered in this gully.",
                parse_mode="Markdown",
            )

            # Set this as the user's active gully if it's not already
            if not participant.get("is_active"):
                await api_client.gullies.set_active_gully(participant["id"])
                await update.message.reply_text("I've set this as your active gully.")
        else:
            # Add user to gully
            participant = await gully_service.add_user_to_gully(
                db_user["id"], gully["id"]
            )
            if participant:
                await update.message.reply_text(
                    f"✅ You've successfully joined the *{gully.get('name')}* gully!",
                    parse_mode="Markdown",
                )

                # Provide guidance on next steps
                bot_username = context.bot.username
                private_chat_link = (
                    f"https://t.me/{bot_username}?start=from_gully_{gully['id']}"
                )

                await update.message.reply_text(
                    "🏏 Here's what you can do next:\n\n"
                    "1️⃣ Use /my_team to view your team\n"
                    "2️⃣ Use /submit_squad to build your initial squad\n"
                    "3️⃣ Use /auction_status to check ongoing auctions\n\n"
                    "For more help, use /help or message me privately.",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Message me privately", url=private_chat_link
                                )
                            ]
                        ]
                    ),
                )
            else:
                await update.message.reply_text(
                    "❌ Sorry, there was an error adding you to the gully. Please try again later."
                )

    # Check for other members in the gully who aren't registered
    try:
        # Get all chat members
        chat_members = await context.bot.get_chat_administrators(chat_id)
        chat_members = [
            member.user for member in chat_members if not member.user.is_bot
        ]

        # Add the sender if they're not an admin
        if not any(member.id == user.id for member in chat_members):
            chat_members.append(user)

        # Check which members are not in the gully
        unregistered_members = []
        for member in chat_members:
            db_user = await api_client.users.get_user(member.id)
            if not db_user:
                unregistered_members.append(member)
                continue

            participant = await api_client.gullies.get_user_gully_participation(
                db_user["id"], gully["id"]
            )
            if not participant:
                unregistered_members.append(member)

        if unregistered_members:
            # Prompt unregistered members to join
            member_mentions = ", ".join(
                [
                    f"@{m.username}" if m.username else m.first_name
                    for m in unregistered_members
                ]
            )
            await update.message.reply_text(
                f"I noticed some members haven't joined the gully yet: {member_mentions}\n\n"
                f"Please use /join_gully to join and start playing!"
            )
    except Exception as e:
        logger.error(f"Error checking for unregistered members: {e}")

    return ConversationHandler.END


async def show_next_steps(
    update: Update, context: ContextTypes.DEFAULT_TYPE, participant: dict
) -> None:
    """
    Show the next steps for a user based on their current status in the gully.
    """
    # Check if registration is complete
    if not participant.get("registration_complete", False):
        await update.message.reply_text(
            "📝 *Next Steps:*\n\n"
            "1. Complete your registration by submitting your initial squad\n"
            "2. Use /submit_squad to select your 18 players\n"
            "3. Once your squad is submitted, you'll be ready to participate in auctions and transfers",
            parse_mode="Markdown",
        )
    else:
        # Registration is complete, show other options
        await update.message.reply_text(
            "📝 *Available Commands:*\n\n"
            "• /myteam - View your current team\n"
            "• /auction_status - Check the status of ongoing auctions\n"
            "• /game_guide - Learn about the game and cricket terminology",
            parse_mode="Markdown",
        )


async def handle_join_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle callbacks for join_gully command.
    """
    query = update.callback_query
    await query.answer()

    callback_data = query.data
    user = update.effective_user

    if callback_data.startswith("join_gully_"):
        # Extract gully ID from callback data
        try:
            gully_id = int(callback_data.split("_")[2])

            # Get user from database
            db_user = await user_service.ensure_user_exists(user)
            if not db_user:
                await query.edit_message_text(
                    "❌ Sorry, there was an error with your account. Please try again later."
                )
                return

            # Add user to gully
            participant = await gully_service.add_user_to_gully(db_user["id"], gully_id)
            if not participant:
                await query.edit_message_text(
                    "❌ Sorry, there was an error adding you to the gully. Please try again later."
                )
                return

            # Set this as the user's active gully
            await api_client.gullies.set_active_gully(participant["id"])

            # Get gully details
            gully = await api_client.gullies.get_gully(gully_id)
            gully_name = gully.get("name", "this gully") if gully else "this gully"

            # Confirm joining
            await query.edit_message_text(
                f"✅ You've successfully joined *{gully_name}*!\n\n"
                f"This is now your active gully.",
                parse_mode="Markdown",
            )

            # Show next steps
            await show_next_steps(update, context, participant)

        except (IndexError, ValueError) as e:
            logger.error(f"Error parsing join_gully callback data: {e}")
            await query.edit_message_text(
                "❌ Sorry, there was an error processing your request. Please try again later."
            )

    elif callback_data == "decline_gully":
        # User declined to join the gully
        await query.edit_message_text(
            "You've chosen not to join this gully. You can always join later by using the /join_gully command again."
        )


def get_join_gully_handlers():
    """
    Get the handlers for the join_gully command.
    """
    from telegram.ext import CommandHandler, CallbackQueryHandler

    return [
        CommandHandler("join_gully", join_gully_command),
        CallbackQueryHandler(
            handle_join_callback, pattern="^join_gully_|^decline_gully"
        ),
    ]
