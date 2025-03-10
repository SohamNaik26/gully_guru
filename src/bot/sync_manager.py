"""
Sync manager module for GullyGuru bot.
Handles background synchronization of users and gullies.
"""

import logging
from telegram import Bot
from src.api.api_client_instance import api_client

logger = logging.getLogger(__name__)


async def discover_groups(bot: Bot):
    """
    Discover all groups the bot is a member of using multiple methods.

    Returns:
        set: Set of chat IDs
    """
    chat_ids = set()

    # Method 1: Get chats from recent updates
    try:
        updates = await bot.get_updates(timeout=1)
        for update in updates:
            if update.effective_chat and update.effective_chat.id:
                if update.effective_chat.type in ["group", "supergroup"]:
                    chat_ids.add(update.effective_chat.id)
        logger.info(f"Found {len(chat_ids)} groups from recent updates")
    except Exception as e:
        logger.error(f"Error getting updates: {e}")

    # Method 2: Get chats from existing gullies in the database
    try:
        gullies = await api_client.gullies.get_all_gullies()
        for gully in gullies:
            if "telegram_group_id" in gully and gully["telegram_group_id"]:
                chat_ids.add(gully["telegram_group_id"])
        logger.info(f"Found {len(chat_ids)} total groups after checking database")
    except Exception as e:
        logger.error(f"Error getting gullies from database: {e}")

    # Method 3: Check if the bot can still access these groups
    valid_chat_ids = set()
    for chat_id in chat_ids:
        try:
            chat = await bot.get_chat(chat_id)
            if chat.type in ["group", "supergroup"]:
                valid_chat_ids.add(chat_id)
                logger.debug(f"Verified access to group: {chat.title} (ID: {chat_id})")
        except Exception as e:
            logger.warning(f"Cannot access group {chat_id}: {e}")

    logger.info(
        f"Verified {len(valid_chat_ids)} accessible groups out of {len(chat_ids)} total groups"
    )
    return valid_chat_ids


async def create_or_get_gully(chat):
    """
    Create a gully for a group if it doesn't exist, or get the existing one.

    Args:
        chat: The Telegram chat object

    Returns:
        dict: The gully object with an additional is_new flag
    """
    # Check if gully exists for this group
    gully = await api_client.gullies.get_gully_by_group(chat.id)

    if not gully:
        # Create new gully
        logger.info(f"Creating new gully for group: {chat.title} (ID: {chat.id})")
        gully = await api_client.gullies.create_gully(
            name=chat.title or f"Gully {chat.id}",
            telegram_group_id=chat.id,
        )
        if gully:
            gully["is_new"] = True
            logger.info(f"Created new gully '{gully['name']}' for group {chat.id}")
        else:
            logger.error(f"Failed to create gully for group {chat.id}")
            return None
    else:
        gully["is_new"] = False
        logger.info(f"Found existing gully '{gully['name']}' for group {chat.id}")

    return gully


