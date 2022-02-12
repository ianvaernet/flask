"""Add editions error table

Revision ID: db7c4efd6fde
Revises: a0e56e212c6a
Create Date: 2022-01-27 19:06:34.529257

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from migrations.utils import exists_table, not_exists_table

# revision identifiers, used by Alembic.
revision = "db7c4efd6fde"
down_revision = "a0e56e212c6a"
branch_labels = None
depends_on = None

__table_name: str = "editions_errors"
__editions_table_name: str = "editions"


def upgrade():
    if not_exists_table(__table_name):
        op.create_table(
            __table_name,
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("edition_id", sa.Integer(), nullable=False),
            sa.Column("error", sa.Text(), nullable=False),
            sa.Column("type", sa.String(length=100), nullable=False),
            sa.Column("suggested_solution", sa.String(length=500), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(
                ["edition_id"],
                ["editions.id"],
            ),
        )


def downgrade():
    if exists_table(__table_name):
        op.drop_table(__table_name)
