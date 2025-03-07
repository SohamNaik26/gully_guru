#!/usr/bin/env python3
"""
Script to check if SQLModel models are properly defined and registered.

Run this script using Pipenv:
    pipenv run python scripts/check_models.py
"""

import os
import sys
import inspect
from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

# Import all models to ensure they're registered with SQLModel.metadata
import src.db.models  # noqa: F401
from src.db.models.models import TimeStampedModel

# Load environment variables
load_dotenv()


def check_models():
    """Check if all models are properly defined and registered."""
    print("Checking SQLModel models...\n")

    # Get all tables registered with SQLModel.metadata
    tables = SQLModel.metadata.tables
    print(f"Found {len(tables)} tables registered with SQLModel.metadata:")

    for table_name in sorted(tables.keys()):
        table = tables[table_name]
        primary_keys = [c.name for c in table.primary_key.columns]
        print(f"  - {table_name} (Primary keys: {', '.join(primary_keys)})")

    # Check for specific tables
    expected_tables = [
        "users",
        "players",
        "user_players",
        "player_stats",
        "matches",
        "match_performances",
        "auction_rounds",
        "auction_bids",
        "transfer_windows",
        "transfer_listings",
        "transfer_bids",
        "match_polls",
        "poll_votes",
        "gullies",
        "gully_participants",
        "api_teams",
        "api_players",
        "api_matches",
        "api_player_stats",
        "cricsheet_teams",
        "cricsheet_players",
        "cricsheet_matches",
        "cricsheet_innings",
        "cricsheet_balls",
        "kaggle_players",
        "games",
        "game_participants",
    ]

    missing_tables = [table for table in expected_tables if table not in tables]
    if missing_tables:
        print("\nWARNING: The following expected tables are missing:")
        for table in missing_tables:
            print(f"  - {table}")
    else:
        print("\nAll expected tables are registered.")

    # Check for tables without primary keys
    tables_without_pk = []
    for table_name, table in tables.items():
        if not table.primary_key:
            tables_without_pk.append(table_name)

    if tables_without_pk:
        print("\nWARNING: The following tables don't have primary keys:")
        for table_name in tables_without_pk:
            print(f"  - {table_name}")
    else:
        print("\nAll tables have primary keys defined.")

    # Check for model organization
    print("\nChecking model organization...")

    # Get all models from models.py
    from src.db.models import models

    models_py_classes = {
        name: cls
        for name, cls in inspect.getmembers(models, inspect.isclass)
        if issubclass(cls, SQLModel) and cls != SQLModel and cls != TimeStampedModel
    }

    print(f"Found {len(models_py_classes)} models defined in models.py:")
    for name in sorted(models_py_classes.keys()):
        print(f"  - {name}")

    # Check for duplicate models in other files
    duplicate_models = []

    # Check api.py
    from src.db.models import api

    api_classes = {
        name: cls
        for name, cls in inspect.getmembers(api, inspect.isclass)
        if issubclass(cls, SQLModel) and cls != SQLModel
    }

    for name, cls in api_classes.items():
        if name in models_py_classes:
            duplicate_models.append((name, "api.py", "models.py"))

    # Check cricsheet.py
    from src.db.models import cricsheet

    cricsheet_classes = {
        name: cls
        for name, cls in inspect.getmembers(cricsheet, inspect.isclass)
        if issubclass(cls, SQLModel) and cls != SQLModel
    }

    for name, cls in cricsheet_classes.items():
        if name in models_py_classes:
            duplicate_models.append((name, "cricsheet.py", "models.py"))

    # Check kaggle.py
    from src.db.models import kaggle

    kaggle_classes = {
        name: cls
        for name, cls in inspect.getmembers(kaggle, inspect.isclass)
        if issubclass(cls, SQLModel) and cls != SQLModel
    }

    for name, cls in kaggle_classes.items():
        if name in models_py_classes:
            duplicate_models.append((name, "kaggle.py", "models.py"))

    # Check game.py
    from src.db.models import game

    game_classes = {
        name: cls
        for name, cls in inspect.getmembers(game, inspect.isclass)
        if issubclass(cls, SQLModel) and cls != SQLModel
    }

    for name, cls in game_classes.items():
        if name in models_py_classes:
            duplicate_models.append((name, "game.py", "models.py"))

    # Check game_participant.py
    from src.db.models import game_participant

    game_participant_classes = {
        name: cls
        for name, cls in inspect.getmembers(game_participant, inspect.isclass)
        if issubclass(cls, SQLModel) and cls != SQLModel
    }

    for name, cls in game_participant_classes.items():
        if name in models_py_classes:
            duplicate_models.append((name, "game_participant.py", "models.py"))

    if duplicate_models:
        print("\nWARNING: Found duplicate model definitions:")
        for name, file1, file2 in duplicate_models:
            print(f"  - {name} is defined in both {file1} and {file2}")
    else:
        print("\nNo duplicate model definitions found.")


def test_database_connection():
    """Test the database connection and create tables."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set.")
        return

    print(f"\nConnecting to database: {database_url}")

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
    check_models()
    test_database_connection()
