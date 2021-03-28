"""empty message

Revision ID: 642b68fd39fe
Revises: 5caf2aefd50a
Create Date: 2021-03-28 08:34:51.157793

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '642b68fd39fe'
down_revision = '5caf2aefd50a'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('custom_avatar_url', sa.VARCHAR(128), nullable=True))


def downgrade():
    op.drop_column('user', 'custom_avatar_url')
