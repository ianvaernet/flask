"""Add dapper_edition_id column

Revision ID: 99d35b1ea1fc
Revises: a1e211dc04b9
Create Date: 2022-01-26 15:53:48.589667

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "99d35b1ea1fc"
down_revision = "a1e211dc04b9"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "editions", sa.Column("dapper_edition_id", sa.String(length=100), nullable=True)
    )


def downgrade():
    op.drop_column("editions", "dapper_edition_id")
