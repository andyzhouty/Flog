"""Initial migration

Revision ID: 101e0dba51e8
Revises: 
Create Date: 2021-10-08 19:45:02.273743

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import null


# revision identifiers, used by Alembic.
revision = "85c6222c1a96"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "articles",
        sa.Column("title", sa.String(length=64), nullable=True),
        sa.Column("author", sa.String(length=64), nullable=True),
        sa.Column("date", sa.String(length=64), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_articles_timestamp"), "articles", ["timestamp"], unique=False
    )
    op.create_index(op.f("ix_articles_title"), "articles", ["title"], unique=False)
    op.create_table(
        "feedback",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("body", sa.String(length=200), nullable=True),
        sa.Column("author", sa.String(length=20), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.Column("author_id", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_feedback_timestamp"), "feedback", ["timestamp"], unique=False
    )
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=True),
        sa.Column("default", sa.Boolean(), nullable=True),
        sa.Column("permissions", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_roles_default"), "roles", ["default"], unique=False)
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("confirmed", sa.Boolean(), nullable=True),
        sa.Column("password_hash", sa.String(length=128), nullable=True),
        sa.Column("avatar_hash", sa.String(length=32), nullable=True),
        sa.Column("locked", sa.Boolean(), nullable=True),
        sa.Column("location", sa.String(length=64), nullable=True),
        sa.Column("about_me", sa.Text(), nullable=True),
        sa.Column("member_since", sa.DateTime(), nullable=True),
        sa.Column("last_seen", sa.DateTime(), nullable=True),
        sa.Column("locale", sa.String(length=16), nullable=True),
        sa.Column("custom_avatar_url", sa.String(length=128), nullable=True),
        sa.Column("coins", sa.Float(), nullable=True),
        sa.Column("experience", sa.Integer(), nullable=True),
        sa.Column("avatar_style_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_name"), "user", ["name"], unique=True)
    op.alter_column(
        "articles", "author", existing_type=sa.VARCHAR(length=64), nullable=True
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_user_name"), table_name="user")
    op.drop_table("user")
    op.drop_index(op.f("ix_roles_default"), table_name="roles")
    op.drop_table("roles")
    op.drop_index(op.f("ix_feedback_timestamp"), table_name="feedback")
    op.drop_table("feedback")
    op.drop_index(op.f("ix_articles_title"), table_name="articles")
    op.drop_index(op.f("ix_articles_timestamp"), table_name="articles")
    op.drop_table("articles")
    # ### end Alembic commands ###
