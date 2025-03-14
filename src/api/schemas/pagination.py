"""
Pagination schemas for the GullyGuru API.
This module provides schemas for paginated responses.
"""

from typing import Generic, TypeVar, List
from pydantic.generics import GenericModel

T = TypeVar("T")


class PaginationParams:
    """Parameters for pagination."""

    def __init__(self, limit: int = 10, offset: int = 0):
        self.limit = min(limit, 100)  # Maximum 100 items per page
        self.offset = max(offset, 0)  # Minimum offset 0

    @property
    def skip(self) -> int:
        """Alias for offset to maintain compatibility with older code."""
        return self.offset

    @property
    def page(self) -> int:
        """Calculate the current page number."""
        return (self.offset // self.limit) + 1 if self.limit > 0 else 1

    @property
    def size(self) -> int:
        """Alias for limit to maintain compatibility with older code."""
        return self.limit


class PaginatedResponse(GenericModel, Generic[T]):
    """
    Paginated response schema.

    Attributes:
        items: List of items
        total: Total number of items
        limit: Maximum number of items per page
        offset: Number of items to skip
    """

    items: List[T]
    total: int
    limit: int
    offset: int

    @property
    def has_more(self) -> bool:
        """Check if there are more items available."""
        return self.total > (self.offset + self.limit)
