from typing import Optional

# Simple authentication module for development
# No security features, just for testing


def create_token(user_id: int) -> str:
    """
    Create a simple token for a user (bypassing JWT).

    Args:
        user_id: User ID to encode in the token

    Returns:
        str: Simple token
    """
    # Just return the user ID as a string (no security, just for development)
    return f"user_{user_id}"


def verify_token(token: str) -> Optional[int]:
    """
    Verify a simple token and return the user ID (bypassing JWT).

    Args:
        token: Simple token to verify

    Returns:
        Optional[int]: User ID if token is valid, None otherwise
    """
    try:
        # Simple token format: "user_123"
        if token and token.startswith("user_"):
            user_id = int(token.split("_")[1])
            return user_id
        return None
    except ValueError:
        return None
