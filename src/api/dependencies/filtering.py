"""
Filtering dependencies for the GullyGuru API.
This module provides utilities for filtering database queries.
"""

from typing import Dict, Any, Type
from sqlalchemy import and_, or_, Column
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.sql.expression import BinaryExpression


def apply_filters(query, model: Type[DeclarativeMeta], filters: Dict[str, Any]):
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
            if not hasattr(model, field):
                continue  # Skip fields that don't exist on the model
                
            model_field = getattr(model, field)
            
            if isinstance(value, list):
                filter_conditions.append(model_field.in_(value))
            else:
                filter_conditions.append(model_field == value)

    if filter_conditions:
        query = query.where(and_(*filter_conditions))

    return query


def apply_advanced_filters(query, model: Type[DeclarativeMeta], advanced_filters: Dict[str, Any]):
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
    range_filters = {
        "min_base_price": ("base_price", ">="),
        "max_base_price": ("base_price", "<="),
        "min_created_at": ("created_at", ">="),
        "max_created_at": ("created_at", "<="),
    }
    
    for filter_name, (field_name, operator) in range_filters.items():
        if filter_name in advanced_filters and advanced_filters[filter_name] is not None:
            if hasattr(model, field_name):
                model_field = getattr(model, field_name)
                value = advanced_filters[filter_name]
                
                if operator == ">=":
                    query = query.where(model_field >= value)
                elif operator == "<=":
                    query = query.where(model_field <= value)

    # Handle search term (search across multiple fields)
    if "search_term" in advanced_filters and advanced_filters["search_term"]:
        search_term = f"%{advanced_filters['search_term']}%"
        search_conditions = []

        # Add searchable fields here
        searchable_fields = ["name", "team", "description", "username", "full_name"]
        for field in searchable_fields:
            if hasattr(model, field):
                model_field = getattr(model, field)
                if hasattr(model_field, "ilike"):  # Check if the field supports ilike
                    search_conditions.append(model_field.ilike(search_term))

        if search_conditions:
            query = query.where(or_(*search_conditions))

    return query


def create_filter_expression(
    model: Type[DeclarativeMeta], 
    field_name: str, 
    value: Any, 
    operator: str = "eq"
) -> BinaryExpression:
    """
    Create a filter expression for a field.
    
    Args:
        model: The model class
        field_name: Name of the field to filter on
        value: Value to filter by
        operator: Operator to use (eq, ne, gt, lt, ge, le, like, ilike, in)
        
    Returns:
        SQLAlchemy binary expression
        
    Raises:
        ValueError: If field doesn't exist or operator is invalid
    """
    if not hasattr(model, field_name):
        raise ValueError(f"Field {field_name} does not exist on model {model.__name__}")
        
    field = getattr(model, field_name)
    
    operators = {
        "eq": lambda f, v: f == v,
        "ne": lambda f, v: f != v,
        "gt": lambda f, v: f > v,
        "lt": lambda f, v: f < v,
        "ge": lambda f, v: f >= v,
        "le": lambda f, v: f <= v,
        "like": lambda f, v: f.like(f"%{v}%"),
        "ilike": lambda f, v: f.ilike(f"%{v}%"),
        "in": lambda f, v: f.in_(v if isinstance(v, list) else [v]),
    }
    
    if operator not in operators:
        raise ValueError(f"Invalid operator: {operator}")
        
    return operators[operator](field, value)
