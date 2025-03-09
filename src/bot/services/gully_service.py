"""
Service layer for gully operations.
Provides a clean interface for gully-related functionality.
"""

import logging
from typing import Dict, Any, List, Optional
from telegram import Bot

from src.api.api_client_instance import api_client

logger = logging.getLogger(__name__)


class GullyService:
    """Service for gully-related operations."""

    @staticmethod
    async def create_gully(
        name: str, telegram_group_id: int, creator_telegram_id: int = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new gully and optionally assign the creator as admin.

        Args:
            name: The name of the gully
            telegram_group_id: The Telegram group ID
            creator_telegram_id: The Telegram ID of the creator (optional)

        Returns:
            Optional[Dict]: The created gully data or None if failed
        """
        try:
            # Create the gully
            gully = await api_client.gullies.create_gully(
                name=name, telegram_group_id=telegram_group_id
            )

            if not gully:
                logger.error(
                    f"Failed to create gully {name} for group {telegram_group_id}"
                )
                return None

            # If creator ID is provided, assign them as admin
            if creator_telegram_id:
                # Get the user
                creator = await api_client.users.get_user(creator_telegram_id)
                if creator:
                    # Assign admin role
                    from src.bot.services.admin_service import admin_service

                    result = await admin_service.assign_admin_role(
                        creator["id"], gully["id"]
                    )
                    if not result.get("success", False):
                        logger.error(
                            f"Failed to assign admin role to creator: {result.get('error', 'Unknown error')}"
                        )
                else:
                    logger.error(f"Creator user {creator_telegram_id} not found")

            return gully
        except Exception as e:
            logger.error(f"Error creating gully: {str(e)}")
            return None

    @staticmethod
    async def set_group_owner_as_admin(
        chat_id: int, gully_id: int, bot: Bot
    ) -> Dict[str, Any]:
        """
        Set the Telegram group owner as the gully admin.

        Args:
            chat_id: The Telegram chat ID
            gully_id: The gully ID
            bot: The bot instance

        Returns:
            Dict: Result of the operation with success status and owner info
        """
        try:
            # Get all Telegram admins
            chat_admins = await bot.get_chat_administrators(chat_id)

            # Find the group owner (creator)
            group_owner = next(
                (admin for admin in chat_admins if admin.status == "creator"),
                None,
            )

            if not group_owner:
                logger.warning(f"No group owner found for chat {chat_id}")
                return {
                    "success": False,
                    "error": "No group owner found",
                    "owner": None,
                }

            # Ensure the owner exists in the database
            from src.bot.services.user_service import user_service

            owner_db_user = await user_service.ensure_user_exists(group_owner.user)
            if not owner_db_user:
                logger.error(
                    f"Failed to create user for group owner {group_owner.user.id}"
                )
                return {
                    "success": False,
                    "error": "Failed to create user for group owner",
                    "owner": group_owner.user,
                }

            # Add the owner to the gully
            owner_participant = await GullyService.add_user_to_gully(
                owner_db_user["id"], gully_id
            )

            if not owner_participant:
                logger.error(
                    f"Failed to add group owner {group_owner.user.id} to gully {gully_id}"
                )
                return {
                    "success": False,
                    "error": "Failed to add group owner to gully",
                    "owner": group_owner.user,
                }

            # Set the owner as admin
            from src.bot.services.admin_service import admin_service

            result = await admin_service.assign_admin_role(
                owner_db_user["id"], gully_id
            )
            if not result.get("success", False):
                logger.error(
                    f"Failed to assign admin role to group owner: {result.get('error', 'Unknown error')}"
                )
                return {
                    "success": False,
                    "error": "Failed to assign admin role to group owner",
                    "owner": group_owner.user,
                }

            logger.info(
                f"Set group owner {group_owner.user.id} as admin for gully {gully_id}"
            )

            # Process all other admins (not the owner)
            for admin in chat_admins:
                if admin.status != "creator" and not admin.user.is_bot:
                    # Ensure the admin exists in the database
                    admin_db_user = await user_service.ensure_user_exists(admin.user)

                    if admin_db_user:
                        # Add the admin to the gully as a regular member
                        await GullyService.add_user_to_gully(
                            admin_db_user["id"], gully_id
                        )

            return {
                "success": True,
                "message": "Group owner set as admin successfully",
                "owner": group_owner.user,
            }

        except Exception as e:
            logger.error(f"Error setting group owner as admin: {str(e)}")
            return {"success": False, "error": str(e), "owner": None}

    @staticmethod
    async def get_gully(gully_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a gully by ID.

        Args:
            gully_id: The gully ID

        Returns:
            Optional[Dict]: The gully data or None if not found
        """
        try:
            return await api_client.gullies.get_gully(gully_id)
        except Exception as e:
            logger.error(f"Error getting gully {gully_id}: {str(e)}")
            return None

    @staticmethod
    async def get_gully_by_group(group_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a gully by Telegram group ID.

        Args:
            group_id: The Telegram group ID

        Returns:
            Optional[Dict]: The gully data or None if not found
        """
        try:
            return await api_client.gullies.get_gully_by_group(group_id)
        except Exception as e:
            logger.error(f"Error getting gully by group {group_id}: {str(e)}")
            return None

    @staticmethod
    async def add_user_to_gully(
        user_id: int, gully_id: int, role: str = "member"
    ) -> Optional[Dict[str, Any]]:
        """
        Add a user to a gully with the specified role.

        Args:
            user_id: The user's database ID
            gully_id: The gully ID
            role: The role to assign (default: "member")

        Returns:
            Optional[Dict]: The created participation data or None if failed
        """
        try:
            # Check if user is already in the gully
            existing = await api_client.gullies.get_user_gully_participation(
                user_id, gully_id
            )
            if existing:
                logger.info(f"User {user_id} is already in gully {gully_id}")
                return existing

            # Add user to gully
            participation = await api_client.gullies.add_user_to_gully(
                user_id=user_id, gully_id=gully_id, role=role
            )

            if participation:
                logger.info(
                    f"Added user {user_id} to gully {gully_id} with role {role}"
                )
            else:
                logger.error(f"Failed to add user {user_id} to gully {gully_id}")

            return participation
        except Exception as e:
            logger.error(f"Error adding user to gully: {str(e)}")
            return None

    @staticmethod
    async def get_gully_participants(gully_id: int) -> List[Dict[str, Any]]:
        """
        Get all participants in a gully.

        Args:
            gully_id: The gully ID

        Returns:
            List[Dict]: List of participants
        """
        try:
            return await api_client.gullies.get_gully_participants(gully_id)
        except Exception as e:
            logger.error(f"Error getting gully participants: {str(e)}")
            return []

    @staticmethod
    async def get_user_gully_participations(user_id: int) -> List[Dict[str, Any]]:
        """
        Get all gullies a user is participating in.

        Args:
            user_id: The user's database ID

        Returns:
            List[Dict]: List of participations
        """
        try:
            return await api_client.gullies.get_user_gully_participations(user_id)
        except Exception as e:
            logger.error(f"Error getting user gully participations: {str(e)}")
            return []

    @staticmethod
    async def get_active_gullies() -> List[Dict[str, Any]]:
        """
        Get all active gullies.

        Returns:
            List[Dict]: List of active gullies
        """
        try:
            return await api_client.gullies.get_all_gullies()
        except Exception as e:
            logger.error(f"Error getting active gullies: {str(e)}")
            return []

    @staticmethod
    async def scan_and_setup_groups(bot: Bot) -> Dict[str, Any]:
        """
        Scan all groups where the bot is a member, create gullies if needed,
        and set group owners as admins.

        This should be run during bot initialization to ensure all groups
        have proper gully and admin setup.

        Args:
            bot: The bot instance

        Returns:
            dict: Summary of the operation with counts of groups processed,
                  gullies created, and admins set up
        """
        results = {
            "groups_scanned": 0,
            "gullies_created": 0,
            "admins_set": 0,
            "errors": 0,
            "details": [],
        }

        try:
            # Get bot updates to find all groups
            # Note: This approach has limitations as it only sees recent updates
            # A more comprehensive approach would require storing group IDs in the database
            updates = await bot.get_updates(limit=100, timeout=1)

            # Extract unique group IDs from updates
            group_ids = set()
            for update in updates:
                if update.message and update.message.chat.type in [
                    "group",
                    "supergroup",
                ]:
                    group_ids.add(update.message.chat.id)

            logger.info(f"Found {len(group_ids)} groups to scan")
            results["groups_scanned"] = len(group_ids)

            # Process each group
            for chat_id in group_ids:
                try:
                    # Check if a gully already exists for this group
                    gully = await GullyService.get_gully_by_group(chat_id)

                    # If no gully exists, create one
                    if not gully:
                        # Get chat info to use as gully name
                        chat = await bot.get_chat(chat_id)
                        gully_name = chat.title or f"Gully {chat_id}"

                        # Create the gully
                        gully = await GullyService.create_gully(
                            name=gully_name,
                            telegram_group_id=chat_id,
                        )

                        if gully:
                            logger.info(
                                f"Created new gully: {gully_name} (ID: {gully['id']}) for chat {chat_id}"
                            )
                            results["gullies_created"] += 1
                            results["details"].append(
                                {
                                    "action": "created_gully",
                                    "chat_id": chat_id,
                                    "gully_id": gully["id"],
                                    "name": gully_name,
                                }
                            )
                        else:
                            logger.error(f"Failed to create gully for chat {chat_id}")
                            results["errors"] += 1
                            results["details"].append(
                                {
                                    "action": "error",
                                    "chat_id": chat_id,
                                    "error": "Failed to create gully",
                                }
                            )
                            continue

                    # Set the group owner as admin
                    owner_result = await GullyService.set_group_owner_as_admin(
                        chat_id, gully["id"], bot
                    )

                    if owner_result["success"]:
                        logger.info(
                            f"Set group owner as admin for gully {gully['id']} (chat {chat_id})"
                        )
                        results["admins_set"] += 1
                        results["details"].append(
                            {
                                "action": "set_admin",
                                "chat_id": chat_id,
                                "gully_id": gully["id"],
                                "owner_id": (
                                    owner_result["owner"].id
                                    if owner_result["owner"]
                                    else None
                                ),
                            }
                        )
                    else:
                        logger.warning(
                            f"Failed to set group owner as admin for chat {chat_id}: {owner_result['error']}"
                        )
                        results["errors"] += 1
                        results["details"].append(
                            {
                                "action": "error",
                                "chat_id": chat_id,
                                "error": f"Failed to set admin: {owner_result['error']}",
                            }
                        )

                except Exception as e:
                    logger.error(f"Error processing group {chat_id}: {str(e)}")
                    results["errors"] += 1
                    results["details"].append(
                        {"action": "error", "chat_id": chat_id, "error": str(e)}
                    )

            logger.info(
                f"Group scan complete. Created {results['gullies_created']} gullies and set {results['admins_set']} admins."
            )
            return results

        except Exception as e:
            logger.error(f"Error scanning groups: {str(e)}")
            results["errors"] += 1
            results["details"].append({"action": "error", "error": str(e)})
            return results


# Create a singleton instance
gully_service = GullyService()
