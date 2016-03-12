"""PDF media type initial migration

Revision ID: faa209f143b5
Revises: 52bf0ccbedc1
Create Date: 2016-03-12 23:08:16.698343

"""

# revision identifiers, used by Alembic.
revision = 'faa209f143b5'
down_revision = '52bf0ccbedc1'
branch_labels = ('pdf_media_type',)
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    if op.get_bind().engine.has_table("pdf__mediadata"):
        # Skip; this has already been instantiated
        # (probably via sqlalchemy-migrate)
        return

    op.create_table(
        'pdf__mediadata',
        sa.Column('media_entry', sa.Integer(), nullable=False),
        sa.Column('pages', sa.Integer(), nullable=True),
        sa.Column('pdf_author', sa.String(), nullable=True),
        sa.Column('pdf_title', sa.String(), nullable=True),
        sa.Column('pdf_keywords', sa.String(), nullable=True),
        sa.Column('pdf_creator', sa.String(), nullable=True),
        sa.Column('pdf_producer', sa.String(), nullable=True),
        sa.Column('pdf_creation_date', sa.DateTime(), nullable=True),
        sa.Column('pdf_modified_date', sa.DateTime(), nullable=True),
        sa.Column('pdf_version_major', sa.Integer(), nullable=True),
        sa.Column('pdf_version_minor', sa.Integer(), nullable=True),
        sa.Column('pdf_page_size_width', sa.Float(), nullable=True),
        sa.Column('pdf_page_size_height', sa.Float(), nullable=True),
        sa.Column('pdf_pages', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['media_entry'], ['core__media_entries.id'], ),
        sa.PrimaryKeyConstraint('media_entry'))


def downgrade():
    op.drop_table('pdf__mediadata')
