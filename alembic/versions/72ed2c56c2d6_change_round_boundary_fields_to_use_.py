"""Change round boundary fields to use inclusive model

Revision ID: 72ed2c56c2d6
Revises: 6c5a10dbd89e
Create Date: 2023-XX-XX

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "72ed2c56c2d6"
down_revision: Union[str, None] = "6c5a10dbd89e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Add new columns as nullable
    op.add_column(
        "ipl_balanced_rounds", sa.Column("first_match", sa.Integer(), nullable=True)
    )
    op.add_column(
        "ipl_balanced_rounds", sa.Column("last_match", sa.Integer(), nullable=True)
    )

    # Step 2: Update existing data - convert start_match/end_match to first_match/last_match
    op.execute(
        """
    UPDATE ipl_balanced_rounds 
    SET first_match = start_match + 1,
        last_match = end_match
    """
    )

    # Step 3: Now make the columns NOT NULL
    op.alter_column("ipl_balanced_rounds", "first_match", nullable=False)
    op.alter_column("ipl_balanced_rounds", "last_match", nullable=False)

    # Step 4: Drop old columns
    op.drop_column("ipl_balanced_rounds", "start_match")
    op.drop_column("ipl_balanced_rounds", "end_match")


def downgrade() -> None:
    # Step 1: Add back the old columns as nullable
    op.add_column(
        "ipl_balanced_rounds",
        sa.Column("start_match", sa.Integer(), nullable=True),
    )
    op.add_column(
        "ipl_balanced_rounds",
        sa.Column("end_match", sa.Integer(), nullable=True),
    )

    # Step 2: Populate the old columns based on new columns
    op.execute(
        """
    UPDATE ipl_balanced_rounds 
    SET start_match = first_match - 1,
        end_match = last_match
    """
    )

    # Step 3: Make old columns NOT NULL
    op.alter_column("ipl_balanced_rounds", "start_match", nullable=False)
    op.alter_column("ipl_balanced_rounds", "end_match", nullable=False)

    # Step 4: Drop new columns
    op.drop_column("ipl_balanced_rounds", "first_match")
    op.drop_column("ipl_balanced_rounds", "last_match")
