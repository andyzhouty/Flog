"""Replace block with 'lock'

Revision ID: 8192b68b7bd0
Revises: 3176777cd2bb
Create Date: 2021-01-20 20:48:40.867104

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '8192b68b7bd0'
down_revision = '3176777cd2bb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('locked', sa.Boolean(), nullable=True))
    op.drop_column('user', 'blocked')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('blocked', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.drop_column('user', 'locked')
    # ### end Alembic commands ###