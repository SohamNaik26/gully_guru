#!/usr/bin/env python3
"""
Test script to verify SQLModel models and Alembic migrations.

Run this script using Pipenv:
    pipenv run python scripts/test_models.py
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

# Import all required modules
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

# Import all models to ensure they're registered with SQLModel.metadata
# This import is used for its side effect of registering models with SQLModel.metadata
import src.db.models  # noqa: F401

# Load environment variables
load_dotenv()


def test_models():
    """Test that all models are properly registered with SQLModel.metadata."""
    # Get all tables registered with SQLModel.metadata
    tables = SQLModel.metadata.tables
    print(f"Found {len(tables)} tables registered with SQLModel.metadata:")

    for table_name in sorted(tables.keys()):
        print(f"  - {table_name}")

    # Check for specific tables to ensure key models are registered
    expected_tables = [
        "users",
        "players",
        "user_player_links",
        "auctions",  # Updated from auction_rounds based on your model
        "auction_bids",
    ]

    missing_tables = [table for table in expected_tables if table not in tables]
    if missing_tables:
        print("\nWARNING: The following expected tables are missing:")
        for table in missing_tables:
            print(f"  - {table}")
    else:
        print("\nAll expected tables are registered.")


def test_database_connection():
    """Test the database connection and create tables."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set.")
        return

    print(f"Connecting to database: {database_url}")

    # Create engine
    engine = create_engine(database_url)

    try:
        # Create all tables
        SQLModel.metadata.create_all(engine)
        print("Successfully created all tables.")

        # Test a simple query
        with Session(engine) as session:
            # Try to query one of the tables
            result = session.execute("SELECT 1").fetchone()
            print(f"Database connection test: {result}")
    except Exception as e:
        print(f"ERROR: Failed to connect to database: {str(e)}")


if __name__ == "__main__":
    print("Testing SQLModel models and database connection...\n")
    test_models()
    print("\n" + "-" * 50 + "\n")
    test_database_connection()


# Usage examples:
"""
# Run this script with Pipenv:
pipenv run python scripts/test_models.py

# Run Alembic migrations with Pipenv:
pipenv run alembic revision --autogenerate -m "Initial migration"
pipenv run alembic upgrade head

# Run the application with Pipenv:
pipenv run uvicorn src.main:app --reload
"""
