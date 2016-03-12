"""Image media type initial migration

Revision ID: a98c1a320e88
Revises: 52bf0ccbedc1
Create Date: 2016-03-12 21:10:10.155623
"""

# revision identifiers, used by Alembic.
revision = 'a98c1a320e88'
down_revision = '52bf0ccbedc1'
branch_labels = ('image_media_type',)
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    if op.get_bind().engine.has_table("image__mediadata"):
        # Skip; this has already been instantiated
        # (probably via sqlalchemy-migrate)
        return

    op.create_table(
        'image__mediadata',
        sa.Column('media_entry', sa.Integer(), nullable=False),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('exif_all', sa.UnicodeText(), nullable=True),
        sa.ForeignKeyConstraint(['media_entry'], ['core__media_entries.id'], ),
        sa.PrimaryKeyConstraint('media_entry'))


def downgrade():
    # @@: Is this safe?
    op.drop_table('image__mediadata')
