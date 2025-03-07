"""
Base utilities and validation functions for models.
"""

from typing import List


def validate_non_negative(value: float) -> float:
    """Validate that a value is non-negative."""
    if value < 0:
        raise ValueError("Value cannot be negative")
    return value


def validate_status(value: str, valid_statuses: List[str]) -> str:
    """Validate that a status is one of the valid options."""
    if value not in valid_statuses:
        raise ValueError(f"Status must be one of {valid_statuses}")
    return value
