"""Update User-Gully relationships

Revision ID: update_user_gully_relationships
Revises: 109a5d59c9b1
Create Date: 2025-03-11 13:00:00.000000

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "update_user_gully_relationships"
down_revision: Union[str, None] = "109a5d59c9b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # No schema changes needed - the relationship changes are in the Python code
    pass


def downgrade() -> None:
    # No schema changes to revert
    pass
