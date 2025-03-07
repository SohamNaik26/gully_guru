#!/usr/bin/env python
"""
Test module for Kaggle integration.

This module contains tests for the Kaggle integration flow, testing each step
individually and the full integration process.
"""

import asyncio
import logging
import pytest
import pandas as pd
from decimal import Decimal

from src.integrations.kaggle import (
    fetch_kaggle_data,
    transform_kaggle_data,
    store_kaggle_data,
    sync_kaggle_to_players,
    import_kaggle_players,
    parse_price,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Mock data for testing
MOCK_KAGGLE_DATA = pd.DataFrame(
    {
        "Players": ["Virat Kohli", "Rohit Sharma", "MS Dhoni"],
        "Team": ["RCB", "MI", "CSK"],
        "Type": ["BAT", "BAT", "WK"],
        "Base": ["2 cr", "2 cr", "1.5 cr"],
        "Sold": ["17 cr", "16.5 cr", "12 cr"],
    }
)


@pytest.mark.asyncio
async def test_fetch_kaggle_data():
    """Test fetching data from Kaggle."""
    # This test will actually call the Kaggle API
    # In a real test environment, you might want to mock this
    df = await fetch_kaggle_data()
    assert df is not None
    assert len(df) > 0
    assert "Players" in df.columns


def test_transform_kaggle_data():
    """Test transforming Kaggle data."""
    # Use mock data instead of real API call
    records = transform_kaggle_data(MOCK_KAGGLE_DATA)

    # Verify records were transformed correctly
    assert len(records) == 3
    assert records[0]["name"] == "Virat Kohli"
    assert records[0]["team"] == "RCB"
    assert records[0]["player_type"] == "BAT"
    assert records[0]["base_price"] == Decimal("20")  # 2 cr = 20 million
    assert records[0]["season"] == 2025
    assert records[0]["processed"] is False


@pytest.mark.asyncio
async def test_store_kaggle_data():
    """Test storing Kaggle data."""
    # Create test records
    records = transform_kaggle_data(MOCK_KAGGLE_DATA)

    # Store records
    success = await store_kaggle_data(records)
    assert success is True


@pytest.mark.asyncio
async def test_sync_kaggle_to_players():
    """Test syncing Kaggle data to Player models."""
    # First ensure we have data to sync
    records = transform_kaggle_data(MOCK_KAGGLE_DATA)
    await store_kaggle_data(records)

    # Now sync to Player models
    stats = await sync_kaggle_to_players()
    assert "created" in stats
    assert "updated" in stats
    assert "skipped" in stats
    assert "failed" in stats


@pytest.mark.asyncio
async def test_full_integration():
    """Test the full Kaggle integration flow."""
    success = await import_kaggle_players()
    assert success is True


def test_parse_price():
    """Test the price parsing function."""
    # Test various formats
    assert parse_price("2 cr") == Decimal("20")
    assert parse_price("1.5 cr") == Decimal("15")
    assert parse_price("75 lakh") == Decimal("7.5")
    assert parse_price("Unsold") is None
    assert parse_price("-") is None
    assert parse_price("TBA") is None


# Manual test runner
async def run_tests_manually():
    """Run all tests manually without pytest."""
    logger.info("Starting manual Kaggle integration tests")

    # Test individual steps
    logger.info("=== Testing fetch_kaggle_data ===")
    df = await fetch_kaggle_data()
    if df is not None:
        logger.info(f"Successfully fetched {len(df)} records")
        logger.info(f"Sample data: {df.head(2)}")
    else:
        logger.error("Failed to fetch data")
        return

    logger.info("=== Testing transform_kaggle_data ===")
    records = transform_kaggle_data(df)
    logger.info(f"Transformed {len(records)} records")
    logger.info(f"Sample record: {records[0]}")

    logger.info("=== Testing store_kaggle_data ===")
    store_success = await store_kaggle_data(records)
    if store_success:
        logger.info("Successfully stored records")
    else:
        logger.error("Failed to store records")
        return

    logger.info("=== Testing sync_kaggle_to_players ===")
    sync_stats = await sync_kaggle_to_players()
    logger.info(f"Sync stats: {sync_stats}")
    logger.info(
        f"Sync summary: {sync_stats['created']} created, {sync_stats['updated']} updated"
    )

    logger.info("=== Testing full Kaggle integration ===")
    full_success = await import_kaggle_players()
    if full_success:
        logger.info("Full integration successful")
    else:
        logger.error("Full integration failed")

    logger.info("Completed Kaggle integration tests")


if __name__ == "__main__":
    # Run tests manually if script is executed directly
    asyncio.run(run_tests_manually())
