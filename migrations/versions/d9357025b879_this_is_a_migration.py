"""this is a migration

Revision ID: d9357025b879
Revises: 3aa95a42561c
Create Date: 2021-10-04 19:48:53.486012

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d9357025b879"
down_revision = "3aa95a42561c"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(sa.Column("avatar_style_id", sa.Integer(), nullable=True))
        batch_op.drop_column("avatar_style")

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("avatar_style", sa.VARCHAR(length=1024), nullable=True)
        )
        batch_op.drop_column("avatar_style_id")

    # ### end Alembic commands ###