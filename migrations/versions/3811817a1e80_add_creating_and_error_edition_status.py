"""Add creating and error edition status

Revision ID: 3811817a1e80
Revises: db7c4efd6fde
Create Date: 2022-01-27 22:55:57.035452

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy.sql import table
from migrations.utils import exists_table
from migrations.utils import (
    exists_table,
    exists_column,
)

# revision identifiers, used by Alembic.
revision = "3811817a1e80"
down_revision = "db7c4efd6fde"
branch_labels = None
depends_on = None

__table_name: str = "editions"
__og_enum: list = [
    "DRAFT",
    "CREATED",
    "MINTED",
    "ON_SALE",
]
__new_enum: list = [
    "DRAFT",
    "CREATING",
    "CREATED",
    "MINTED",
    "ON_SALE",
    "ERROR",
]
__column_name: str = "status"


def upgrade():
    if exists_table(__table_name):
        if exists_column(__table_name, __column_name):
            op.alter_column(
                __table_name,
                __column_name,
                existing_type=sa.Enum(*__og_enum),
                type_=sa.Enum(*__new_enum),
            )
        else:
            op.add_column(__table_name, sa.Column(__column_name, sa.Enum(*__new_enum)))


def downgrade():
    if exists_table(__table_name):
        if exists_column(__table_name, __column_name):
            editions = table(__table_name)
            op.execute(
                editions.update()
                .where(editions.c.status == op.inline_literal("CREATING"))
                .values({"status": op.inline_literal("DRAFT")})
            )
            op.execute(
                editions.update()
                .where(editions.c.status == op.inline_literal("ERROR"))
                .values({"status": op.inline_literal("DRAFT")})
            )
