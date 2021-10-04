"""this is a migration

Revision ID: 3aa95a42561c
Revises: 98fef64846fe
Create Date: 2021-10-04 10:49:46.832296

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3aa95a42561c'
down_revision = '98fef64846fe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('belong', schema=None) as batch_op:
        batch_op.create_foreign_key('owner_id', 'user', ['owner_id'], ['id'])

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('avatar_style', sa.String(length=1024)))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('avatar_style')

    with op.batch_alter_table('belong', schema=None) as batch_op:
        batch_op.drop_constraint('owner_id', type_='foreignkey')

    # ### end Alembic commands ###
