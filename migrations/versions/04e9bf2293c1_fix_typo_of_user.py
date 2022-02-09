"""Fix typo of user

Revision ID: 04e9bf2293c1
Revises: ffb40e3d89ed
Create Date: 2020-12-31 18:08:48.492804

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "04e9bf2293c1"
down_revision = "ffb40e3d89ed"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("group_user", sa.Column("user_id", sa.Integer(), nullable=True))
    op.drop_constraint("group_user_ibfk_2", "group_user", type_="foreignkey")
    op.create_foreign_key(None, "group_user", "user", ["user_id"], ["id"])
    op.drop_column("group_user", "student_id")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "group_user",
        sa.Column(
            "student_id",
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.drop_constraint(None, "group_user", type_="foreignkey")
    op.create_foreign_key(
        "group_user_ibfk_2", "group_user", "user", ["student_id"], ["id"]
    )
    op.drop_column("group_user", "user_id")
    # ### end Alembic commands ###
