"""this is a migration

Revision ID: 4d7d3fed8e08
Revises: 22cb187afb24, 4567890123ab
Create Date: 2021-10-04 10:33:20.962968

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4d7d3fed8e08"
down_revision = "dd62dd1cc018"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, "belong", "user", ["owner_id"], ["id"])
    op.add_column(
        "user", sa.Column("avatar_style", sa.String(length=1024), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("user", "avatar_style")
    op.drop_constraint(None, "belong", type_="foreignkey")
    # ### end Alembic commands ###
