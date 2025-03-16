"""
Pagination dependencies for the GullyGuru API.
"""

from fastapi import Query
from src.api.schemas.pagination import PaginationParams


async def pagination_params(
    limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
) -> PaginationParams:
    """
    Dependency for pagination parameters.

    Args:
        limit: Maximum number of items to return (default: 10, max: 100)
        offset: Number of items to skip (default: 0)

    Returns:
        PaginationParams object with validated limit and offset
    """
    return PaginationParams(limit=limit, offset=offset)
