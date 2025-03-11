#!/usr/bin/env python
"""
Script to run the migration to remove models and modify GullyParticipant.
"""
import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database connection details from environment variables
DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    print("Error: DATABASE_URL environment variable not found.")
    sys.exit(1)

# SQL statements for migration
MIGRATION_SQL = """
-- Migration script to remove models and modify GullyParticipant

-- 1. Remove fields from GullyParticipant
ALTER TABLE gully_participants DROP COLUMN IF EXISTS is_active;
ALTER TABLE gully_participants DROP COLUMN IF EXISTS last_active_at;
ALTER TABLE gully_participants DROP COLUMN IF EXISTS registration_complete;

-- 2. Remove status column from Gully
ALTER TABLE gullies DROP COLUMN IF EXISTS status;

-- 3. Drop models from line 195-341
-- Drop Match and MatchPerformance tables
DROP TABLE IF EXISTS match_performances;
DROP TABLE IF EXISTS matches;

-- Drop AuctionRound and AuctionBid tables
DROP TABLE IF EXISTS auction_bids;
DROP TABLE IF EXISTS auction_rounds;

-- Drop TransferWindow, TransferListing, and TransferBid tables
DROP TABLE IF EXISTS transfer_bids;
DROP TABLE IF EXISTS transfer_listings;
DROP TABLE IF EXISTS transfer_windows;

-- 4. Drop AdminPermission table
DROP TABLE IF EXISTS admin_permissions;
"""


def run_migration():
    """Execute the migration SQL statements."""
    try:
        # Connect to the database
        print(f"Connecting to database: {DB_URL}")
        conn = psycopg2.connect(DB_URL)
        conn.autocommit = True

        # Create a cursor
        cursor = conn.cursor()

        # Execute the migration SQL
        print("Executing migration SQL...")
        cursor.execute(MIGRATION_SQL)

        # Close the cursor and connection
        cursor.close()
        conn.close()

        print("Migration completed successfully!")
        return True
    except Exception as e:
        print(f"Error executing migration: {e}")
        return False


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
