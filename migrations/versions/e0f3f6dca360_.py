"""empty message

Revision ID: e0f3f6dca360
Revises: 642b68fd39fe
Create Date: 2021-05-23 12:22:34.714086

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = 'e0f3f6dca360'
down_revision = '642b68fd39fe'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('group', sa.Column('password_hash', mysql.VARCHAR(length=128), nullable=True))


def downgrade():
    op.drop_column('group', 'password_hash')
