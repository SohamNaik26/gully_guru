"""remove_models_and_modify_gully_participant

Revision ID: ab63dc35cf0a
Revises: 048cefd0161f
Create Date: 2025-03-11 12:12:57.656281

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "ab63dc35cf0a"
down_revision: Union[str, None] = "048cefd0161f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Using raw SQL to avoid model loading issues

    # 1. Remove fields from GullyParticipant
    op.execute("ALTER TABLE gully_participants DROP COLUMN IF EXISTS is_active;")
    op.execute("ALTER TABLE gully_participants DROP COLUMN IF EXISTS last_active_at;")
    op.execute(
        "ALTER TABLE gully_participants DROP COLUMN IF EXISTS registration_complete;"
    )

    # 2. Remove status column from Gully table
    op.execute("ALTER TABLE gullies DROP COLUMN IF EXISTS status;")

    # 3. Drop models from line 195-341
    # Drop Match and MatchPerformance tables
    op.execute("DROP TABLE IF EXISTS match_performances;")
    op.execute("DROP TABLE IF EXISTS matches;")

    # Drop AuctionRound and AuctionBid tables
    op.execute("DROP TABLE IF EXISTS auction_bids;")
    op.execute("DROP TABLE IF EXISTS auction_rounds;")

    # Drop TransferWindow, TransferListing, and TransferBid tables
    op.execute("DROP TABLE IF EXISTS transfer_bids;")
    op.execute("DROP TABLE IF EXISTS transfer_listings;")
    op.execute("DROP TABLE IF EXISTS transfer_windows;")

    # 4. Drop AdminPermission table
    op.execute("DROP TABLE IF EXISTS admin_permissions;")


def downgrade() -> None:
    # Using raw SQL for downgrade as well

    # 1. Add back fields to GullyParticipant
    op.execute(
        """
        ALTER TABLE gully_participants 
        ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT FALSE,
        ADD COLUMN IF NOT EXISTS last_active_at TIMESTAMP WITH TIME ZONE,
        ADD COLUMN IF NOT EXISTS registration_complete BOOLEAN DEFAULT FALSE;
    """
    )

    # 2. Add back status column to Gully table
    op.execute(
        """
        ALTER TABLE gullies
        ADD COLUMN IF NOT EXISTS status VARCHAR DEFAULT 'pending' NOT NULL;
    """
    )

    # 3. Recreate models from line 195-341
    # Note: This is a simplified recreation that may not include all constraints
    # For a full restoration, a database backup should be used

    # Recreate Match table
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS matches (
            id SERIAL PRIMARY KEY,
            date VARCHAR NOT NULL,
            venue VARCHAR NOT NULL,
            team1 VARCHAR NOT NULL,
            team2 VARCHAR NOT NULL,
            team1_score VARCHAR,
            team2_score VARCHAR,
            match_winner VARCHAR,
            player_of_the_match VARCHAR,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );
    """
    )

    # Recreate MatchPerformance table
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS match_performances (
            id SERIAL PRIMARY KEY,
            match_id INTEGER NOT NULL REFERENCES matches(id),
            player_id INTEGER NOT NULL REFERENCES players(id),
            runs INTEGER NOT NULL DEFAULT 0,
            balls_faced INTEGER NOT NULL DEFAULT 0,
            fours INTEGER NOT NULL DEFAULT 0,
            sixes INTEGER NOT NULL DEFAULT 0,
            wickets INTEGER NOT NULL DEFAULT 0,
            overs_bowled FLOAT NOT NULL DEFAULT 0.0,
            runs_conceded INTEGER NOT NULL DEFAULT 0,
            economy FLOAT NOT NULL DEFAULT 0.0,
            catches INTEGER NOT NULL DEFAULT 0,
            stumpings INTEGER NOT NULL DEFAULT 0,
            run_outs INTEGER NOT NULL DEFAULT 0,
            fantasy_points FLOAT NOT NULL DEFAULT 0.0,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );
    """
    )

    # Recreate AuctionRound table
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS auction_rounds (
            id SERIAL PRIMARY KEY,
            round_number INTEGER NOT NULL UNIQUE,
            start_time VARCHAR NOT NULL,
            end_time VARCHAR NOT NULL,
            status VARCHAR NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS ix_auction_rounds_round_number ON auction_rounds (round_number);
    """
    )

    # Recreate AuctionBid table
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS auction_bids (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            player_id INTEGER NOT NULL REFERENCES players(id),
            auction_round_id INTEGER NOT NULL REFERENCES auction_rounds(id),
            bid_amount NUMERIC NOT NULL,
            status VARCHAR NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );
    """
    )

    # Recreate TransferWindow table
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS transfer_windows (
            id SERIAL PRIMARY KEY,
            start_time VARCHAR NOT NULL,
            end_time VARCHAR NOT NULL,
            status VARCHAR NOT NULL DEFAULT 'pending',
            gully_id INTEGER NOT NULL REFERENCES gullies(id),
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );
    """
    )

    # Recreate TransferListing table
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS transfer_listings (
            id SERIAL PRIMARY KEY,
            seller_id INTEGER NOT NULL REFERENCES users(id),
            player_id INTEGER NOT NULL REFERENCES players(id),
            transfer_window_id INTEGER NOT NULL REFERENCES transfer_windows(id),
            asking_price NUMERIC NOT NULL,
            status VARCHAR NOT NULL DEFAULT 'active',
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );
    """
    )

    # Recreate TransferBid table
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS transfer_bids (
            id SERIAL PRIMARY KEY,
            bidder_id INTEGER NOT NULL REFERENCES users(id),
            listing_id INTEGER NOT NULL REFERENCES transfer_listings(id),
            bid_amount NUMERIC NOT NULL,
            status VARCHAR NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );
    """
    )

    # Recreate AdminPermission table
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS admin_permissions (
            id SERIAL PRIMARY KEY,
            gully_id INTEGER NOT NULL REFERENCES gullies(id),
            user_id INTEGER NOT NULL REFERENCES users(id),
            permission_type VARCHAR NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );
    """
    )
