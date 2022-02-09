"""this is a migration

Revision ID: 98fef64846fe
Revises: 4d7d3fed8e08
Create Date: 2021-10-04 10:43:01.404776

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "98fef64846fe"
down_revision = "4d7d3fed8e08"
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
