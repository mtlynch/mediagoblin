"""ArchivaLook plugin initial migration

Revision ID: b10b5f822789
Revises: 52bf0ccbedc1
Create Date: 2016-03-12 23:37:51.551856

"""

# revision identifiers, used by Alembic.
revision = 'b10b5f822789'
down_revision = '52bf0ccbedc1'
branch_labels = ('archivalook_plugin',)
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    if op.get_bind().engine.has_table('archivalook__featured_media'):
        # Skip; this has already been instantiated
        # (probably via sqlalchemy-migrate)
        return

    op.create_table(
        'archivalook__featured_media',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('media_entry_id', sa.Integer(), nullable=False),
        sa.Column('display_type', sa.Unicode(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['media_entry_id'],
                                ['core__media_entries.id']),
        sa.PrimaryKeyConstraint('id'))


def downgrade():
    op.drop_table('archivalook__featured_media')
