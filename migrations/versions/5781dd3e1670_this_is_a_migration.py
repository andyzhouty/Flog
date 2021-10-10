"""this is a migration

Revision ID: 5781dd3e1670
Revises: d9357025b879
Create Date: 2021-10-10 14:02:54.696749

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5781dd3e1670'
down_revision = 'd9357025b879'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('feedback', schema=None) as batch_op:
        batch_op.add_column(sa.Column('author_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('author_id', 'user', ['author_id'], ['id'])
        batch_op.drop_column('author')

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('username', sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column('confirmed', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('avatar_hash', sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column('locked', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('location', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('about_me', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('member_since', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('last_seen', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('locale', sa.String(length=16), nullable=True))
        batch_op.add_column(sa.Column('custom_avatar_url', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('coins', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('experience', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('avatar_style_id', sa.Integer(), nullable=True))
        batch_op.drop_index('ix_user_name')
        batch_op.create_index(batch_op.f('ix_user_username'), ['username'], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_username'))
        batch_op.create_index('ix_user_name', ['name'], unique=False)
        batch_op.drop_column('avatar_style_id')
        batch_op.drop_column('experience')
        batch_op.drop_column('coins')
        batch_op.drop_column('custom_avatar_url')
        batch_op.drop_column('locale')
        batch_op.drop_column('last_seen')
        batch_op.drop_column('member_since')
        batch_op.drop_column('about_me')
        batch_op.drop_column('location')
        batch_op.drop_column('locked')
        batch_op.drop_column('avatar_hash')
        batch_op.drop_column('confirmed')
        batch_op.drop_column('username')

    with op.batch_alter_table('feedback', schema=None) as batch_op:
        batch_op.add_column(sa.Column('author', sa.VARCHAR(length=20), nullable=True))
        batch_op.drop_constraint('author_id', type_='foreignkey')
        batch_op.drop_column('author_id')

    # ### end Alembic commands ###
