"""Merge migrations 243016ad35eb and 99d35b1ea1fc

Revision ID: a0e56e212c6a
Revises: 99d35b1ea1fc, 243016ad35eb
Create Date: 2022-01-26 18:09:18.384908

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a0e56e212c6a"
down_revision = ("99d35b1ea1fc", "243016ad35eb")
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
