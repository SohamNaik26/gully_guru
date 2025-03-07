from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext

from src.utils.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_token(user_id: int) -> str:
    """
    Create a JWT token for a user.

    Args:
        user_id: User ID to encode in the token

    Returns:
        str: JWT token
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": str(user_id), "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def verify_token(token: str) -> Optional[int]:
    """
    Verify a JWT token and return the user ID.

    Args:
        token: JWT token to verify

    Returns:
        Optional[int]: User ID if token is valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = int(payload.get("sub"))
        return user_id
    except (jwt.PyJWTError, ValueError):
        return None
