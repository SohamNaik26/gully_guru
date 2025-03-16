"""Update player types from ALL to AR

Revision ID: dec481882462
Revises: 77fc500320b5
Create Date: 2025-03-15

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "dec481882462"
down_revision = "77fc500320b5"  # Previous revision ID
branch_labels = None
depends_on = None


def upgrade():
    """Update player_type from ALL to AR."""
    op.execute("UPDATE players SET player_type = 'AR' WHERE player_type = 'ALL'")


def downgrade():
    """Revert player_type from AR to ALL."""
    op.execute("UPDATE players SET player_type = 'ALL' WHERE player_type = 'AR'")
