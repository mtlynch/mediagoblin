"""use_comment_link_ids_notifications

Revision ID: 4066b9f8b84a
Revises: 8429e33fdf7
Create Date: 2016-02-29 11:46:13.511318

"""

# revision identifiers, used by Alembic.
revision = '4066b9f8b84a'
down_revision = '8429e33fdf7'

from alembic import op
from sqlalchemy import MetaData
from sqlalchemy import and_
from mediagoblin.db.migration_tools import inspect_table

def upgrade():
    """"
    This replaces the Notification.obj with the ID of the Comment (i.e. comment
    link) ID instead of the TextComment object.
    """
    db = op.get_bind()
    metadata = MetaData(bind=db)
    notification_table = inspect_table(metadata, "core__notifications")
    comment_table = inspect_table(metadata, "core__comment_links")
    gmr_table = inspect_table(metadata, "core__generic_model_reference")

    # Get the notifications.
    notifications = list(db.execute(notification_table.select()))

    # Iterate through all the notifications
    for notification in notifications:
        # Lookup the Comment link object from the notification's ID
        comment_link = db.execute(comment_table.select().where(
            comment_table.c.comment_id == notification.object_id
        )).first()

        # Find the GMR for this comment or make one if one doesn't exist.
        gmr = db.execute(gmr_table.select().where(and_(
            gmr_table.c.obj_pk == comment_link.id,
            gmr_table.c.model_type == "core__comment_links"
        ))).first()

        # If it doesn't exist we need to create one.
        if gmr is None:
            gmr = db.execute(gmr_table.insert().values(
                obj_pk=comment_link.id,
                model_type="core__comment_links"
            )).inserted_primary_key[0]
        else:
            gmr = gmr.id

        # Okay now we need to update the notification with the ID of the link
        # rather than the ID of TextComment object.
        db.execute(notification_table.update().values(
            object_id=gmr
        ).where(
            notification_table.c.id == notification.id
        ))


def downgrade():
    """
    This puts back the TextComment ID for the notification.object_id field
    where we're using the Comment object (i.e. the comment link ID)
    """
    db = op.get_bind()
    metadata = MetaData(bind=db)
    notification_table = inspect_table(metadata, "core__notifications")
    comment_table = inspect_table(metadata, "core__comment_links")

    # Notificaitons
    notifications = list(db.execute(notification_table.select()))

    # Iterate through all the notifications
    for notification in notifications:
        # Lookup the Comment link object from the notification's ID
        comment_link = db.execute(comment_table.select().where(
            comment_table.c.id == notification.object_id
        )).first()

        # Find the GMR for the TextComment
        gmr = db.execute(gmr_table.select().where(and_(
            gmr_table.c.obj_pk == comment_link.id,
            gmr_table.c.model_type == "core__comment_links"
        ))).first()

        if gmr is None:
            gmr = db.execute(gmr_table.insert().values(
                obj_pk=comment_link.id,
                model_type="core__comment_links"
            )).inserted_primary_key[0]
        else:
            gmr = gmr.id

        # Update the notification with the TextComment (i.e. the comment object)
        db.execute(notification_table.update().values(
            object_id=gmr
        ).where(
            notification_table.c.id == notification.id
        ))

