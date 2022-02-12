"""Merge migrations f27e256d11c1 and da5e60f413ee

Revision ID: 243016ad35eb
Revises: f27e256d11c1, da5e60f413ee
Create Date: 2022-01-24 12:17:47.183902

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "243016ad35eb"
down_revision = ("f27e256d11c1", "da5e60f413ee")
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
