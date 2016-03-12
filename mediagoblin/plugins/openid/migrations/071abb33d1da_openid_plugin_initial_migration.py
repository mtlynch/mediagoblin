"""OpenID plugin initial migration

Revision ID: 071abb33d1da
Revises: 52bf0ccbedc1
Create Date: 2016-03-12 23:32:58.191980

"""

# revision identifiers, used by Alembic.
revision = '071abb33d1da'
down_revision = '52bf0ccbedc1'
branch_labels = ('openid_plugin',)
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    if op.get_bind().engine.has_table('openid__association'):
        # Skip; this has already been instantiated
        # (probably via sqlalchemy-migrate)
        return

    op.create_table(
        'openid__association',
        sa.Column('server_url', sa.Unicode(), nullable=False),
        sa.Column('handle', sa.Unicode(), nullable=False),
        sa.Column('secret', sa.Unicode(), nullable=True),
        sa.Column('issued', sa.Integer(), nullable=True),
        sa.Column('lifetime', sa.Integer(), nullable=True),
        sa.Column('assoc_type', sa.Unicode(), nullable=True),
        sa.PrimaryKeyConstraint('server_url', 'handle'))

    op.create_table(
        'openid__nonce',
        sa.Column('server_url', sa.Unicode(), nullable=False),
        sa.Column('timestamp', sa.Integer(), nullable=False),
        sa.Column('salt', sa.Unicode(), nullable=False),
        sa.PrimaryKeyConstraint('server_url', 'timestamp', 'salt'))

    op.create_table(
        'openid__user_urls',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('openid_url', sa.Unicode(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['core__users.id'], ),
        sa.PrimaryKeyConstraint('id'))


def downgrade():
    op.drop_table('openid__user_urls')
    op.drop_table('openid__nonce')
    op.drop_table('openid__association')
