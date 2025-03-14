"""add_status_fields_to_gully_and_userplayer

Revision ID: 9e99274a72c2
Revises: f8eee723efa6
Create Date: 2025-03-14 12:39:57.208583

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9e99274a72c2"
down_revision: Union[str, None] = "f8eee723efa6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add status field to Gully table
    op.add_column(
        "gullies",
        sa.Column(
            "status",
            sa.String(),
            nullable=False,
            server_default="draft",
            index=True,
        ),
    )

    # Add CHECK constraint to ensure status is valid
    op.create_check_constraint(
        "ck_gully_status",
        "gullies",
        "status IN ('draft', 'auction', 'transfers', 'completed')",
    )

    # Add status field to UserPlayer table
    op.add_column(
        "user_players",
        sa.Column(
            "status",
            sa.String(),
            nullable=False,
            server_default="draft",
            index=True,
        ),
    )

    # Add CHECK constraint to ensure status is valid
    op.create_check_constraint(
        "ck_user_player_status",
        "user_players",
        "status IN ('draft', 'locked', 'contested', 'owned')",
    )


def downgrade() -> None:
    # Remove CHECK constraints
    op.drop_constraint("ck_user_player_status", "user_players", type_="check")
    op.drop_constraint("ck_gully_status", "gullies", type_="check")

    # Remove status columns
    op.drop_column("user_players", "status")
    op.drop_column("gullies", "status")
