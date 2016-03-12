"""Ascii media type initial migration

Revision ID: 72bd70f7eefd
Revises: 52bf0ccbedc1
Create Date: 2016-03-12 22:50:58.382980

"""

# revision identifiers, used by Alembic.
revision = '72bd70f7eefd'
down_revision = '52bf0ccbedc1'
branch_labels = ('ascii_media_type',)
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    if op.get_bind().engine.has_table("ascii__mediadata"):
        # Skip; this has already been instantiated
        # (probably via sqlalchemy-migrate)
        return

    op.create_table(
        'ascii__mediadata',
        sa.Column('media_entry', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['media_entry'], ['core__media_entries.id'], ),
        sa.PrimaryKeyConstraint('media_entry'))


def downgrade():
    op.drop_table('ascii__mediadata')
