"""remove is_read from notification

Revision ID: 5a7ba0146ee5
Revises: 9612aba86eb2
Create Date: 2021-06-30 16:14:22.419912

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a7ba0146ee5'
down_revision = '9612aba86eb2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('notification', 'is_read')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('notification', sa.Column('is_read', sa.BOOLEAN(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
