# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2011, 2012 MediaGoblin contributors.  See AUTHORS.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging

from mediagoblin.db.models import Notification, CommentSubscription, User, \
                                  Comment, GenericModelReference
from mediagoblin.notifications.task import email_notification_task
from mediagoblin.notifications.tools import generate_comment_message

_log = logging.getLogger(__name__)

def trigger_notification(comment, media_entry, request):
    '''
    Send out notifications about a new comment.
    '''
    # Verify we have the Comment object and not any other type e.g. TextComment
    if not isinstance(comment, Comment):
        raise ValueError("Must provide Comment to trigger_notification")

    # Get the associated object associated to the Comment wrapper.
    comment_object = comment.comment()

    subscriptions = CommentSubscription.query.filter_by(
        media_entry_id=media_entry.id).all()

    for subscription in subscriptions:
        # Check the user wants to be notified, if not, skip.
        if not subscription.notify:
            continue

        # If the subscriber is the current actor, don't bother.
        if comment_object.get_actor == subscription.user:
            continue

        cn = Notification(
            user_id=subscription.user_id,
        )
        cn.obj = comment
        cn.save()

        if subscription.send_email:
            message = generate_comment_message(
                subscription.user,
                comment,
                media_entry,
                request)

            from mediagoblin.notifications.task import email_notification_task
            email_notification_task.apply_async([cn.id, message])


def mark_notification_seen(notification):
    if notification:
        notification.seen = True
        notification.save()


def mark_comment_notification_seen(comment_id, user):
    comment = Comment.query.get(comment_id)

    # If there is no comment, there is no notification
    if comment == None:
        return

    comment_gmr = GenericModelReference.query.filter_by(
        obj_pk=comment.id,
        model_type=comment.__tablename__
    ).first()

    # If there is no GMR, there is no notification
    if comment_gmr == None:
        return

    notification = Notification.query.filter_by(
        user_id=user.id,
        object_id=comment_gmr.id
    ).first()

    _log.debug(u'Marking {0} as seen.'.format(notification))

    mark_notification_seen(notification)


def get_comment_subscription(user_id, media_entry_id):
    return CommentSubscription.query.filter_by(
        user_id=user_id,
        media_entry_id=media_entry_id).first()

def add_comment_subscription(user, media_entry):
    '''
    Create a comment subscription for a User on a MediaEntry.

    Uses the User's wants_comment_notification to set email notifications for
    the subscription to enabled/disabled.
    '''
    cn = get_comment_subscription(user.id, media_entry.id)

    if not cn:
        cn = CommentSubscription(
            user_id=user.id,
            media_entry_id=media_entry.id)

    cn.notify = True

    if not user.wants_comment_notification:
        cn.send_email = False

    cn.save()


def silence_comment_subscription(user, media_entry):
    '''
    Silence a subscription so that the user is never notified in any way about
    new comments on an entry
    '''
    cn = get_comment_subscription(user.id, media_entry.id)

    if cn:
        cn.notify = False
        cn.send_email = False
        cn.save()


def remove_comment_subscription(user, media_entry):
    cn = get_comment_subscription(user.id, media_entry.id)

    if cn:
        cn.delete()


NOTIFICATION_FETCH_LIMIT = 100


def get_notifications(user_id, only_unseen=True):
    query = Notification.query.filter_by(user_id=user_id)
    wants_notifications = User.query.filter_by(id=user_id).first()\
        .wants_notifications

    # If the user does not want notifications, don't return any
    if not wants_notifications:
        return None

    if only_unseen:
        query = query.filter_by(seen=False)

    notifications = query.limit(
        NOTIFICATION_FETCH_LIMIT).all()

    return notifications


def get_notification_count(user_id, only_unseen=True):
    query = Notification.query.filter_by(user_id=user_id)
    wants_notifications = User.query.filter_by(id=user_id).first()\
        .wants_notifications

    if only_unseen:
        query = query.filter_by(seen=False)

    # If the user doesn't want notifications, don't show any
    if not wants_notifications:
        count = None
    else:
        count = query.count()

    return count
