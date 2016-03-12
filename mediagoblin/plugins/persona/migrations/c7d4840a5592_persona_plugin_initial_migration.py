"""Persona plugin initial migration

Revision ID: c7d4840a5592
Revises: 52bf0ccbedc1
Create Date: 2016-03-12 23:30:33.624390

"""

# revision identifiers, used by Alembic.
revision = 'c7d4840a5592'
down_revision = '52bf0ccbedc1'
branch_labels = ('persona_plugin',)
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    if op.get_bind().engine.has_table('persona__user_emails'):
        # Skip; this has already been instantiated
        # (probably via sqlalchemy-migrate)
        return

    op.create_table(
        'persona__user_emails',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('persona_email', sa.Unicode(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['core__users.id'], ),
        sa.PrimaryKeyConstraint('id'))


def downgrade():
    op.drop_table('persona__user_emails')
