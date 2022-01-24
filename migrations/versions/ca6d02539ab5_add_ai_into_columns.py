"""add ai into columns

Revision ID: ca6d02539ab5
Revises: 0a8453c4d88c
Create Date: 2022-01-24 10:35:02.869970

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "ca6d02539ab5"
down_revision = "0a8453c4d88c"
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
    # ### end Alembic commands ###
