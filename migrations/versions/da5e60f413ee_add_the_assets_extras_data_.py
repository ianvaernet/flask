"""Add the asset extras for publsh table

Revision ID: da5e60f413ee
Revises: 08022051c993
Create Date: 2022-01-11 19:08:49.119778

"""
from alembic import op
import sqlalchemy as sa
from migrations.utils import exists_table, not_exists_table


# revision identifiers, used by Alembic.
revision = "da5e60f413ee"
down_revision = "08022051c993"
branch_labels = None
depends_on = None

__table_name: str = "assets_extras"
__editions_table_name: str = "editions"


def upgrade():
    if not_exists_table(__table_name):
        op.create_table(
            __table_name,
            sa.Column("avatar_wearable_id", sa.Integer(), nullable=False),
            sa.Column("images", sa.JSON(), nullable=False),
            sa.Column("videos", sa.JSON(), nullable=False),
            sa.Column("uuid", sa.String(length=100), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint("avatar_wearable_id"),
            sa.UniqueConstraint("uuid"),
        )


def downgrade():
    if exists_table(__table_name):
        op.drop_table(__table_name)
