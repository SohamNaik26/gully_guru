"""
Script to drop and recreate the kaggle_players table with the new schema.
This is a brute force approach to resolve Alembic migration issues.
"""

import asyncio
from sqlalchemy import text
from src.db.session import async_engine
from src.db.models.kaggle import KagglePlayer
from sqlmodel import SQLModel


async def recreate_kaggle_table():
    """Drop and recreate the kaggle_players table with the new schema."""
    print("Dropping and recreating kaggle_players table...")

    async with async_engine.begin() as conn:
        # Drop the table if it exists
        await conn.execute(text("DROP TABLE IF EXISTS kaggle_players CASCADE;"))

        # Create the table with the new schema
        await conn.run_sync(
            SQLModel.metadata.create_all, tables=[KagglePlayer.__table__]
        )

        print("Successfully recreated kaggle_players table with the new schema.")


if __name__ == "__main__":
    asyncio.run(recreate_kaggle_table())
