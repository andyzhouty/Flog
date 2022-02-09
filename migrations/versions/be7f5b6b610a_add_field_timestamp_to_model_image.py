"""Add field timestamp to model Image

Revision ID: be7f5b6b610a
Revises: 4d7cdee9b1a4
Create Date: 2020-12-12 20:16:44.923016

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "be7f5b6b610a"
down_revision = "4d7cdee9b1a4"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("image", sa.Column("timestamp", sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("image", "timestamp")
    # ### end Alembic commands ###
