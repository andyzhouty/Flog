"""Add back slug uniqueness check again

Revision ID: 4c31ffedf980
Revises: 5c9c64efc276
Create Date: 2020-11-15 19:50:26.450195

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4c31ffedf980"
down_revision = "5c9c64efc276"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, "post", ["slug"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "post", type_="unique")
    # ### end Alembic commands ###
