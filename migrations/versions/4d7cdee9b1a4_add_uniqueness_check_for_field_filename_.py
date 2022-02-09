"""Add uniqueness check for field filename in model Image

Revision ID: 4d7cdee9b1a4
Revises: 66997fab6cc0
Create Date: 2020-12-12 19:47:17.602759

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4d7cdee9b1a4"
down_revision = "66997fab6cc0"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, "image", ["filename"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "image", type_="unique")
    # ### end Alembic commands ###
