"""empty message

Revision ID: a1f1e9336ecf
Revises: 780c29109b25
Create Date: 2020-08-30 15:27:53.720024

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a1f1e9336ecf"
down_revision = "780c29109b25"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, "feedback", "user", ["author_id"], ["id"])
    op.drop_column("feedback", "author")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("feedback", sa.Column("author", sa.VARCHAR(length=20), nullable=True))
    op.drop_constraint(None, "feedback", type_="foreignkey")
    # ### end Alembic commands ###
