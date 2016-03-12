"""Video media type initial migration

Revision ID: 38feb829c545
Revises: 52bf0ccbedc1
Create Date: 2016-03-12 22:44:16.291834

"""

# revision identifiers, used by Alembic.
revision = '38feb829c545'
down_revision = '52bf0ccbedc1'
branch_labels = ('video_media_type',)
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    if op.get_bind().engine.has_table("video__mediadata"):
        # Skip; this has already been instantiated
        # (probably via sqlalchemy-migrate)
        return

    op.create_table(
        'video__mediadata',
        sa.Column('media_entry', sa.Integer(), nullable=False),
        sa.Column('width', sa.SmallInteger(), nullable=True),
        sa.Column('height', sa.SmallInteger(), nullable=True),
        sa.Column('orig_metadata', sa.UnicodeText(), nullable=True),
        sa.ForeignKeyConstraint(['media_entry'], ['core__media_entries.id'], ),
        sa.PrimaryKeyConstraint('media_entry'))


def downgrade():
    op.drop_table('video__mediadata')
