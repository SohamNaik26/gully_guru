import os
import asyncio
from sqlmodel import create_engine
from databases import Database
from sqlmodel import SQLModel


async def check_database_connection():
    """
    check_database_connection

    Checks the database connection by attempting to connect to the database,
    executing a simple query to ensure the connection is active, and then disconnecting.

    Returns:
        bool: True if the database connection is successful, False otherwise.
    """
    try:
        await database.connect()
        # Optionally, perform a simple query to ensure connection is indeed working
        query = "SELECT 1"
        await database.execute(query)
        await database.disconnect()
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(check_database_connection())
