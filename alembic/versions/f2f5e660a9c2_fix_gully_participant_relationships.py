"""fix_gully_participant_relationships

Revision ID: f2f5e660a9c2
Revises: update_user_gully_relationships
Create Date: 2025-03-11 15:02:05.936095

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "f2f5e660a9c2"
down_revision: Union[str, None] = "update_user_gully_relationships"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # No schema changes needed - the relationship changes are in the Python code
    # We're only fixing the relationship definitions between models
    pass


def downgrade() -> None:
    # No schema changes to revert
    pass
