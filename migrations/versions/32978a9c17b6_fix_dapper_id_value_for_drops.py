"""Fix dapper_id value for drops

Revision ID: 32978a9c17b6
Revises: f8b3d59c9ab1
Create Date: 2022-02-11 01:27:12.983615

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from migrations.utils import exists_column, not_exists_column

# revision identifiers, used by Alembic.
revision = '32978a9c17b6'
down_revision = '3811817a1e80'
branch_labels = None
depends_on = None


def upgrade():
    if exists_column("drops", "dapper_flow_id") and not_exists_column(
        "drops", "dapper_drop_id"
    ):
        op.alter_column(
            "drops",
            column_name="dapper_flow_id",
            new_column_name="dapper_drop_id",
            existing_type=sa.String(100),
        )

def downgrade():
    if exists_column("drops", "dapper_drop_id") and not_exists_column(
        "drops", "dapper_flow_id"
    ):
        op.alter_column(
            "drops",
            column_name="dapper_drop_id",
            new_column_name="dapper_flow_id",
            existing_type=sa.Integer(),
        )
