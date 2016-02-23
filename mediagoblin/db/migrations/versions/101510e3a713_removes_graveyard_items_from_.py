"""#5382 Removes graveyard items from collections

Revision ID: 101510e3a713
Revises: 52bf0ccbedc1
Create Date: 2016-01-12 10:46:26.486610

"""

# revision identifiers, used by Alembic.
revision = '101510e3a713'
down_revision = '52bf0ccbedc1'

from alembic import op
from sqlalchemy import MetaData
from sqlalchemy.sql import and_
from mediagoblin.db.migration_tools import inspect_table

def upgrade():
    """
    The problem is deletions are occuring and as we expect the
    GenericModelReference objects are being updated to point to the tombstone
    object. The issue is that collections now contain deleted items, this
    causes problems when it comes to rendering them for example.

    This migration is to remove any Graveyard objects (tombstones) from any
    Collection.
    """
    db = op.get_bind()
    metadata = MetaData(bind=db)
   
    gmr_table = inspect_table(metadata, "core__generic_model_reference")
    collection_items_table = inspect_table(metadata, "core__collection_items")
    graveyard_table = inspect_table(metadata, "core__graveyard")

    res = list(db.execute(graveyard_table.select()))
    for tombstone in res:
        # Get GMR for tombstone
        gmr = db.execute(gmr_table.select().where(and_(
            gmr_table.c.obj_pk == tombstone.id,
            gmr_table.c.model_type == "core__graveyard"
        ))).first()

        # If there is no GMR, we're all good as it's required to be in a
        # collection
        if gmr is None:
            continue

        # Delete all the CollectionItem objects for this GMR
        db.execute(collection_items_table.delete().where(
            collection_items_table.c.object_id == gmr.id
        ))


def downgrade():
    """
    Nothing to do here, the migration just deletes objects from collections.
    There are no schema changes that have occured. This can be reverted without
    any problems.
    """
    pass
