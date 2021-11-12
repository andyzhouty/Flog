"""

Revision ID: 3f81c4c0180e
Revises: 5781dd3e1670
Create Date: 2021-11-10 14:15:35.722642

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3f81c4c0180e"
down_revision = "5781dd3e1670"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("feedback", schema=None) as batch_op:
        batch_op.add_column(sa.Column("author_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("user", "user", ["author_id"], ["id"])
        batch_op.drop_column("author")

    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(sa.Column("username", sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column("confirmed", sa.Boolean(), nullable=True))
        batch_op.add_column(
            sa.Column("avatar_hash", sa.String(length=32), nullable=True)
        )
        batch_op.add_column(sa.Column("locked", sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column("location", sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column("about_me", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("member_since", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("last_seen", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("locale", sa.String(length=16), nullable=True))
        batch_op.add_column(
            sa.Column("custom_avatar_url", sa.String(length=128), nullable=True)
        )
        batch_op.add_column(sa.Column("coins", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("experience", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("avatar_style_id", sa.Integer(), nullable=True))
        batch_op.drop_index("ix_user_name")
        batch_op.create_index(batch_op.f("ix_user_username"), ["username"], unique=True)

    # ### end Alembic commands ###

    # ### end Alembic commands ###