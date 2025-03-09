"""Remove free_bids_used from GullyParticipant model

Revision ID: edc12c7811d3
Revises: cfbb77fbbc4c
Create Date: 2025-03-09 10:57:38.525861

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "edc12c7811d3"
down_revision: Union[str, None] = "cfbb77fbbc4c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the free_bids_used column from gully_participants table
    op.drop_column("gully_participants", "free_bids_used")


def downgrade() -> None:
    # Add back the free_bids_used column to gully_participants table
    op.add_column(
        "gully_participants",
        sa.Column("free_bids_used", sa.INTEGER(), nullable=False, server_default="0"),
    )
