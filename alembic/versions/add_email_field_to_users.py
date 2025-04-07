"""Add email field to users
Revision ID: add_email_field_to_users
Revises: f2f5e660a9c2
Create Date: 2025-04-01 10:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_email_field_to_users'
down_revision = 'f2f5e660a9c2'  # update this to the latest migration in your system
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('email', sa.String(), nullable=True, unique=True, index=True))


def downgrade():
    op.drop_column('users', 'email') 