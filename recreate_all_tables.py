"""
Script to drop all tables and recreate them from scratch.
This is a brute force approach to resolve database schema issues.
"""

import asyncio
from sqlalchemy import text
from sqlmodel import SQLModel
from src.db.session import async_engine

# Import all models to ensure they're registered with SQLModel metadata
# We need to import these even if they're not directly used in this file
# pylint: disable=unused-import
from src.db.models import *


async def recreate_all_tables():
    """Drop all tables and recreate them from scratch."""
    print("Dropping and recreating all tables...")

    async with async_engine.begin() as conn:
        # Drop all tables
        await conn.execute(text("DROP SCHEMA public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))

        # Recreate all tables
        await conn.run_sync(SQLModel.metadata.create_all)

        # Reset the alembic_version table
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version;"))
        await conn.execute(
            text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL);")
        )

        print("Successfully recreated all tables from scratch.")


if __name__ == "__main__":
    asyncio.run(recreate_all_tables())
