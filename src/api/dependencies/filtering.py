from typing import Dict, Any
from sqlalchemy import and_, or_


def apply_filters(query, model, filters: Dict[str, Any]):
    """
    Apply filters to a SQLModel query.

    Args:
        query: The SQLModel query to filter
        model: The model class being queried
        filters: Dictionary of field names and values to filter by

    Returns:
        Filtered query
    """
    if not filters:
        return query

    filter_conditions = []
    for field, value in filters.items():
        if value is not None:
            if isinstance(value, list):
                filter_conditions.append(getattr(model, field).in_(value))
            else:
                filter_conditions.append(getattr(model, field) == value)

    if filter_conditions:
        query = query.where(and_(*filter_conditions))

    return query


def apply_advanced_filters(query, model, advanced_filters: Dict[str, Any]):
    """
    Apply advanced filters to a SQLModel query.

    Args:
        query: The SQLModel query to filter
        model: The model class being queried
        advanced_filters: Dictionary of advanced filter conditions

    Returns:
        Filtered query

    Examples:
        - min_base_price: Filter by minimum base price
        - max_base_price: Filter by maximum base price
        - search_term: Search across multiple fields
    """
    if not advanced_filters:
        return query

    # Handle range filters
    if (
        "min_base_price" in advanced_filters
        and advanced_filters["min_base_price"] is not None
    ):
        query = query.where(
            getattr(model, "base_price") >= advanced_filters["min_base_price"]
        )

    if (
        "max_base_price" in advanced_filters
        and advanced_filters["max_base_price"] is not None
    ):
        query = query.where(
            getattr(model, "base_price") <= advanced_filters["max_base_price"]
        )

    # Handle search term (search across multiple fields)
    if "search_term" in advanced_filters and advanced_filters["search_term"]:
        search_term = f"%{advanced_filters['search_term']}%"
        search_conditions = []

        # Add searchable fields here
        searchable_fields = ["name", "team"]
        for field in searchable_fields:
            if hasattr(model, field):
                search_conditions.append(getattr(model, field).ilike(search_term))

        if search_conditions:
            query = query.where(or_(*search_conditions))

    return query
