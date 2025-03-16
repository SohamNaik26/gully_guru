"""
Pagination schemas for the GullyGuru API.
This module provides schemas for paginated responses.
"""

from typing import Generic, TypeVar, List, Dict, Any
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Parameters for pagination."""

    limit: int = Field(10, ge=1, le=100, description="Number of items per page")
    offset: int = Field(0, ge=0, description="Number of items to skip")

    @property
    def page(self) -> int:
        """Calculate the current page number."""
        return (self.offset // self.limit) + 1 if self.limit > 0 else 1

    @property
    def size(self) -> int:
        """Get the page size."""
        return self.limit


class PaginatedResponse(BaseModel, Generic[T]):
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
    def page(self) -> int:
        """Calculate the current page number."""
        return (self.offset // self.limit) + 1 if self.limit > 0 else 1

    @property
    def pages(self) -> int:
        """Calculate the total number of pages."""
        return (self.total + self.limit - 1) // self.limit if self.limit > 0 else 1

    @property
    def has_more(self) -> bool:
        """Check if there are more items available."""
        return self.total > (self.offset + self.limit)
