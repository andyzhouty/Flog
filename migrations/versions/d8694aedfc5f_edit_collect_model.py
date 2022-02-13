"""edit collect model

Revision ID: d8694aedfc5f
Revises: 30ce011500f9
Create Date: 2022-02-12 01:06:03.796506

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'd8694aedfc5f'
down_revision = '30ce011500f9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('collect', sa.Column('post_id', sa.Integer(), nullable=True))
    op.add_column('collect', sa.Column('user_id', sa.Integer(), nullable=True))
    op.drop_constraint('collect_ibfk_1', 'collect', type_='foreignkey')
    op.drop_constraint('collect_ibfk_2', 'collect', type_='foreignkey')
    op.create_foreign_key(None, 'collect', 'user', ['user_id'], ['id'])
    op.create_foreign_key(None, 'collect', 'post', ['post_id'], ['id'])
    op.drop_column('collect', 'collector_id')
    op.drop_column('collect', 'collected_id')
    op.drop_column('collect', 'created_at')
    op.drop_column('collect', 'timestamp')
    op.drop_column('collect', 'updated_at')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('collect', sa.Column('updated_at', mysql.DATETIME(), nullable=True))
    op.add_column('collect', sa.Column('timestamp', mysql.DATETIME(), nullable=True))
    op.add_column('collect', sa.Column('created_at', mysql.DATETIME(), nullable=True))
    op.add_column('collect', sa.Column('collected_id', mysql.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('collect', sa.Column('collector_id', mysql.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'collect', type_='foreignkey')
    op.drop_constraint(None, 'collect', type_='foreignkey')
    op.create_foreign_key('collect_ibfk_2', 'collect', 'post', ['collected_id'], ['id'])
    op.create_foreign_key('collect_ibfk_1', 'collect', 'user', ['collector_id'], ['id'])
    op.drop_column('collect', 'user_id')
    op.drop_column('collect', 'post_id')
    # ### end Alembic commands ###
