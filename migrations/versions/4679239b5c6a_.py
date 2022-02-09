"""empty message

Revision ID: 4679239b5c6a
Revises: e0f3f6dca360
Create Date: 2021-05-29 19:35:51.035137

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4679239b5c6a"
down_revision = "e0f3f6dca360"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("group", "password_hash")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "group",
        sa.Column(
            "password_hash", sa.VARCHAR(length=128), autoincrement=False, nullable=True
        ),
    )
    # ### end Alembic commands ###
