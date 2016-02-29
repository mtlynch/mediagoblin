"""remove tombstone comment wrappers

Revision ID: 3145accb8fe3
Revises: 4066b9f8b84a
Create Date: 2016-02-29 14:38:12.096859

"""

# revision identifiers, used by Alembic.
revision = '3145accb8fe3'
down_revision = '4066b9f8b84a'

from alembic import op
from sqlalchemy import MetaData, and_
from mediagoblin.db.migration_tools import inspect_table

def upgrade():
    """
    Removes comments which have been deleted and exist as a tombstone but still
    have their Comment wrapper.
    """
    db = op.get_bind()
    metadata = MetaData(bind=db)
    comment_table = inspect_table(metadata, "core__comment_links")
    gmr_table = inspect_table(metadata, "core__generic_model_reference")

    # Get the Comment wrappers
    comment_wrappers = list(db.execute(comment_table.select()))

    for wrapper in comment_wrappers:
        # Query for the graveyard GMR comment
        gmr = db.execute(gmr_table.select().where(and_(
            gmr_table.c.id == wrapper.comment_id,
            gmr_table.c.model_type == "core__graveyard"
        ))).first()

        if gmr is not None:
            # Okay delete this wrapper as it's to a deleted comment
            db.execute(comment_table.delete().where(
                comment_table.c.id == wrapper.id
            ))

def downgrade():
    pass
