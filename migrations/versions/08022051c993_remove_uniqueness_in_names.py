"""Remove uniqueness in names

Revision ID: 08022051c993
Revises: 5a79dfd022e2
Create Date: 2021-12-08 15:13:57.871878

"""
from alembic import op
import sqlalchemy as sa

from migrations.utils import has_index, has_not_index


# revision identifiers, used by Alembic.
revision = "08022051c993"
down_revision = "5a79dfd022e2"
branch_labels = None
depends_on = None


def upgrade():
    if has_index("collections", "name"):
        op.drop_index("name", table_name="collections")
    if has_index("editions", "name"):
        op.drop_index("name", table_name="editions")
    if has_index("series", "name"):
        op.drop_index("name", table_name="series")


def downgrade():
    if has_not_index("series", "name"):
        op.create_index("name", "series", ["name"], unique=True)
    if has_not_index("editions", "name"):
        op.create_index("name", "editions", ["name"], unique=True)
    if has_not_index("collections", "name"):
        op.create_index("name", "collections", ["name"], unique=True)
