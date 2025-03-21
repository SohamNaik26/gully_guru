"""Update auction_status constraint to include 'rejected'

Revision ID: update_auction_status_constraint
Revises: edc2c02b414a
Create Date: 2025-03-19 21:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "update_auction_status_constraint"
down_revision: Union[str, None] = "edc2c02b414a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the existing constraint
    op.execute("ALTER TABLE auction_queue DROP CONSTRAINT ck_auction_status")

    # Create a new constraint that includes 'rejected'
    op.execute(
        """
        ALTER TABLE auction_queue ADD CONSTRAINT ck_auction_status 
        CHECK (status IN ('pending', 'bidding', 'completed', 'rejected'))
    """
    )


def downgrade() -> None:
    # Drop the modified constraint
    op.execute("ALTER TABLE auction_queue DROP CONSTRAINT ck_auction_status")

    # Recreate the original constraint
    op.execute(
        """
        ALTER TABLE auction_queue ADD CONSTRAINT ck_auction_status 
        CHECK (status IN ('pending', 'bidding', 'completed'))
    """
    )
