import asyncio
import pandas as pd
import logging
import kagglehub
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from decimal import Decimal
import traceback
from sqlalchemy.sql import select
from kagglehub import KaggleDatasetAdapter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import true

from src.db.models import Player
from src.db.models.kaggle import KagglePlayer
from src.db.integration_helper import (
    push_integration_data,
    process_integration_data,
    retry_operation,
)

logger = logging.getLogger(__name__)


# Main entry point for Kaggle integration
async def import_kaggle_players() -> bool:
    """
    Import IPL players from Kaggle to the database.

    This function orchestrates the entire Kaggle integration process:
    1. Fetch data from Kaggle
    2. Transform data to match our model
    3. Store data in kaggle_players table
    4. Sync data to core Player models

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Step 1: Fetch data from Kaggle
        raw_data = await fetch_kaggle_data()
        if raw_data is None:
            return False

        # Step 2: Transform data to match our model
        player_records = transform_kaggle_data(raw_data)

        # Step 3: Store data in kaggle_players table
        import_success = await store_kaggle_data(player_records)
        if not import_success:
            return False

        # Step 4: Sync data to core Player models
        sync_stats = await sync_kaggle_to_players()

        logger.info(
            f"Kaggle integration completed: "
            f"{sync_stats['created']} players created, "
            f"{sync_stats['updated']} players updated, "
            f"{sync_stats['skipped']} players skipped, "
            f"{sync_stats['failed']} players failed"
        )

        return True

    except Exception as e:
        logger.error(f"Kaggle integration failed: {str(e)}")
        logger.error(f"Detailed error:\n{traceback.format_exc()}")
        return False


# Step 1: Fetch data from Kaggle
async def fetch_kaggle_data() -> Optional[pd.DataFrame]:
    """
    Fetch IPL 2025 player data from Kaggle.

    Returns:
        DataFrame or None: Pandas DataFrame with player data or None if failed
    """
    try:
        logger.info("Loading dataset from Kaggle...")
        # Use retry_operation to handle potential network issues
        df = await retry_operation(
            lambda: asyncio.to_thread(
                kagglehub.dataset_load,
                KaggleDatasetAdapter.PANDAS,
                "souviksamanta1053/ipl-2025-mega-auction-dataset",
                "ipl_2025_auction_players.csv",
            )
        )

        logger.info(f"Original columns: {df.columns.tolist()}")
        return df

    except Exception as e:
        logger.error(f"Failed to fetch Kaggle data: {str(e)}")
        return None


# Step 2: Transform data to match our model
def transform_kaggle_data(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Transform Kaggle data to match our model structure.

    Args:
        df: Pandas DataFrame with raw Kaggle data

    Returns:
        list: List of dictionaries ready for import
    """
    # Rename columns to match our model
    column_mapping = {
        "Players": "name",
        "Team": "team",
        "Type": "player_type",
        "Base": "base_price",
        "Sold": "sold_price",
    }
    df = df.rename(columns=column_mapping)
    logger.info(f"Final columns after mapping: {df.columns.tolist()}")

    # Get current time with timezone
    now = datetime.now(timezone.utc)
    current_year = now.year

    # Process data and create records
    import_records = []
    for _, row in df.iterrows():
        import_records.append(
            {
                "name": row.get("name", "Unknown"),
                "team": row.get("team", "TBA"),
                "player_type": row.get("player_type", "BAT"),
                "base_price": parse_price(row.get("base_price")),
                "sold_price": parse_price(row.get("sold_price")),
                "season": current_year,  # Use current year as season
                "processed": False,
                "created_at": now,
                "updated_at": now,
            }
        )

    return import_records


