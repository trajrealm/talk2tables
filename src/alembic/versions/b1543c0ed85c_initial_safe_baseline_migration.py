"""initial safe baseline migration

Revision ID: b1543c0ed85c
Revises: 887033a372ee
Create Date: 2025-06-23 11:03:34.122214

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg


# revision identifiers, used by Alembic.
revision = 'b1543c0ed85c'
down_revision = '887033a372ee'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgcrypto extension for UUID generation
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    op.create_table(
        "users",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.Text, unique=True, nullable=False),
        sa.Column("hashed_password", sa.Text, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "user_databases",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("db_type", sa.Text, nullable=False),
        sa.Column("host", sa.Text, nullable=False),
        sa.Column("port", sa.Integer, nullable=False),
        sa.Column("db_name", sa.Text, nullable=False),
        sa.Column("username", sa.Text, nullable=False),
        sa.Column("password_encrypted", sa.Text, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "schemas",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_db_id", pg.UUID(as_uuid=True), sa.ForeignKey("user_databases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("table_name", sa.Text, nullable=False),
        sa.Column("column_name", sa.Text, nullable=False),
        sa.Column("data_type", sa.Text, nullable=False),
        sa.Column("is_nullable", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("is_primary_key", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("is_foreign_key", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("references_table", sa.Text),
        sa.Column("references_column", sa.Text),
        sa.Column("last_indexed", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "query_history",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_db_id", pg.UUID(as_uuid=True), sa.ForeignKey("user_databases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("generated_sql", sa.Text),
        sa.Column("result", sa.JSON),
        sa.Column("success", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("error", sa.Text),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "query_feedback",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("query_id", pg.UUID(as_uuid=True), sa.ForeignKey("query_history.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rating", sa.Integer),
        sa.Column("comment", sa.Text),
    )



def downgrade() -> None:
    op.drop_table("query_feedback")
    op.drop_table("query_history")
    op.drop_table("schemas")
    op.drop_table("user_databases")
    op.drop_table("users")