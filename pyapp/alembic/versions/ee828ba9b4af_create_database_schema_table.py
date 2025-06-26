"""create database_schema table

Revision ID: ee828ba9b4af
Revises: b1543c0ed85c
Create Date: 2025-06-24 10:31:37.937898

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg



# revision identifiers, used by Alembic.
revision = 'ee828ba9b4af'
down_revision = 'b1543c0ed85c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'database_schema',
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_database_id", pg.UUID(as_uuid=True), sa.ForeignKey("user_databases.id", ondelete="CASCADE"), nullable=False),
        sa.Column('schema_name', sa.String(), nullable=False),
        sa.Column('schema_json_info', sa.JSON(), nullable=False)
    )

def downgrade():
    op.drop_table('database_schema')