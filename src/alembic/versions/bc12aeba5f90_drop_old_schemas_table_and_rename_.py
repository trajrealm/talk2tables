"""Drop old schemas table and rename database_schema to user_db_schema

Revision ID: bc12aeba5f90
Revises: ee828ba9b4af
Create Date: 2025-06-24 10:37:00.699007

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bc12aeba5f90'
down_revision = 'ee828ba9b4af'
branch_labels = None
depends_on = None


def upgrade():
    # Drop old `schemas` table if it exists
    op.drop_table('schemas')

    # Rename `database_schema` to `user_db_schema`
    op.rename_table('database_schema', 'user_db_schema')


def downgrade():
    # Revert table rename
    op.rename_table('user_db_schema', 'database_schema')

    # Recreate `schemas` table (optional: match original schema)
    op.create_table(
        'schemas',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        # Add any other original columns if needed
    )