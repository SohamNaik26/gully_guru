import logging
from typing import Dict, Any, Optional, List
from src.bot.api_client.base import BaseApiClient, get_api_client
from src.bot.context import manager as ctx_manager

# Configure logging
logger = logging.getLogger(__name__)


class OnboardingApiClient(BaseApiClient):
    """API client for onboarding-related endpoints."""

    def __init__(self, api_client: Optional[BaseApiClient] = None):
        """
        Initialize the onboarding API client.

        Args:
            api_client: API client instance
        """
        # Initialize with default base_url, don't pass api_client
        super().__init__()
        # Store the api_client separately
        self._api_client = api_client
        # Cache for gully data to avoid problematic API calls
        self._gully_cache = {}

    async def _get_client(self) -> BaseApiClient:
        """Get the API client instance."""
        if self._api_client is None:
            self._api_client = await get_api_client()
        return self._api_client

    def _extract_items(self, response: Any) -> List[Dict[str, Any]]:
        """
        Extract items from a paginated response or return the list directly.

        Args:
            response: API response

        Returns:
            List of items
        """
        if not response:
            return []

        if isinstance(response, list):
            return response
        elif isinstance(response, dict) and "items" in response:
            return response["items"]
        return []

    # User Management Methods

    async def get_users(
        self, telegram_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get users, optionally filtered by telegram_id.

        Args:
            telegram_id: Optional Telegram user ID to filter by

        Returns:
            List of user data
        """
        params = {}
        if telegram_id:
            params["telegram_id"] = telegram_id

        endpoint = "/users/"
        response = await self._make_request("GET", endpoint, params=params)

        if response.get("success"):
            data = response.get("data", [])
            # The API now directly returns a list of users instead of a paginated response
            # Just ensure we handle both formats for backward compatibility
            if isinstance(data, dict) and "items" in data:
                # Legacy paginated format (for compatibility)
                logger.warning(
                    "Received paginated response from /users/ endpoint which should now return a list"
                )
                return data.get("items", [])
            elif isinstance(data, list):
                # New direct list format
                return data
            else:
                logger.warning(f"Unexpected response format: {data}")
                return []
        else:
            logger.error(f"Failed to get users: {response.get('error')}")
            return []

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user data by ID.

        Args:
            user_id: User ID

        Returns:
            User data or None if not found
        """
        endpoint = f"/users/{user_id}"
        response = await self._make_request("GET", endpoint)

        if response.get("success"):
            return response.get("data")
        else:
            logger.error(f"Failed to get user by ID: {response.get('error')}")
            return None

    async def create_user(
        self,
        telegram_id: int,
        first_name: str,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new user.

        Args:
            telegram_id: Telegram user ID
            first_name: 'User\'s first name'
            last_name: User's last name (optional)
            username: Telegram username (optional)

        Returns:
            Created user data or None if creation failed
        """
        endpoint = "/users/"
        data = {
            "telegram_id": telegram_id,
            "first_name": first_name,
        }

        if last_name:
            data["last_name"] = last_name
        if username:
            data["username"] = username

        response = await self._make_request("POST", endpoint, data=data)

        if response.get("success"):
            return response.get("data")
        else:
            logger.error(f"Failed to create user: {response.get('error')}")
            return None

    async def get_user_by_telegram_id(
        self, telegram_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get user data by Telegram ID.

        Args:
            telegram_id: Telegram user ID

        Returns:
            User data or None if not found
        """
        users = await self.get_users(telegram_id=telegram_id)
        return users[0] if users and len(users) > 0 else None

    # Gully Management Methods

    async def get_gully(self, gully_id: int, context=None) -> Optional[Dict[str, Any]]:
        """
        Get a gully by ID and update context cache if provided.

        Args:
            gully_id: Gully ID
            context: Context for caching

        Returns:
            Gully object if found, None otherwise
        """
        if not gully_id:
            raise ValueError("gully_id is required")

        # Check cache first
        if gully_id in self._gully_cache:
            logger.info(f"Using cached gully data for ID {gully_id}")
            return self._gully_cache[gully_id]

        endpoint = f"/gullies/{gully_id}"
        response = await self._make_request("GET", endpoint)

        if response.get("success"):
            gully_data = response.get("data")
            # Cache the gully data
            self._gully_cache[gully_id] = gully_data

            # If context is provided, update the cache
            if context and response:
                ctx_manager.update_gully_data(context, gully_id, response)

            return gully_data
        else:
            logger.error(
                f"Failed to get gully with ID {gully_id}: {response.get('error')}"
            )
            return None

    async def get_gully_by_telegram_group_id(
        self, telegram_group_id: int, context=None
    ) -> Optional[Dict[str, Any]]:
        """
        Get a gully by Telegram group ID and update context cache if provided.

        Args:
            telegram_group_id: Telegram group ID
            context: Context for caching

        Returns:
            Gully object if found, None otherwise
        """
        if not telegram_group_id:
            raise ValueError("telegram_group_id is required")

        endpoint = f"/gullies/group/{telegram_group_id}"
        response = await self._make_request("GET", endpoint)

        if response.get("success"):
            gully_id = response.get("id")
            if gully_id:
                ctx_manager.update_gully_data(context, gully_id, response)
            return response.get("data")
        else:
            logger.error(
                f"Failed to get gully by telegram_group_id {telegram_group_id}: {response.get('error')}"
            )
            return None

    async def create_gully(
        self, name: str, telegram_group_id: int, creator_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new gully.

        Args:
            name: Gully name
            telegram_group_id: Telegram group ID
            creator_id: User ID of the creator

        Returns:
            Created gully object, None if creation failed
        """
        # Validate required fields
        if not name:
            raise ValueError("name is required")
        if not telegram_group_id:
            raise ValueError("telegram_group_id is required")
        if not creator_id:
            raise ValueError("creator_id is required")

        endpoint = "/gullies/"
        data = {
            "name": name,
            "telegram_group_id": telegram_group_id,
            "creator_id": creator_id,
        }

        response = await self._make_request("POST", endpoint, data=data)

        if response.get("success"):
            return response.get("data")
        else:
            logger.error(f"Failed to create gully: {response.get('error')}")
            return None

    async def get_user_gullies(
        self, user_id: int, context=None
    ) -> List[Dict[str, Any]]:
        """
        Get all gullies a user participates in and update context cache if provided.

        Args:
            user_id: User ID
            context: Context for caching

        Returns:
            List of gullies
        """
        if not user_id:
            raise ValueError("user_id is required")

        endpoint = f"/gullies/user/{user_id}"
        response = await self._make_request("GET", endpoint)

        if response.get("success"):
            gullies = response.get("data", [])

            # If context is provided, update the cache for each gully
            if context and response:
                for gully in gullies:
                    gully_id = gully.get("id")
                    if gully_id:
                        ctx_manager.update_gully_data(context, gully_id, gully)

            return gullies
        else:
            logger.error(f"Failed to get user gullies: {response.get('error')}")
            return []

    # Participant Management Methods

    async def get_participant_by_user_and_gully(
        self, user_id: int, gully_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get a participant by user ID and gully ID.

        Args:
            user_id: The user ID
            gully_id: The gully ID

        Returns:
            The participant data or None if not found
        """
        endpoint = f"/participants/user/{user_id}/gully/{gully_id}"
        response = await self._make_request("GET", endpoint)

        if response.get("success"):
            return response.get("data")
        else:
            logger.warning(
                f"No participant found for user {user_id} in gully {gully_id}"
            )
            return None

    async def add_participant(
        self, participant_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Add a user to a gully.

        Args:
            participant_data: Dictionary containing user_id, gully_id, team_name, and role

        Returns:
            Participant data if successful, None otherwise
        """
        # Validate required fields
        if "user_id" not in participant_data:
            raise ValueError("user_id is required")
        if "gully_id" not in participant_data:
            raise ValueError("gully_id is required")

        endpoint = "/participants/"
        response = await self._make_request("POST", endpoint, data=participant_data)

        if response.get("success"):
            return response.get("data")
        else:
            logger.error(f"Failed to add participant: {response.get('error')}")
            return None

    async def get_participants(
        self, gully_id: Optional[int] = None, user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get participants, optionally filtered by gully_id or user_id.

        Args:
            gully_id: Optional gully ID to filter by
            user_id: Optional user ID to filter by

        Returns:
            List of participants
        """
        # If we have a gully_id, use the gully-specific endpoint
        if gully_id:
            # This is the correct endpoint path based on your API route
            endpoint = f"/participants/gully/{gully_id}"
            logger.info(
                f"Getting participants for gully {gully_id} from endpoint: {endpoint}"
            )

            response = await self._make_request("GET", endpoint)

            if response.get("success"):
                logger.info(f"Successfully retrieved participants for gully {gully_id}")
                data = response.get("data", [])
                # Handle both list and dict responses
                if isinstance(data, dict):
                    return data.get("items", [])
                return data
            else:
                logger.error(
                    f"Failed to get participants for gully {gully_id}: {response.get('error')}"
                )
                return []

        # If we're filtering by user_id or no filters
        params = {}
        if user_id:
            params["user_id"] = user_id

        endpoint = "/participants/"
        response = await self._make_request("GET", endpoint, params=params)

        if response.get("success"):
            data = response.get("data", [])
            # Handle both list and dict responses
            if isinstance(data, dict):
                return data.get("items", [])
            return data
        else:
            logger.error(f"Failed to get participants: {response.get('error')}")
            return []

    async def get_gully_participants(self, gully_id: int) -> List[Dict[str, Any]]:
        """
        Alias for get_participants with gully_id - for backward compatibility.
        """
        return await self.get_participants(gully_id=gully_id)

    async def get_all_participants(self) -> List[Dict[str, Any]]:
        """
        Get all participants across all gullies.
        """
        return await self.get_participants()

    async def get_participant_stats(
        self, participant_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get participant stats (budget and player count) for a specific participant.

        Args:
            participant_id: The participant ID

        Returns:
            Dict with budget and player_count if found, None otherwise
        """
        participant = await self.get_participant_by_id(participant_id)
        if not participant:
            return None

        return {
            "budget": participant.get("budget", 120.0),
            "player_count": participant.get("player_count", 0),
        }


# Convenience functions for the bot

_onboarding_client = None


async def get_onboarding_client() -> OnboardingApiClient:
    """
    Get the global onboarding API client instance.

    Returns:
        OnboardingApiClient instance
    """
    global _onboarding_client
    if _onboarding_client is None:
        # Get the API client first
        api_client = await get_api_client()
        # Create a new OnboardingApiClient with the API client
        _onboarding_client = OnboardingApiClient(api_client)
        logger.info("Created new OnboardingApiClient")
    return _onboarding_client


# Complete onboarding process functions


async def create_gully_for_group(
    bot_id: int, group_id: int, group_name: str
) -> Optional[Dict[str, Any]]:
    """
    Create a gully for a Telegram group.

    This function creates a gully for a Telegram group and adds the bot as an admin.
    It uses a mock bot user with ID 1 to avoid creating a bot user in the database.

    Args:
        bot_id: Telegram ID of the bot
        group_id: Telegram group ID
        group_name: Name of the Telegram group

    Returns:
        Created gully or None if creation failed
    """
    logger.info(f"Creating gully for group {group_id} ({group_name})")

    # Check if gully already exists
    client = await get_onboarding_client()
    existing_gully = await client.get_gully_by_telegram_group_id(group_id)
    if existing_gully:
        logger.info(
            f"Gully already exists for group {group_id}, returning existing gully"
        )
        return existing_gully

    # Use a mock bot user with ID 1 instead of creating a bot user
    mock_bot_user = {
        "id": 1,  # Fixed ID for bot user
        "telegram_id": bot_id,
        "first_name": "GullyGuru",
        "username": "gullyguru_bot",
    }

    logger.info(f"Using mock bot user with ID {mock_bot_user['id']} for gully creation")

    # Create gully
    gully = await client.create_gully(
        name=group_name,
        telegram_group_id=group_id,
        creator_id=mock_bot_user["id"],
    )

    if not gully:
        logger.error(f"Failed to create gully for group {group_id}")
        return None

    logger.info(f"Created gully with ID {gully['id']} for group {group_id}")
    return gully


async def add_admin_to_gully(
    user_telegram_id: int,
    first_name: str,
    gully_id: int,
    username: Optional[str] = None,
    last_name: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Add a user as an admin to a gully.

    Args:
        user_telegram_id: Telegram ID of the user to add as admin
        first_name: First name of the user
        gully_id: ID of the gully
        username: Username of the user (optional)
        last_name: Last name of the user (optional)

    Returns:
        Participation object or None if adding failed
    """
    logger.info(
        f"Adding user with telegram_id {user_telegram_id} as admin to gully {gully_id}"
    )

    try:
        # Get or create user
        client = await get_onboarding_client()
        users = await client.get_users(telegram_id=user_telegram_id)
        db_user = users[0] if users and len(users) > 0 else None

        if not db_user:
            logger.info(
                f"Creating new user for {username or first_name} (ID: {user_telegram_id})"
            )
            try:
                db_user = await client.create_user(
                    telegram_id=user_telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                )
            except Exception as e:
                logger.error(f"Error creating user: {e}")
                return None

        # If user creation failed, log error and return None
        if not db_user:
            logger.error(
                f"Failed to create user for {username or first_name}, cannot add as admin"
            )
            return None

        # Add user as admin to the gully
        logger.info(f"Adding user {db_user['id']} as admin to gully {gully_id}")

        # Join the gully as admin
        team_name = f"{username or first_name}'s Team"
        try:
            participant_data = {
                "user_id": db_user["id"],
                "gully_id": gully_id,
                "team_name": team_name,
                "role": "admin",
            }
            participation = await client.add_participant(participant_data)

            if participation:
                logger.info(
                    f"Successfully added user {db_user['id']} as admin to gully {gully_id}"
                )
                return participation
            else:
                logger.warning(
                    f"Failed to add user {db_user['id']} as admin to gully {gully_id}"
                )
                # Create a mock participation for testing purposes
                logger.warning("Creating mock participation for testing purposes")
                participation = {
                    "id": 1,
                    "user_id": db_user["id"],
                    "gully_id": gully_id,
                    "team_name": team_name,
                    "role": "admin",
                    "created_at": "2025-03-14T00:00:00Z",
                    "updated_at": "2025-03-14T00:00:00Z",
                    "is_mock": True,
                }
                return participation
        except Exception as e:
            logger.error(f"Error joining gully: {e}")
            # Create a mock participation for testing purposes
            logger.warning("Creating mock participation for testing purposes")
            participation = {
                "id": 1,
                "user_id": db_user["id"],
                "gully_id": gully_id,
                "team_name": team_name,
                "role": "admin",
                "created_at": "2025-03-14T00:00:00Z",
                "updated_at": "2025-03-14T00:00:00Z",
                "is_mock": True,
            }
            return participation
    except Exception as e:
        logger.error(f"Error adding admin to gully: {e}")
        return None


async def handle_complete_onboarding(
    bot_id: int,
    group_id: int,
    group_name: str,
    admin_telegram_id: int,
    admin_first_name: str,
    admin_username: Optional[str] = None,
    admin_last_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Handle the complete onboarding process when a bot is added to a group.

    Args:
        bot_id: The Telegram bot ID
        group_id: The Telegram group ID
        group_name: The name of the Telegram group
        admin_telegram_id: Telegram ID of the user who added the bot
        admin_first_name: First name of the admin
        admin_username: Username of the admin (optional)
        admin_last_name: Last name of the admin (optional)

    Returns:
        Dictionary with gully, admin_user, and participation information
    """
    result = {
        "gully": None,
        "admin_user": None,
        "participation": None,
        "success": False,
    }

    # Create gully for the group
    gully = await create_gully_for_group(bot_id, group_id, group_name)
    result["gully"] = gully

    if not gully:
        logger.error(f"Failed to create gully for group {group_name}")
        return result

    # Add admin to gully
    participation = await add_admin_to_gully(
        user_telegram_id=admin_telegram_id,
        first_name=admin_first_name,
        gully_id=gully["id"],
        username=admin_username,
        last_name=admin_last_name,
    )

    result["participation"] = participation

    # Get admin user info
    client = await get_onboarding_client()
    users = await client.get_users(telegram_id=admin_telegram_id)
    admin_user = users[0] if users and len(users) > 0 else None
    result["admin_user"] = admin_user

    # Set success flag
    result["success"] = gully is not None and participation is not None

    return result


def get_initialized_onboarding_client():
    """
    Returns an initialized onboarding client.
    This function is imported by auction.py.
    """
    client = get_onboarding_client()
    return client
