"""Delete column date

Revision ID: f497cb532a67
Revises: aafd15767fb7
Create Date: 2020-10-20 22:20:37.908816

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f497cb532a67"
down_revision = "aafd15767fb7"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("post", "date")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "post",
        sa.Column("date", sa.VARCHAR(length=64), autoincrement=False, nullable=True),
    )
    # ### end Alembic commands ###
