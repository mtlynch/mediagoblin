"""Audio media type initial migration

Revision ID: e9212d3a12d3
Revises: 52bf0ccbedc1
Create Date: 2016-03-12 22:37:35.086080
"""

# revision identifiers, used by Alembic.
revision = 'e9212d3a12d3'
down_revision = '52bf0ccbedc1'
branch_labels = ('audio_media_type',)
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    if op.get_bind().engine.has_table("audio__mediadata"):
        # Skip; this has already been instantiated
        # (probably via sqlalchemy-migrate)
        return

    op.create_table(
        'audio__mediadata',
        sa.Column('media_entry', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['media_entry'], ['core__media_entries.id'], ),
        sa.PrimaryKeyConstraint('media_entry'))


def downgrade():
    op.drop_table('audio__mediadata')
