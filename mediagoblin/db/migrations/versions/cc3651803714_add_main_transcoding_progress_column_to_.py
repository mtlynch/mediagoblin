"""add main transcoding progress column to MediaEntry

Revision ID: cc3651803714
Revises: 228916769bd2
Create Date: 2017-08-21 23:33:01.401589

"""

# revision identifiers, used by Alembic.
revision = 'cc3651803714'
down_revision = '228916769bd2'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
	"""
	Addition of main_transcoding_progress is required to save the progress of the
	default resolution (other than the total progress of the video).
	"""
	op.add_column('core__media_entries', sa.Column('main_transcoding_progress', sa.Float(), default=0))


def downgrade():
    pass
