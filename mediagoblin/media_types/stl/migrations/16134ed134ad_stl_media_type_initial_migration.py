"""STL media type initial migration

Revision ID: 16134ed134ad
Revises: 52bf0ccbedc1
Create Date: 2016-03-12 23:00:43.084284

"""

# revision identifiers, used by Alembic.
revision = '16134ed134ad'
down_revision = '52bf0ccbedc1'
branch_labels = ('stl_media_type',)
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    if op.get_bind().engine.has_table("stl__mediadata"):
        # Skip; this has already been instantiated
        # (probably via sqlalchemy-migrate)
        return

    op.create_table(
        'stl__mediadata',
        sa.Column('media_entry', sa.Integer(), nullable=False),
        sa.Column('center_x', sa.Float(), nullable=True),
        sa.Column('center_y', sa.Float(), nullable=True),
        sa.Column('center_z', sa.Float(), nullable=True),
        sa.Column('width', sa.Float(), nullable=True),
        sa.Column('height', sa.Float(), nullable=True),
        sa.Column('depth', sa.Float(), nullable=True),
        sa.Column('file_type', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['media_entry'], ['core__media_entries.id'], ),
        sa.PrimaryKeyConstraint('media_entry'))


def downgrade():
    op.drop_table('stl__mediadata')
