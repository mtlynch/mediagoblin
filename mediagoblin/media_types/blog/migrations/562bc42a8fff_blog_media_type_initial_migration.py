"""Blog media type initial migration

Revision ID: 562bc42a8fff
Revises: 52bf0ccbedc1
Create Date: 2016-03-12 23:17:45.477894

"""

# revision identifiers, used by Alembic.
revision = '562bc42a8fff'
down_revision = '52bf0ccbedc1'
branch_labels = ('blog_media_type',)
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    if op.get_bind().engine.has_table("blogpost__mediadata"):
        # Skip; this has already been instantiated
        # (probably via sqlalchemy-migrate)
        return

    op.create_table(
        'mediatype__blogs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.Unicode(), nullable=True),
        sa.Column('description', sa.UnicodeText(), nullable=True),
        sa.Column('author', sa.Integer(), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('slug', sa.Unicode(), nullable=True),
        sa.ForeignKeyConstraint(['author'], ['core__users.id']),
        sa.PrimaryKeyConstraint('id'))

    op.create_index(
        op.f('ix_mediatype__blogs_author'),
        'mediatype__blogs', ['author'], unique=False)

    op.create_index(
        op.f('ix_mediatype__blogs_created'),
        'mediatype__blogs', ['created'], unique=False)

    op.create_table(
        'blogpost__mediadata',
        sa.Column('media_entry', sa.Integer(), nullable=False),
        sa.Column('blog', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['blog'], ['mediatype__blogs.id']),
        sa.ForeignKeyConstraint(['media_entry'], ['core__media_entries.id']),
        sa.PrimaryKeyConstraint('media_entry'))


def downgrade():
    op.drop_table('blogpost__mediadata')
    op.drop_index(op.f('ix_mediatype__blogs_created'),
                  table_name='mediatype__blogs')
    op.drop_index(op.f('ix_mediatype__blogs_author'),
                  table_name='mediatype__blogs')
    op.drop_table('mediatype__blogs')
