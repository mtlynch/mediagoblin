"""#5382 Removes graveyard items from collections

Revision ID: 101510e3a713
Revises: 52bf0ccbedc1
Create Date: 2016-01-12 10:46:26.486610

"""

# revision identifiers, used by Alembic.
revision = '101510e3a713'
down_revision = '52bf0ccbedc1'

from alembic import op

import sqlalchemy as sa
from sqlalchemy.sql import and_

# Create the tables to query
gmr_table = sa.Table(
    "core__generic_model_reference",
    sa.MetaData(),
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("obj_pk", sa.Integer),
    sa.Column("model_type", sa.Unicode)
)

graveyard_table = sa.Table(
    "core__graveyard",
    sa.MetaData(),
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("public_id", sa.Unicode, unique=True),
    sa.Column("deleted", sa.DateTime, nullable=False),
    sa.Column("object_type", sa.Unicode, nullable=False),
    sa.Column("actor_id", sa.Integer)
)

collection_items_table = sa.Table(
    "core__collection_items",
    sa.MetaData(),
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("collection", sa.Integer, nullable=False),
    sa.Column("note", sa.UnicodeText),
    sa.Column("added", sa.DateTime, nullable=False),
    sa.Column("position", sa.Integer),
    sa.Column("object_id", sa.Integer, index=True)
) 

def upgrade():
    """
    The problem is deletions are occuring and as we expect the
    GenericModelReference objects are being updated to point to the tombstone
    object. The issue is that collections now contain deleted items, this
    causes problems when it comes to rendering them for example.

    This migration is to remove any Graveyard objects (tombstones) from any
    Collection.
    """
    connection = op.get_bind()

    for tombstone in connection.execute(graveyard_table.select()):
        # Get GMR for tombstone
        gmr = connection.execute(gmr_table.select().where(and_(
            gmr_table.c.obj_pk == tombstone.id,
            gmr_table.c.model_type == "core__graveyard"
        ))).first()

        # If there is no GMR, we're all good as it's required to be in a
        # collection
        if gmr is None:
            continue

        # Delete all the CollectionItem objects for this GMR
        connection.execute(collection_items_table.delete().where(
            collection_items_table.c.object_id == gmr.id
        ))


def downgrade():
    """
    Nothing to do here, the migration just deletes objects from collections.
    There are no schema changes that have occured. This can be reverted without
    any problems.
    """
    pass