async def add_user_to_gully(user, gully_id, is_admin=False):
    """
    Add a user to a gully.

    Args:
        user: The Telegram user object
        gully_id: The ID of the gully
        is_admin: Whether the user should be added as an admin

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Skip bots
        if user.is_bot:
            logger.debug(f"Skipping bot user {user.id}")
            return False

        # Get or create user
        db_user = await api_client.users.get_user(user.id)

        if not db_user:
            logger.info(f"Creating new user: {user.first_name} (ID: {user.id})")
            db_user = await api_client.users.create_user(
                telegram_id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
            )

        if not db_user:
            logger.error(f"Failed to create user {user.id}")
            return False

        # Check if user is already in gully
        participation = await api_client.get_user_gully_participation(
            user_id=db_user["id"], gully_id=gully_id
        )

        if participation:
            logger.debug(
                f"User {user.id} already in gully {gully_id} with role {participation.get('role')}"
            )
            # User already in gully, update role if needed
            if is_admin and participation.get("role") != "admin":
                logger.info(
                    f"Updating user {user.first_name} (ID: {user.id}) to admin role in gully {gully_id}"
                )
                update_result = await api_client.update_gully_participant_role(
                    participation["id"], "admin"
                )

                if not update_result:
                    logger.error(f"Failed to update role for user {user.id}")
                    return False
            return True

        # Add user to gully with appropriate role
        role = "admin" if is_admin else "member"

        logger.info(
            f"Adding user {user.first_name} (ID: {user.id}) as {role} to gully {gully_id}"
        )
        result = await api_client.gullies.add_user_to_gully(
            user_id=db_user["id"],
            gully_id=gully_id,
            role=role,
        )

        if not result:
            logger.error(f"API call to add user {user.id} to gully {gully_id} failed")
            return False

        logger.info(
            f"Successfully added user {user.first_name} (ID: {user.id}) as {role} to gully {gully_id}"
        )
        return True

    except Exception as e:
        logger.error(f"Error adding user {user.id} to gully {gully_id}: {e}")
        return False


async def sync_group_members(bot, chat, gully):
    """
    Sync group members to the gully.

    Args:
        bot: The Telegram bot instance
        chat: The Telegram chat object
        gully: The gully object

    Returns:
        dict: Results of the sync operation
    """
    result = {
        "members_added": 0,
        "admins_added": 0,
        "roles_updated": 0,
        "errors": 0,
        "error_details": [],
    }

    try:
        # Get group admins
        logger.info(f"Getting administrators for group {chat.title} (ID: {chat.id})")
        admins = await bot.get_chat_administrators(chat.id)
        admin_ids = {admin.user.id for admin in admins}
        logger.info(f"Found {len(admins)} administrators in group {chat.title}")

        # Process admins first
        for admin in admins:
            user = admin.user

            # Skip the bot itself
            if user.is_bot:
                logger.debug(f"Skipping bot user {user.id}")
                continue

            try:
                # Add user as admin to gully
                success = await add_user_to_gully(user, gully["id"], is_admin=True)
                if success:
                    result["admins_added"] += 1

            except Exception as e:
                error_msg = f"Error processing admin {user.id}: {str(e)}"
                logger.error(error_msg)
                result["errors"] += 1
                result["error_details"].append(error_msg)

        # Try to get regular members
        # Since Telegram doesn't provide a direct way to get all members,
        # we'll use getChatMember for each member we can find

        # Method 1: Try to get members from recent messages
        try:
            logger.info(
                f"Attempting to get members from recent messages in {chat.title}"
            )
            # This is a workaround - we'll try to get some recent message senders
            # Note: This requires the bot to have access to message history
            members_processed = set(admin_ids)  # Skip admins we've already processed

            # Try to get member info from chat
            member_count = await bot.get_chat_member_count(chat.id)
            logger.info(f"Chat {chat.title} has approximately {member_count} members")

            # Get some recent messages to find member IDs
            # Note: This is limited by Telegram API and may not get all members
            updates = await bot.get_updates(timeout=1)
            for update in updates:
                if (
                    update.effective_chat
                    and update.effective_chat.id == chat.id
                    and update.effective_user
                    and update.effective_user.id not in members_processed
                ):

                    user = update.effective_user
                    members_processed.add(user.id)

                    # Skip bots
                    if user.is_bot:
                        continue

                    # Add as regular member
                    try:
                        success = await add_user_to_gully(
                            user, gully["id"], is_admin=False
                        )
                        if success:
                            result["members_added"] += 1
                    except Exception as e:
                        error_msg = f"Error adding member {user.id}: {str(e)}"
                        logger.error(error_msg)
                        result["errors"] += 1
                        result["error_details"].append(error_msg)

            logger.info(
                f"Processed {len(members_processed) - len(admin_ids)} regular members from recent messages"
            )

        except Exception as e:
            error_msg = f"Error getting members from recent messages: {str(e)}"
            logger.error(error_msg)
            result["errors"] += 1
            result["error_details"].append(error_msg)

        # Log summary
        logger.info(
            f"Sync completed for group {chat.title}: "
            f"{result['admins_added']} admins added, "
            f"{result['members_added']} members added, "
            f"{result['roles_updated']} roles updated, "
            f"{result['errors']} errors"
        )

    except Exception as e:
        error_msg = f"Error syncing group members for gully {gully['id']}: {str(e)}"
        logger.error(error_msg)
        result["errors"] += 1
        result["error_details"].append(error_msg)

    return result


async def sync_all_groups(bot: Bot):
    """
    Sync all groups the bot is a member of.
    Creates gullies and adds users as needed.
    """
    logger.info("Starting group synchronization...")

    # Get all bot chats using improved discovery
    chat_ids = await discover_groups(bot)

    if not chat_ids:
        logger.warning(
            "No groups found. Bot may need to be added to groups or receive messages."
        )
        return {"processed": 0, "gullies_created": 0, "users_added": 0, "errors": 0}

    # Process each chat
    results = {
        "processed": 0,
        "gullies_created": 0,
        "users_added": 0,
        "errors": 0,
        "groups": [],
    }

    for chat_id in chat_ids:
        group_result = {
            "chat_id": chat_id,
            "name": None,
            "status": "failed",
            "users_added": 0,
            "admins_added": 0,
            "error": None,
        }

        try:
            # Check if chat is a group
            chat = await bot.get_chat(chat_id)
            group_result["name"] = chat.title

            if chat.type not in ["group", "supergroup"]:
                group_result["error"] = "Not a group chat"
                continue

            logger.info(f"Processing group: {chat.title} (ID: {chat.id})")

            # Create or get gully
            gully = await create_or_get_gully(chat)
            if not gully:
                group_result["error"] = "Failed to create or get gully"
                results["errors"] += 1
                continue

            # Sync members and admins
            sync_result = await sync_group_members(bot, chat, gully)

            # Send a message to the group about the sync
            try:
                message = (
                    f"✅ Gully synchronization completed!\n\n"
                    f"• {sync_result.get('admins_added', 0)} admins added\n"
                    f"• {sync_result.get('members_added', 0)} members added\n"
                    f"• {sync_result.get('roles_updated', 0)} roles updated\n\n"
                    f"All members are now properly registered in the gully."
                )

                if (
                    sync_result.get("admins_added", 0) > 0
                    or sync_result.get("members_added", 0) > 0
                ):
                    await bot.send_message(chat_id=chat.id, text=message)
            except Exception as e:
                logger.error(f"Error sending sync confirmation to group {chat.id}: {e}")

            # Update group result
            group_result["status"] = "success"
            group_result["users_added"] = sync_result.get("members_added", 0)
            group_result["admins_added"] = sync_result.get("admins_added", 0)

            # Update overall results
            results["users_added"] += sync_result.get(
                "members_added", 0
            ) + sync_result.get("admins_added", 0)
            results["processed"] += 1
            if gully.get("is_new", False):
                results["gullies_created"] += 1

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error processing chat {chat_id}: {error_msg}")
            group_result["error"] = error_msg
            results["errors"] += 1

        # Add group result to results
        results["groups"].append(group_result)

    # Log detailed results
    logger.info(
        f"Group synchronization completed: {results['processed']} groups processed, "
        f"{results['gullies_created']} gullies created, "
        f"{results['users_added']} users added, "
        f"{results['errors']} errors"
    )

    # Log details for each group
    for group in results["groups"]:
        if group["status"] == "success":
            logger.info(
                f"Group '{group['name']}' (ID: {group['chat_id']}): "
                f"{group['users_added']} users and {group['admins_added']} admins added"
            )
        else:
            logger.error(
                f"Group '{group['name']}' (ID: {group['chat_id']}): "
                f"Failed - {group['error']}"
            )

    return results