# Step 3: Store data in kaggle_players table
async def store_kaggle_data(records: List[Dict[str, Any]]) -> bool:
    """
    Store Kaggle data in the kaggle_players table.

    Uses the integration helper to push data to the database.

    Args:
        records: List of dictionaries with player data

    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Storing {len(records)} Kaggle player records")

    # Use integration helper to push data to database
    return await push_integration_data(
        KagglePlayer,
        records,
        strategy="replace",  # Replace existing records
        create_table=True,  # Create table if it doesn't exist
    )


# Step 4: Sync data to core Player models
async def sync_kaggle_to_players() -> Dict[str, int]:
    """
    Sync Kaggle players to core Player models.

    Uses the integration helper to process data.

    Returns:
        dict: Statistics about the sync process
    """
    logger.info("Syncing Kaggle players to core Player models")

    # Use integration helper to process data with a condition to process all records
    # regardless of the processed flag
    return await process_integration_data(
        KagglePlayer,
        Player,
        kaggle_to_player_processor,
        condition=true(),  # Process all records regardless of processed flag
    )


# Helper function to process a single Kaggle player record
async def kaggle_to_player_processor(
    kaggle_record: KagglePlayer, session: AsyncSession
) -> Optional[Player]:
    """
    Process a Kaggle player record to create or update a core Player record.

    Data cleaning rules:
    1. Skip players with no team (team is None, empty, "-", or "TBA")
    2. Set base_price to 2cr (2.0) if it's null
    3. Ensure players with a team have both base_price and sold_price

    Args:
        kaggle_record: The Kaggle player record
        session: SQLAlchemy session

    Returns:
        Player: The created or updated Player record, or None if skipped
    """
    try:
        # Skip records without a name
        if not kaggle_record.name or kaggle_record.name == "Unknown":
            logger.info(f"Skipping record with missing name: {kaggle_record.id}")
            # Mark as processed even though we're skipping it
            kaggle_record.processed = True
            session.add(kaggle_record)
            return None

        # Skip players with no team or invalid team values
        if not kaggle_record.team or kaggle_record.team in ["-", "TBA", ""]:
            logger.info(
                f"Skipping player with no valid team: {kaggle_record.name} (team: {kaggle_record.team})"
            )
            # Mark as processed even though we're skipping it
            kaggle_record.processed = True
            session.add(kaggle_record)
            return None

        # Set default base price if null
        base_price = kaggle_record.base_price
        if base_price is None:
            base_price = Decimal("2.0")  # 2cr default base price

        # Ensure sold price exists
        sold_price = kaggle_record.sold_price
        if sold_price is None:
            # If no sold price, use base price as fallback
            sold_price = base_price

        # Check if player already exists
        stmt = select(Player).where(Player.name == kaggle_record.name)
        if kaggle_record.season:
            stmt = stmt.where(Player.season == kaggle_record.season)

        result = await session.execute(stmt)
        player = result.scalar_one_or_none()

        if player:
            # Check if the existing player has a valid team
            # If the existing player has an invalid team, we should delete it and create a new one
            if player.team in ["-", "TBA", ""] or player.team is None:
                logger.info(
                    f"Deleting player with invalid team: {player.name} (team: {player.team})"
                )
                await session.delete(player)
                await session.flush()

                # Create new player
                new_player = Player(
                    name=kaggle_record.name,
                    team=kaggle_record.team,
                    player_type=kaggle_record.player_type
                    or "BAT",  # Default to BAT if not specified
                    base_price=base_price,
                    sold_price=sold_price,
                    season=kaggle_record.season or datetime.now(timezone.utc).year,
                )
                session.add(new_player)

                # Mark the record as processed
                kaggle_record.processed = True
                session.add(kaggle_record)

                return new_player
            else:
                # Update existing player
                player.team = kaggle_record.team
                player.player_type = (
                    kaggle_record.player_type or "BAT"
                )  # Default to BAT if not specified
                player.base_price = base_price
                player.sold_price = sold_price
                player.updated_at = datetime.now(timezone.utc)
                session.add(player)

                # Mark the record as processed
                kaggle_record.processed = True
                session.add(kaggle_record)

                return player
        else:
            # Create new player
            new_player = Player(
                name=kaggle_record.name,
                team=kaggle_record.team,
                player_type=kaggle_record.player_type
                or "BAT",  # Default to BAT if not specified
                base_price=base_price,
                sold_price=sold_price,
                season=kaggle_record.season or datetime.now(timezone.utc).year,
            )
            session.add(new_player)

            # Mark the record as processed
            kaggle_record.processed = True
            session.add(kaggle_record)

            return new_player

    except Exception as e:
        logger.error(f"Error processing Kaggle record: {str(e)}")
        return None


# Helper function to parse price values
def parse_price(price_value: Any) -> Optional[Decimal]:
    """
    Parse price values from various formats to Decimal.

    Args:
        price_value: Price value in various formats

    Returns:
        Decimal or None: Parsed price value
    """
    if pd.isna(price_value) or price_value in ["-", "TBA", "Unsold"]:
        return None

    try:
        # Remove currency symbols and whitespace
        clean_value = str(price_value).replace("₹", "").strip()

        # Handle crore/lakh notation if present
        if "cr" in clean_value.lower():
            # Convert crore to regular number (1 crore = 10 million)
            value = clean_value.lower().replace("cr", "").strip()
            return Decimal(value) * 10
        elif "lakh" in clean_value.lower():
            # Convert lakh to regular number (1 lakh = 100,000)
            value = clean_value.lower().replace("lakh", "").strip()
            return Decimal(value) / 10  # Store in crores (1 crore = 100 lakhs)

        return Decimal(clean_value)
    except Exception as e:
        logger.warning(f"Could not parse price value: {price_value}. Error: {str(e)}")
        return None


# For direct execution
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run the import
    asyncio.run(import_kaggle_players())
