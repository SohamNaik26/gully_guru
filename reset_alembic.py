"""
Script to reset the Alembic migrations.
This is a brute force approach to resolve Alembic migration issues.
"""

import asyncio
import os
from sqlalchemy import text
from src.db.session import async_engine


async def reset_alembic():
    """Reset the Alembic migrations."""
    print("Resetting Alembic migrations...")

    # 1. Clear the alembic_version table
    async with async_engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version;"))
        await conn.execute(
            text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL);")
        )

    # 2. Remove all migration files
    versions_dir = os.path.join("alembic", "versions")
    if os.path.exists(versions_dir):
        for file in os.listdir(versions_dir):
            if file.endswith(".py") and not file.startswith("__"):
                os.remove(os.path.join(versions_dir, file))

    print("Successfully reset Alembic migrations.")
    print("You can now create a new initial migration with:")
    print('pipenv run alembic revision --autogenerate -m "initial"')


if __name__ == "__main__":
    asyncio.run(reset_alembic())
