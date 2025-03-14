#!/usr/bin/env python3
"""
Test script for the GullyGuru API client.
"""

import asyncio
import logging
import sys
import os
from src.bot.api_client.base import BaseApiClient

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def test_api():
    """Test the API client."""
    logger.info("Starting API client test")

    # Initialize client
    client = BaseApiClient()
    logger.info(f"Initialized client with base URL: {client.base_url}")

    try:
        # Test health endpoint
        logger.info("Testing health endpoint...")
        health = await client.get("/api/health")
        logger.info(f"Health response: {health}")

        # Test gullies endpoint
        logger.info("Testing gullies endpoint...")
        gullies = await client.get("/api/gullies/")
        logger.info(f"Found {len(gullies) if isinstance(gullies, list) else 0} gullies")

        # Test gullies with telegram_group_id
        test_group_id = -1002444881555  # Example group ID
        logger.info(
            f"Testing gullies endpoint with telegram_group_id {test_group_id}..."
        )
        gully = await client.get(
            "/api/gullies/", params={"telegram_group_id": test_group_id}
        )
        logger.info(f"Gully response: {gully}")

        # Test participants endpoint
        logger.info("Testing participants endpoint...")
        participants = await client.get("/api/participants/")
        logger.info(
            f"Found {len(participants) if isinstance(participants, list) else 0} participants"
        )

    except Exception as e:
        logger.error(f"Error during API test: {e}")
    finally:
        # Close client
        await client.close()
        logger.info("API client test completed")


if __name__ == "__main__":
    asyncio.run(test_api())
