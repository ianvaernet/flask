"""Change dapper_entity_id to dapper_flow_id

Revision ID: a1e211dc04b9
Revises: f27e256d11c1
Create Date: 2022-01-26 15:31:32.513248

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from migrations.utils import exists_column, not_exists_column

# revision identifiers, used by Alembic.
revision = "a1e211dc04b9"
down_revision = "f27e256d11c1"
branch_labels = None
depends_on = None


def upgrade():
    if exists_column("series", "dapper_series_id") and not_exists_column(
        "series", "dapper_flow_id"
    ):
        op.alter_column(
            "series",
            column_name="dapper_series_id",
            new_column_name="dapper_flow_id",
            existing_type=sa.Integer(),
        )
    if exists_column("collections", "dapper_collection_id") and not_exists_column(
        "collections", "dapper_flow_id"
    ):
        op.alter_column(
            "collections",
            column_name="dapper_collection_id",
            new_column_name="dapper_flow_id",
            existing_type=sa.Integer(),
        )
    if exists_column("editions", "dapper_edition_id") and not_exists_column(
        "editions", "dapper_flow_id"
    ):
        op.alter_column(
            "editions",
            column_name="dapper_edition_id",
            new_column_name="dapper_flow_id",
            existing_type=sa.Integer(),
        )
    if exists_column("drops", "dapper_drop_id") and not_exists_column(
        "drops", "dapper_flow_id"
    ):
        op.alter_column(
            "drops",
            column_name="dapper_drop_id",
            new_column_name="dapper_flow_id",
            existing_type=sa.Integer(),
        )
    if exists_column("nfts", "dapper_nft_id") and not_exists_column(
        "nfts", "dapper_flow_id"
    ):
        op.alter_column(
            "nfts",
            column_name="dapper_nft_id",
            new_column_name="dapper_flow_id",
            existing_type=sa.Integer(),
        )


def downgrade():
    if exists_column("series", "dapper_flow_id") and not_exists_column(
        "series", "dapper_series_id"
    ):
        op.alter_column(
            "series",
            column_name="dapper_flow_id",
            new_column_name="dapper_series_id",
            existing_type=sa.Integer(),
        )
    if exists_column("collections", "dapper_flow_id") and not_exists_column(
        "collections", "dapper_collection_id"
    ):
        op.alter_column(
            "collections",
            column_name="dapper_flow_id",
            new_column_name="dapper_collection_id",
            existing_type=sa.Integer(),
        )
    if exists_column("editions", "dapper_flow_id") and not_exists_column(
        "editions", "dapper_edition_id"
    ):
        op.alter_column(
            "editions",
            column_name="dapper_flow_id",
            new_column_name="dapper_edition_id",
            existing_type=sa.Integer(),
        )
    if exists_column("drops", "dapper_flow_id") and not_exists_column(
        "drops", "dapper_drop_id"
    ):
        op.alter_column(
            "drops",
            column_name="dapper_flow_id",
            new_column_name="dapper_drop_id",
            existing_type=sa.Integer(),
        )
    if exists_column("nfts", "dapper_flow_id") and not_exists_column(
        "nfts", "dapper_nft_id"
    ):
        op.alter_column(
            "nfts",
            column_name="dapper_flow_id",
            new_column_name="dapper_nft_id",
            existing_type=sa.Integer(),
        )
