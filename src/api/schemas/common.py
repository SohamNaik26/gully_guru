"""
Common schemas for the GullyGuru API.
"""

from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional, List, Any, Dict

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard API response format."""

    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Success or error message")
    data: Optional[T] = Field(None, description="Response data")
    errors: Optional[List[str]] = Field(None, description="List of error messages")
    meta: Optional[dict] = Field(None, description="Additional metadata")


class SuccessResponse(BaseModel):
    """Model for success response."""

    success: bool = Field(..., description="Success status")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")


def success_response(
    data: Any = None, message: str = "Operation successful", meta: dict = None
) -> dict:
    """
    Create a success response.

    Args:
        data: Response data
        message: Success message
        meta: Additional metadata

    Returns:
        Dictionary with success response
    """
    return {"success": True, "message": message, "data": data, "meta": meta}


def error_response(message: str = "Operation failed", errors: List[str] = None) -> dict:
    """
    Create an error response.

    Args:
        message: Error message
        errors: List of specific error messages

    Returns:
        Dictionary with error response
    """
    return {"success": False, "message": message, "errors": errors or []}
