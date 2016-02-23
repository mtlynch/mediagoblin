"""Remove the Graveyard objects from CommentNotification objects

Revision ID: 8429e33fdf7
Revises: 101510e3a713
Create Date: 2016-01-19 08:01:21.577274

"""

# revision identifiers, used by Alembic.
revision = '8429e33fdf7'
down_revision = '101510e3a713'

from alembic import op
from sqlalchemy import MetaData
from sqlalchemy.sql import and_
from mediagoblin.db.migration_tools import inspect_table

def upgrade():
    """
    This migration is very similiar to that of 101510e3a713. It removes objects
    from Notification objects which are from Graveyard. It also iterates through
    any reports which might have been filed and sets the objects to None. 
    """
    db = op.get_bind()
    metadata = MetaData(bind=db)
    notification_table = inspect_table(metadata, "core__notifications")
    report_table = inspect_table(metadata, "core__reports")
    graveyard_table = inspect_table(metadata, "core__graveyard")
    gmr_table = inspect_table(metadata, "core__generic_model_reference")
    
    res = list(db.execute(gmr_table.select()))
    for tombstone in res:
        # Look up the gmr for the tombstone8
        gmr = db.execute(gmr_table.select().where(and_(
            gmr_table.c.obj_pk == tombstone.id,
            gmr_table.c.model_type == "core__graveyard"
        ))).first()

        # If we can't find one we can skip it as it needs one to be part of
        # the notification objects
        if gmr is None:
            continue

        # Delete all notifications which link to the GMR as that's invalid.
        db.execute(notification_table.delete().where(
            notification_table.c.object_id == gmr.id
        ))

        # Deal with reports, we don't want to delete these though, they want to
        # still exist if the object that was reported was deleted as that can
        # be part of the resolution, just set it to None.
        db.execute(report_table.update().where(
            report_table.c.object_id == gmr.id
        ).values(object_id=None))


def downgrade():
    """
    There is nothing to do as this was a data migration, it'll downgrade
    just fine without any steps. It's not like we can undo the deletions.
    """
    pass
