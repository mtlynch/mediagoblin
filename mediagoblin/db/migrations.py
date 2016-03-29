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

from __future__ import print_function

import datetime
import uuid

import six

try:
    import migrate
except ImportError:
    # Apparently sqlalchemy-migrate is not installed, so we assume
    # we must not need it
    # TODO: Better error handling here, or require sqlalchemy-migrate
    print("sqlalchemy-migrate not found... assuming we don't need it")
    print("I hope you aren't running the legacy migrations!")

import pytz
import dateutil.tz
from sqlalchemy import (MetaData, Table, Column, Boolean, SmallInteger,
                        Integer, Unicode, UnicodeText, DateTime,
                        ForeignKey, Date, Index)
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import and_
from sqlalchemy.schema import UniqueConstraint

from mediagoblin import oauth
from mediagoblin.tools import crypto
from mediagoblin.db.extratypes import JSONEncoded, MutationDict
from mediagoblin.db.migration_tools import (
    RegisterMigration, inspect_table, replace_table_hack, model_iteration_hack)
from mediagoblin.db.models import (MediaEntry, Collection, Comment, User,
                                   Privilege, Generator, LocalUser, Location,
                                   Client, RequestToken, AccessToken)
from mediagoblin.db.extratypes import JSONEncoded, MutationDict


MIGRATIONS = {}


@RegisterMigration(1, MIGRATIONS)
def ogg_to_webm_audio(db_conn):
    metadata = MetaData(bind=db_conn.bind)

    file_keynames = Table('core__file_keynames', metadata, autoload=True,
                          autoload_with=db_conn.bind)

    db_conn.execute(
        file_keynames.update().where(file_keynames.c.name == 'ogg').
            values(name='webm_audio')
    )
    db_conn.commit()


@RegisterMigration(2, MIGRATIONS)
def add_wants_notification_column(db_conn):
    metadata = MetaData(bind=db_conn.bind)

    users = Table('core__users', metadata, autoload=True,
            autoload_with=db_conn.bind)

    col = Column('wants_comment_notification', Boolean,
            default=True, nullable=True)
    col.create(users, populate_defaults=True)
    db_conn.commit()


@RegisterMigration(3, MIGRATIONS)
def add_transcoding_progress(db_conn):
    metadata = MetaData(bind=db_conn.bind)

    media_entry = inspect_table(metadata, 'core__media_entries')

    col = Column('transcoding_progress', SmallInteger)
    col.create(media_entry)
    db_conn.commit()


class Collection_v0(declarative_base()):
    __tablename__ = "core__collections"

    id = Column(Integer, primary_key=True)
    title = Column(Unicode, nullable=False)
    slug = Column(Unicode)
    created = Column(DateTime, nullable=False, default=datetime.datetime.now,
        index=True)
    description = Column(UnicodeText)
    creator = Column(Integer, ForeignKey(User.id), nullable=False)
    items = Column(Integer, default=0)

class CollectionItem_v0(declarative_base()):
    __tablename__ = "core__collection_items"

    id = Column(Integer, primary_key=True)
    media_entry = Column(
        Integer, ForeignKey(MediaEntry.id), nullable=False, index=True)
    collection = Column(Integer, ForeignKey(Collection.id), nullable=False)
    note = Column(UnicodeText, nullable=True)
    added = Column(DateTime, nullable=False, default=datetime.datetime.now)
    position = Column(Integer)

    ## This should be activated, normally.
    ## But this would change the way the next migration used to work.
    ## So it's commented for now.
    __table_args__ = (
        UniqueConstraint('collection', 'media_entry'),
        {})

collectionitem_unique_constraint_done = False

@RegisterMigration(4, MIGRATIONS)
def add_collection_tables(db_conn):
    Collection_v0.__table__.create(db_conn.bind)
    CollectionItem_v0.__table__.create(db_conn.bind)

    global collectionitem_unique_constraint_done
    collectionitem_unique_constraint_done = True

    db_conn.commit()


@RegisterMigration(5, MIGRATIONS)
def add_mediaentry_collected(db_conn):
    metadata = MetaData(bind=db_conn.bind)

    media_entry = inspect_table(metadata, 'core__media_entries')

    col = Column('collected', Integer, default=0)
    col.create(media_entry)
    db_conn.commit()


class ProcessingMetaData_v0(declarative_base()):
    __tablename__ = 'core__processing_metadata'

    id = Column(Integer, primary_key=True)
    media_entry_id = Column(Integer, ForeignKey(MediaEntry.id), nullable=False,
            index=True)
    callback_url = Column(Unicode)

@RegisterMigration(6, MIGRATIONS)
def create_processing_metadata_table(db):
    ProcessingMetaData_v0.__table__.create(db.bind)
    db.commit()


# Okay, problem being:
#  Migration #4 forgot to add the uniqueconstraint for the
#  new tables. While creating the tables from scratch had
#  the constraint enabled.
#
# So we have four situations that should end up at the same
# db layout:
#
# 1. Fresh install.
#    Well, easy. Just uses the tables in models.py
# 2. Fresh install using a git version just before this migration
#    The tables are all there, the unique constraint is also there.
#    This migration should do nothing.
#    But as we can't detect the uniqueconstraint easily,
#    this migration just adds the constraint again.
#    And possibly fails very loud. But ignores the failure.
# 3. old install, not using git, just releases.
#    This one will get the new tables in #4 (now with constraint!)
#    And this migration is just skipped silently.
# 4. old install, always on latest git.
#    This one has the tables, but lacks the constraint.
#    So this migration adds the constraint.
@RegisterMigration(7, MIGRATIONS)
def fix_CollectionItem_v0_constraint(db_conn):
    """Add the forgotten Constraint on CollectionItem"""

    global collectionitem_unique_constraint_done
    if collectionitem_unique_constraint_done:
        # Reset it. Maybe the whole thing gets run again
        # For a different db?
        collectionitem_unique_constraint_done = False
        return

    metadata = MetaData(bind=db_conn.bind)

    CollectionItem_table = inspect_table(metadata, 'core__collection_items')

    constraint = UniqueConstraint('collection', 'media_entry',
        name='core__collection_items_collection_media_entry_key',
        table=CollectionItem_table)

    try:
        constraint.create()
    except ProgrammingError:
        # User probably has an install that was run since the
        # collection tables were added, so we don't need to run this migration.
        pass

    db_conn.commit()


@RegisterMigration(8, MIGRATIONS)
def add_license_preference(db):
    metadata = MetaData(bind=db.bind)

    user_table = inspect_table(metadata, 'core__users')

    col = Column('license_preference', Unicode)
    col.create(user_table)
    db.commit()


@RegisterMigration(9, MIGRATIONS)
def mediaentry_new_slug_era(db):
    """
    Update for the new era for media type slugs.

    Entries without slugs now display differently in the url like:
      /u/cwebber/m/id=251/

    ... because of this, we should back-convert:
     - entries without slugs should be converted to use the id, if possible, to
       make old urls still work
     - slugs with = (or also : which is now also not allowed) to have those
       stripped out (small possibility of breakage here sadly)
    """

    def slug_and_user_combo_exists(slug, uploader):
        return db.execute(
            media_table.select(
                and_(media_table.c.uploader==uploader,
                     media_table.c.slug==slug))).first() is not None

    def append_garbage_till_unique(row, new_slug):
        """
        Attach junk to this row until it's unique, then save it
        """
        if slug_and_user_combo_exists(new_slug, row.uploader):
            # okay, still no success;
            # let's whack junk on there till it's unique.
            new_slug += '-' + uuid.uuid4().hex[:4]
            # keep going if necessary!
            while slug_and_user_combo_exists(new_slug, row.uploader):
                new_slug += uuid.uuid4().hex[:4]

        db.execute(
            media_table.update(). \
            where(media_table.c.id==row.id). \
            values(slug=new_slug))

    metadata = MetaData(bind=db.bind)

    media_table = inspect_table(metadata, 'core__media_entries')

    for row in db.execute(media_table.select()):
        # no slug, try setting to an id
        if not row.slug:
            append_garbage_till_unique(row, six.text_type(row.id))
        # has "=" or ":" in it... we're getting rid of those
        elif u"=" in row.slug or u":" in row.slug:
            append_garbage_till_unique(
                row, row.slug.replace(u"=", u"-").replace(u":", u"-"))

    db.commit()


@RegisterMigration(10, MIGRATIONS)
def unique_collections_slug(db):
    """Add unique constraint to collection slug"""
    metadata = MetaData(bind=db.bind)
    collection_table = inspect_table(metadata, "core__collections")
    existing_slugs = {}
    slugs_to_change = []

    for row in db.execute(collection_table.select()):
        # if duplicate slug, generate a unique slug
        if row.creator in existing_slugs and row.slug in \
           existing_slugs[row.creator]:
            slugs_to_change.append(row.id)
        else:
            if not row.creator in existing_slugs:
                existing_slugs[row.creator] = [row.slug]
            else:
                existing_slugs[row.creator].append(row.slug)

    for row_id in slugs_to_change:
        new_slug = six.text_type(uuid.uuid4())
        db.execute(collection_table.update().
                   where(collection_table.c.id == row_id).
                   values(slug=new_slug))
    # sqlite does not like to change the schema when a transaction(update) is
    # not yet completed
    db.commit()

    constraint = UniqueConstraint('creator', 'slug',
                                  name='core__collection_creator_slug_key',
                                  table=collection_table)
    constraint.create()

    db.commit()

@RegisterMigration(11, MIGRATIONS)
def drop_token_related_User_columns(db):
    """
    Drop unneeded columns from the User table after switching to using
    itsdangerous tokens for email and forgot password verification.
    """
    metadata = MetaData(bind=db.bind)
    user_table = inspect_table(metadata, 'core__users')

    verification_key = user_table.columns['verification_key']
    fp_verification_key = user_table.columns['fp_verification_key']
    fp_token_expire = user_table.columns['fp_token_expire']

    verification_key.drop()
    fp_verification_key.drop()
    fp_token_expire.drop()

    db.commit()


class CommentSubscription_v0(declarative_base()):
    __tablename__ = 'core__comment_subscriptions'
    id = Column(Integer, primary_key=True)

    created = Column(DateTime, nullable=False, default=datetime.datetime.now)

    media_entry_id = Column(Integer, ForeignKey(MediaEntry.id), nullable=False)

    user_id = Column(Integer, ForeignKey(User.id), nullable=False)

    notify = Column(Boolean, nullable=False, default=True)
    send_email = Column(Boolean, nullable=False, default=True)


class Notification_v0(declarative_base()):
    __tablename__ = 'core__notifications'
    id = Column(Integer, primary_key=True)
    type = Column(Unicode)

    created = Column(DateTime, nullable=False, default=datetime.datetime.now)

    user_id = Column(Integer, ForeignKey(User.id), nullable=False,
                     index=True)
    seen = Column(Boolean, default=lambda: False, index=True)


class CommentNotification_v0(Notification_v0):
    __tablename__ = 'core__comment_notifications'
    id = Column(Integer, ForeignKey(Notification_v0.id), primary_key=True)

    subject_id = Column(Integer, ForeignKey(Comment.id))


class ProcessingNotification_v0(Notification_v0):
    __tablename__ = 'core__processing_notifications'

    id = Column(Integer, ForeignKey(Notification_v0.id), primary_key=True)

    subject_id = Column(Integer, ForeignKey(MediaEntry.id))


@RegisterMigration(12, MIGRATIONS)
def add_new_notification_tables(db):
    metadata = MetaData(bind=db.bind)

    user_table = inspect_table(metadata, 'core__users')
    mediaentry_table = inspect_table(metadata, 'core__media_entries')
    mediacomment_table = inspect_table(metadata, 'core__media_comments')

    CommentSubscription_v0.__table__.create(db.bind)

    Notification_v0.__table__.create(db.bind)
    CommentNotification_v0.__table__.create(db.bind)
    ProcessingNotification_v0.__table__.create(db.bind)

    db.commit()


@RegisterMigration(13, MIGRATIONS)
def pw_hash_nullable(db):
    """Make pw_hash column nullable"""
    metadata = MetaData(bind=db.bind)
    user_table = inspect_table(metadata, "core__users")

    user_table.c.pw_hash.alter(nullable=True)

    # sqlite+sqlalchemy seems to drop this constraint during the
    # migration, so we add it back here for now a bit manually.
    if db.bind.url.drivername == 'sqlite':
        constraint = UniqueConstraint('username', table=user_table)
        constraint.create()

    db.commit()


# oauth1 migrations
class Client_v0(declarative_base()):
    """
        Model representing a client - Used for API Auth
    """
    __tablename__ = "core__clients"

    id = Column(Unicode, nullable=True, primary_key=True)
    secret = Column(Unicode, nullable=False)
    expirey = Column(DateTime, nullable=True)
    application_type = Column(Unicode, nullable=False)
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    updated = Column(DateTime, nullable=False, default=datetime.datetime.now)

    # optional stuff
    redirect_uri = Column(JSONEncoded, nullable=True)
    logo_url = Column(Unicode, nullable=True)
    application_name = Column(Unicode, nullable=True)
    contacts = Column(JSONEncoded, nullable=True)

    def __repr__(self):
        if self.application_name:
            return "<Client {0} - {1}>".format(self.application_name, self.id)
        else:
            return "<Client {0}>".format(self.id)

class RequestToken_v0(declarative_base()):
    """
        Model for representing the request tokens
    """
    __tablename__ = "core__request_tokens"

    token = Column(Unicode, primary_key=True)
    secret = Column(Unicode, nullable=False)
    client = Column(Unicode, ForeignKey(Client_v0.id))
    user = Column(Integer, ForeignKey(User.id), nullable=True)
    used = Column(Boolean, default=False)
    authenticated = Column(Boolean, default=False)
    verifier = Column(Unicode, nullable=True)
    callback = Column(Unicode, nullable=False, default=u"oob")
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    updated = Column(DateTime, nullable=False, default=datetime.datetime.now)

class AccessToken_v0(declarative_base()):
    """
        Model for representing the access tokens
    """
    __tablename__ = "core__access_tokens"

    token = Column(Unicode, nullable=False, primary_key=True)
    secret = Column(Unicode, nullable=False)
    user = Column(Integer, ForeignKey(User.id))
    request_token = Column(Unicode, ForeignKey(RequestToken_v0.token))
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    updated = Column(DateTime, nullable=False, default=datetime.datetime.now)


class NonceTimestamp_v0(declarative_base()):
    """
        A place the timestamp and nonce can be stored - this is for OAuth1
    """
    __tablename__ = "core__nonce_timestamps"

    nonce = Column(Unicode, nullable=False, primary_key=True)
    timestamp = Column(DateTime, nullable=False, primary_key=True)


@RegisterMigration(14, MIGRATIONS)
def create_oauth1_tables(db):
    """ Creates the OAuth1 tables """

    Client_v0.__table__.create(db.bind)
    RequestToken_v0.__table__.create(db.bind)
    AccessToken_v0.__table__.create(db.bind)
    NonceTimestamp_v0.__table__.create(db.bind)

    db.commit()

@RegisterMigration(15, MIGRATIONS)
def wants_notifications(db):
    """Add a wants_notifications field to User model"""
    metadata = MetaData(bind=db.bind)
    user_table = inspect_table(metadata, "core__users")
    col = Column('wants_notifications', Boolean, default=True)
    col.create(user_table)
    db.commit()



@RegisterMigration(16, MIGRATIONS)
def upload_limits(db):
    """Add user upload limit columns"""
    metadata = MetaData(bind=db.bind)

    user_table = inspect_table(metadata, 'core__users')
    media_entry_table = inspect_table(metadata, 'core__media_entries')

    col = Column('uploaded', Integer, default=0)
    col.create(user_table)

    col = Column('upload_limit', Integer)
    col.create(user_table)

    col = Column('file_size', Integer, default=0)
    col.create(media_entry_table)

    db.commit()


@RegisterMigration(17, MIGRATIONS)
def add_file_metadata(db):
    """Add file_metadata to MediaFile"""
    metadata = MetaData(bind=db.bind)
    media_file_table = inspect_table(metadata, "core__mediafiles")

    col = Column('file_metadata', MutationDict.as_mutable(JSONEncoded))
    col.create(media_file_table)

    db.commit()

###################
# Moderation tables
###################

class ReportBase_v0(declarative_base()):
    __tablename__ = 'core__reports'
    id = Column(Integer, primary_key=True)
    reporter_id = Column(Integer, ForeignKey(User.id), nullable=False)
    report_content = Column(UnicodeText)
    reported_user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    discriminator = Column('type', Unicode(50))
    resolver_id = Column(Integer, ForeignKey(User.id))
    resolved = Column(DateTime)
    result = Column(UnicodeText)
    __mapper_args__ = {'polymorphic_on': discriminator}


class CommentReport_v0(ReportBase_v0):
    __tablename__ = 'core__reports_on_comments'
    __mapper_args__ = {'polymorphic_identity': 'comment_report'}

    id = Column('id',Integer, ForeignKey('core__reports.id'),
                                                primary_key=True)
    comment_id = Column(Integer, ForeignKey(Comment.id), nullable=True)


class MediaReport_v0(ReportBase_v0):
    __tablename__ = 'core__reports_on_media'
    __mapper_args__ = {'polymorphic_identity': 'media_report'}

    id = Column('id',Integer, ForeignKey('core__reports.id'), primary_key=True)
    media_entry_id = Column(Integer, ForeignKey(MediaEntry.id), nullable=True)


class UserBan_v0(declarative_base()):
    __tablename__ = 'core__user_bans'
    user_id = Column(Integer, ForeignKey(User.id), nullable=False,
                                         primary_key=True)
    expiration_date = Column(Date)
    reason = Column(UnicodeText, nullable=False)


class Privilege_v0(declarative_base()):
    __tablename__ = 'core__privileges'
    id = Column(Integer, nullable=False, primary_key=True, unique=True)
    privilege_name = Column(Unicode, nullable=False, unique=True)


class PrivilegeUserAssociation_v0(declarative_base()):
    __tablename__ = 'core__privileges_users'
    privilege_id = Column(
        'core__privilege_id',
        Integer,
        ForeignKey(User.id),
        primary_key=True)
    user_id = Column(
        'core__user_id',
        Integer,
        ForeignKey(Privilege.id),
        primary_key=True)


PRIVILEGE_FOUNDATIONS_v0 = [{'privilege_name':u'admin'},
                            {'privilege_name':u'moderator'},
                            {'privilege_name':u'uploader'},
                            {'privilege_name':u'reporter'},
                            {'privilege_name':u'commenter'},
                            {'privilege_name':u'active'}]

# vR1 stands for "version Rename 1".  This only exists because we need
# to deal with dropping some booleans and it's otherwise impossible
# with sqlite.

class User_vR1(declarative_base()):
    __tablename__ = 'rename__users'
    id = Column(Integer, primary_key=True)
    username = Column(Unicode, nullable=False, unique=True)
    email = Column(Unicode, nullable=False)
    pw_hash = Column(Unicode)
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    wants_comment_notification = Column(Boolean, default=True)
    wants_notifications = Column(Boolean, default=True)
    license_preference = Column(Unicode)
    url = Column(Unicode)
    bio = Column(UnicodeText)  # ??
    uploaded = Column(Integer, default=0)
    upload_limit = Column(Integer)


@RegisterMigration(18, MIGRATIONS)
def create_moderation_tables(db):

    # First, we will create the new tables in the database.
    #--------------------------------------------------------------------------
    ReportBase_v0.__table__.create(db.bind)
    CommentReport_v0.__table__.create(db.bind)
    MediaReport_v0.__table__.create(db.bind)
    UserBan_v0.__table__.create(db.bind)
    Privilege_v0.__table__.create(db.bind)
    PrivilegeUserAssociation_v0.__table__.create(db.bind)

    db.commit()

    # Then initialize the tables that we will later use
    #--------------------------------------------------------------------------
    metadata = MetaData(bind=db.bind)
    privileges_table= inspect_table(metadata, "core__privileges")
    user_table = inspect_table(metadata, 'core__users')
    user_privilege_assoc = inspect_table(
        metadata, 'core__privileges_users')

    # This section initializes the default Privilege foundations, that
    # would be created through the FOUNDATIONS system in a new instance
    #--------------------------------------------------------------------------
    for parameters in PRIVILEGE_FOUNDATIONS_v0:
        db.execute(privileges_table.insert().values(**parameters))

    db.commit()

    # This next section takes the information from the old is_admin and status
    # columns and converts those to the new privilege system
    #--------------------------------------------------------------------------
    admin_users_ids, active_users_ids, inactive_users_ids = (
        db.execute(
            user_table.select().where(
                user_table.c.is_admin==True)).fetchall(),
        db.execute(
            user_table.select().where(
                user_table.c.is_admin==False).where(
                user_table.c.status==u"active")).fetchall(),
        db.execute(
            user_table.select().where(
                user_table.c.is_admin==False).where(
                user_table.c.status!=u"active")).fetchall())

    # Get the ids for each of the privileges so we can reference them ~~~~~~~~~
    (admin_privilege_id, uploader_privilege_id,
     reporter_privilege_id, commenter_privilege_id,
     active_privilege_id) = [
        db.execute(privileges_table.select().where(
            privileges_table.c.privilege_name==privilege_name)).first()['id']
        for privilege_name in
            [u"admin",u"uploader",u"reporter",u"commenter",u"active"]
    ]

    # Give each user the appopriate privileges depending whether they are an
    # admin, an active user or an inactive user ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    for admin_user in admin_users_ids:
        admin_user_id = admin_user['id']
        for privilege_id in [admin_privilege_id, uploader_privilege_id,
                            reporter_privilege_id, commenter_privilege_id,
                            active_privilege_id]:
            db.execute(user_privilege_assoc.insert().values(
                core__privilege_id=admin_user_id,
                core__user_id=privilege_id))

    for active_user in active_users_ids:
        active_user_id = active_user['id']
        for privilege_id in [uploader_privilege_id, reporter_privilege_id,
                            commenter_privilege_id, active_privilege_id]:
            db.execute(user_privilege_assoc.insert().values(
                core__privilege_id=active_user_id,
                core__user_id=privilege_id))

    for inactive_user in inactive_users_ids:
        inactive_user_id = inactive_user['id']
        for privilege_id in [uploader_privilege_id, reporter_privilege_id,
                             commenter_privilege_id]:
            db.execute(user_privilege_assoc.insert().values(
                core__privilege_id=inactive_user_id,
                core__user_id=privilege_id))

    db.commit()

    # And then, once the information is taken from is_admin & status columns
    # we drop all of the vestigial columns from the User table.
    #--------------------------------------------------------------------------
    if db.bind.url.drivername == 'sqlite':
        # SQLite has some issues that make it *impossible* to drop boolean
        # columns. So, the following code is a very hacky workaround which
        # makes it possible. ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        User_vR1.__table__.create(db.bind)
        db.commit()
        new_user_table = inspect_table(metadata, 'rename__users')
        replace_table_hack(db, user_table, new_user_table)
    else:
        # If the db is not run using SQLite, this process is much simpler ~~~~~

        status = user_table.columns['status']
        email_verified = user_table.columns['email_verified']
        is_admin = user_table.columns['is_admin']
        status.drop()
        email_verified.drop()
        is_admin.drop()

    db.commit()


@RegisterMigration(19, MIGRATIONS)
def drop_MediaEntry_collected(db):
    """
    Drop unused MediaEntry.collected column
    """
    metadata = MetaData(bind=db.bind)

    media_collected= inspect_table(metadata, 'core__media_entries')
    media_collected = media_collected.columns['collected']

    media_collected.drop()

    db.commit()


@RegisterMigration(20, MIGRATIONS)
def add_metadata_column(db):
    metadata = MetaData(bind=db.bind)

    media_entry = inspect_table(metadata, 'core__media_entries')

    col = Column('media_metadata', MutationDict.as_mutable(JSONEncoded),
        default=MutationDict())
    col.create(media_entry)

    db.commit()


class PrivilegeUserAssociation_R1(declarative_base()):
    __tablename__ = 'rename__privileges_users'
    user = Column(
        "user",
        Integer,
        ForeignKey(User.id),
        primary_key=True)
    privilege = Column(
        "privilege",
        Integer,
        ForeignKey(Privilege.id),
        primary_key=True)

@RegisterMigration(21, MIGRATIONS)
def fix_privilege_user_association_table(db):
    """
    There was an error in the PrivilegeUserAssociation table that allowed for a
    dangerous sql error. We need to the change the name of the columns to be
    unique, and properly referenced.
    """
    metadata = MetaData(bind=db.bind)

    privilege_user_assoc = inspect_table(
        metadata, 'core__privileges_users')

    # This whole process is more complex if we're dealing with sqlite
    if db.bind.url.drivername == 'sqlite':
        PrivilegeUserAssociation_R1.__table__.create(db.bind)
        db.commit()

        new_privilege_user_assoc = inspect_table(
            metadata, 'rename__privileges_users')
        result = db.execute(privilege_user_assoc.select())
        for row in result:
            # The columns were improperly named before, so we switch the columns
            user_id, priv_id = row['core__privilege_id'], row['core__user_id']
            db.execute(new_privilege_user_assoc.insert().values(
                user=user_id,
                privilege=priv_id))

        db.commit()

        privilege_user_assoc.drop()
        new_privilege_user_assoc.rename('core__privileges_users')

    # much simpler if postgres though!
    else:
        privilege_user_assoc.c.core__user_id.alter(name="privilege")
        privilege_user_assoc.c.core__privilege_id.alter(name="user")

    db.commit()


@RegisterMigration(22, MIGRATIONS)
def add_index_username_field(db):
    """
    This migration has been found to be doing the wrong thing.  See
    the documentation in migration 23 (revert_username_index) below
    which undoes this for those databases that did run this migration.

    Old description:
      This indexes the User.username field which is frequently queried
      for example a user logging in. This solves the issue #894
    """
    ## This code is left commented out *on purpose!*
    ##
    ## We do not normally allow commented out code like this in
    ## MediaGoblin but this is a special case: since this migration has
    ## been nullified but with great work to set things back below,
    ## this is commented out for historical clarity.
    #
    # metadata = MetaData(bind=db.bind)
    # user_table = inspect_table(metadata, "core__users")
    #
    # new_index = Index("ix_core__users_uploader", user_table.c.username)
    # new_index.create()
    #
    # db.commit()
    pass


@RegisterMigration(23, MIGRATIONS)
def revert_username_index(db):
    """
    Revert the stuff we did in migration 22 above.

    There were a couple of problems with what we did:
     - There was never a need for this migration!  The unique
       constraint had an implicit b-tree index, so it wasn't really
       needed.  (This is my (Chris Webber's) fault for suggesting it
       needed to happen without knowing what's going on... my bad!)
     - On top of that, databases created after the models.py was
       changed weren't the same as those that had been run through
       migration 22 above.

    As such, we're setting things back to the way they were before,
    but as it turns out, that's tricky to do!
    """
    metadata = MetaData(bind=db.bind)
    user_table = inspect_table(metadata, "core__users")
    indexes = dict(
        [(index.name, index) for index in user_table.indexes])

    # index from unnecessary migration
    users_uploader_index = indexes.get(u'ix_core__users_uploader')
    # index created from models.py after (unique=True, index=True)
    # was set in models.py
    users_username_index = indexes.get(u'ix_core__users_username')

    if users_uploader_index is None and users_username_index is None:
        # We don't need to do anything.
        # The database isn't in a state where it needs fixing
        #
        # (ie, either went through the previous borked migration or
        #  was initialized with a models.py where core__users was both
        #  unique=True and index=True)
        return

    if db.bind.url.drivername == 'sqlite':
        # Again, sqlite has problems.  So this is tricky.

        # Yes, this is correct to use User_vR1!  Nothing has changed
        # between the *correct* version of this table and migration 18.
        User_vR1.__table__.create(db.bind)
        db.commit()
        new_user_table = inspect_table(metadata, 'rename__users')
        replace_table_hack(db, user_table, new_user_table)

    else:
        # If the db is not run using SQLite, we don't need to do crazy
        # table copying.

        # Remove whichever of the not-used indexes are in place
        if users_uploader_index is not None:
            users_uploader_index.drop()
        if users_username_index is not None:
            users_username_index.drop()

        # Given we're removing indexes then adding a unique constraint
        # which *we know might fail*, thus probably rolling back the
        # session, let's commit here.
        db.commit()

        try:
            # Add the unique constraint
            constraint = UniqueConstraint(
                'username', table=user_table)
            constraint.create()
        except ProgrammingError:
            # constraint already exists, no need to add
            db.rollback()

    db.commit()

class Generator_R0(declarative_base()):
    __tablename__ = "core__generators"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode, nullable=False)
    published = Column(DateTime, nullable=False, default=datetime.datetime.now)
    updated = Column(DateTime, nullable=False, default=datetime.datetime.now)
    object_type = Column(Unicode, nullable=False)

class ActivityIntermediator_R0(declarative_base()):
    __tablename__ = "core__activity_intermediators"
    id = Column(Integer, primary_key=True)
    type = Column(Unicode, nullable=False)

    # These are needed for migration 29
    TABLENAMES = {
        "user": "core__users",
        "media": "core__media_entries",
        "comment": "core__media_comments",
        "collection": "core__collections",
    }

class Activity_R0(declarative_base()):
    __tablename__ = "core__activities"
    id = Column(Integer, primary_key=True)
    actor = Column(Integer, ForeignKey(User.id), nullable=False)
    published = Column(DateTime, nullable=False, default=datetime.datetime.now)
    updated = Column(DateTime, nullable=False, default=datetime.datetime.now)
    verb = Column(Unicode, nullable=False)
    content = Column(Unicode, nullable=True)
    title = Column(Unicode, nullable=True)
    generator = Column(Integer, ForeignKey(Generator_R0.id), nullable=True)
    object = Column(Integer,
                    ForeignKey(ActivityIntermediator_R0.id),
                    nullable=False)
    target = Column(Integer,
                    ForeignKey(ActivityIntermediator_R0.id),
                    nullable=True)


@RegisterMigration(24, MIGRATIONS)
def activity_migration(db):
    """
    Creates everything to create activities in GMG
    - Adds Activity, ActivityIntermediator and Generator table
    - Creates GMG service generator for activities produced by the server
    - Adds the activity_as_object and activity_as_target to objects/targets
    - Retroactively adds activities for what we can acurately work out
    """
    # Set constants we'll use later
    FOREIGN_KEY = "core__activity_intermediators.id"
    ACTIVITY_COLUMN = "activity"

    # Create the new tables.
    ActivityIntermediator_R0.__table__.create(db.bind)
    Generator_R0.__table__.create(db.bind)
    Activity_R0.__table__.create(db.bind)
    db.commit()

    # Initiate the tables we want to use later
    metadata = MetaData(bind=db.bind)
    user_table = inspect_table(metadata, "core__users")
    activity_table = inspect_table(metadata, "core__activities")
    generator_table = inspect_table(metadata, "core__generators")
    collection_table = inspect_table(metadata, "core__collections")
    media_entry_table = inspect_table(metadata, "core__media_entries")
    media_comments_table = inspect_table(metadata, "core__media_comments")
    ai_table = inspect_table(metadata, "core__activity_intermediators")


    # Create the foundations for Generator
    db.execute(generator_table.insert().values(
        name="GNU Mediagoblin",
        object_type="service",
        published=datetime.datetime.now(),
        updated=datetime.datetime.now()
    ))
    db.commit()

    # Get the ID of that generator
    gmg_generator = db.execute(generator_table.select(
        generator_table.c.name==u"GNU Mediagoblin")).first()


    # Now we want to modify the tables which MAY have an activity at some point
    media_col = Column(ACTIVITY_COLUMN, Integer, ForeignKey(FOREIGN_KEY))
    media_col.create(media_entry_table)

    user_col = Column(ACTIVITY_COLUMN, Integer, ForeignKey(FOREIGN_KEY))
    user_col.create(user_table)

    comments_col = Column(ACTIVITY_COLUMN, Integer, ForeignKey(FOREIGN_KEY))
    comments_col.create(media_comments_table)

    collection_col = Column(ACTIVITY_COLUMN, Integer, ForeignKey(FOREIGN_KEY))
    collection_col.create(collection_table)
    db.commit()


    # Now we want to retroactively add what activities we can
    # first we'll add activities when people uploaded media.
    # these can't have content as it's not fesible to get the
    # correct content strings.
    for media in db.execute(media_entry_table.select()):
        # Now we want to create the intermedaitory
        db_ai = db.execute(ai_table.insert().values(
            type="media",
        ))
        db_ai = db.execute(ai_table.select(
            ai_table.c.id==db_ai.inserted_primary_key[0]
        )).first()

        # Add the activity
        activity = {
            "verb": "create",
            "actor": media.uploader,
            "published": media.created,
            "updated": media.created,
            "generator": gmg_generator.id,
            "object": db_ai.id
        }
        db.execute(activity_table.insert().values(**activity))

        # Add the AI to the media.
        db.execute(media_entry_table.update().values(
            activity=db_ai.id
        ).where(media_entry_table.c.id==media.id))

    # Now we want to add all the comments people made
    for comment in db.execute(media_comments_table.select()):
        # Get the MediaEntry for the comment
        media_entry = db.execute(
            media_entry_table.select(
                media_entry_table.c.id==comment.media_entry
        )).first()

        # Create an AI for target
        db_ai_media = db.execute(ai_table.select(
            ai_table.c.id==media_entry.activity
        )).first().id

        db.execute(
            media_comments_table.update().values(
                activity=db_ai_media
        ).where(media_comments_table.c.id==media_entry.id))

        # Now create the AI for the comment
        db_ai_comment = db.execute(ai_table.insert().values(
            type="comment"
        )).inserted_primary_key[0]

        activity = {
            "verb": "comment",
            "actor": comment.author,
            "published": comment.created,
            "updated": comment.created,
            "generator": gmg_generator.id,
            "object": db_ai_comment,
            "target": db_ai_media,
        }

        # Now add the comment object
        db.execute(activity_table.insert().values(**activity))

        # Now add activity to comment
        db.execute(media_comments_table.update().values(
            activity=db_ai_comment
        ).where(media_comments_table.c.id==comment.id))

    # Create 'create' activities for all collections
    for collection in db.execute(collection_table.select()):
        # create AI
        db_ai = db.execute(ai_table.insert().values(
            type="collection"
        ))
        db_ai = db.execute(ai_table.select(
            ai_table.c.id==db_ai.inserted_primary_key[0]
        )).first()

        # Now add link the collection to the AI
        db.execute(collection_table.update().values(
            activity=db_ai.id
        ).where(collection_table.c.id==collection.id))

        activity = {
            "verb": "create",
            "actor": collection.creator,
            "published": collection.created,
            "updated": collection.created,
            "generator": gmg_generator.id,
            "object": db_ai.id,
        }

        db.execute(activity_table.insert().values(**activity))

        # Now add the activity to the collection
        db.execute(collection_table.update().values(
            activity=db_ai.id
        ).where(collection_table.c.id==collection.id))

    db.commit()

class Location_V0(declarative_base()):
    __tablename__ = "core__locations"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    position = Column(MutationDict.as_mutable(JSONEncoded))
    address = Column(MutationDict.as_mutable(JSONEncoded))

@RegisterMigration(25, MIGRATIONS)
def add_location_model(db):
    """ Add location model """
    metadata = MetaData(bind=db.bind)

    # Create location table
    Location_V0.__table__.create(db.bind)
    db.commit()

    # Inspect the tables we need
    user = inspect_table(metadata, "core__users")
    collections = inspect_table(metadata, "core__collections")
    media_entry = inspect_table(metadata, "core__media_entries")
    media_comments = inspect_table(metadata, "core__media_comments")

    # Now add location support to the various models
    col = Column("location", Integer, ForeignKey(Location_V0.id))
    col.create(user)

    col = Column("location", Integer, ForeignKey(Location_V0.id))
    col.create(collections)

    col = Column("location", Integer, ForeignKey(Location_V0.id))
    col.create(media_entry)

    col = Column("location", Integer, ForeignKey(Location_V0.id))
    col.create(media_comments)

    db.commit()

@RegisterMigration(26, MIGRATIONS)
def datetime_to_utc(db):
    """ Convert datetime stamps to UTC """
    # Get the server's timezone, this is what the database has stored
    server_timezone = dateutil.tz.tzlocal()

    ##
    # Look up all the timestamps and convert them to UTC
    ##
    metadata = MetaData(bind=db.bind)

    def dt_to_utc(dt):
        # Add the current timezone
        dt = dt.replace(tzinfo=server_timezone)

        # Convert to UTC
        return dt.astimezone(pytz.UTC)

    # Convert the User model
    user_table = inspect_table(metadata, "core__users")
    for user in db.execute(user_table.select()):
        db.execute(user_table.update().values(
            created=dt_to_utc(user.created)
        ).where(user_table.c.id==user.id))

    # Convert Client
    client_table = inspect_table(metadata, "core__clients")
    for client in db.execute(client_table.select()):
        db.execute(client_table.update().values(
            created=dt_to_utc(client.created),
            updated=dt_to_utc(client.updated)
        ).where(client_table.c.id==client.id))

    # Convert RequestToken
    rt_table = inspect_table(metadata, "core__request_tokens")
    for request_token in db.execute(rt_table.select()):
        db.execute(rt_table.update().values(
            created=dt_to_utc(request_token.created),
            updated=dt_to_utc(request_token.updated)
        ).where(rt_table.c.token==request_token.token))

    # Convert AccessToken
    at_table = inspect_table(metadata, "core__access_tokens")
    for access_token in db.execute(at_table.select()):
        db.execute(at_table.update().values(
            created=dt_to_utc(access_token.created),
            updated=dt_to_utc(access_token.updated)
        ).where(at_table.c.token==access_token.token))

    # Convert MediaEntry
    media_table = inspect_table(metadata, "core__media_entries")
    for media in db.execute(media_table.select()):
        db.execute(media_table.update().values(
            created=dt_to_utc(media.created)
        ).where(media_table.c.id==media.id))

    # Convert Media Attachment File
    media_attachment_table = inspect_table(metadata, "core__attachment_files")
    for ma in db.execute(media_attachment_table.select()):
        db.execute(media_attachment_table.update().values(
            created=dt_to_utc(ma.created)
        ).where(media_attachment_table.c.id==ma.id))

    # Convert MediaComment
    comment_table = inspect_table(metadata, "core__media_comments")
    for comment in db.execute(comment_table.select()):
        db.execute(comment_table.update().values(
            created=dt_to_utc(comment.created)
        ).where(comment_table.c.id==comment.id))

    # Convert Collection
    collection_table = inspect_table(metadata, "core__collections")
    for collection in db.execute(collection_table.select()):
        db.execute(collection_table.update().values(
            created=dt_to_utc(collection.created)
        ).where(collection_table.c.id==collection.id))

    # Convert Collection Item
    collection_item_table = inspect_table(metadata, "core__collection_items")
    for ci in db.execute(collection_item_table.select()):
        db.execute(collection_item_table.update().values(
            added=dt_to_utc(ci.added)
        ).where(collection_item_table.c.id==ci.id))

    # Convert Comment subscription
    comment_sub = inspect_table(metadata, "core__comment_subscriptions")
    for sub in db.execute(comment_sub.select()):
        db.execute(comment_sub.update().values(
            created=dt_to_utc(sub.created)
        ).where(comment_sub.c.id==sub.id))

    # Convert Notification
    notification_table = inspect_table(metadata, "core__notifications")
    for notification in db.execute(notification_table.select()):
        db.execute(notification_table.update().values(
            created=dt_to_utc(notification.created)
        ).where(notification_table.c.id==notification.id))

    # Convert ReportBase
    reportbase_table = inspect_table(metadata, "core__reports")
    for report in db.execute(reportbase_table.select()):
        db.execute(reportbase_table.update().values(
            created=dt_to_utc(report.created)
        ).where(reportbase_table.c.id==report.id))

    # Convert Generator
    generator_table = inspect_table(metadata, "core__generators")
    for generator in db.execute(generator_table.select()):
        db.execute(generator_table.update().values(
            published=dt_to_utc(generator.published),
            updated=dt_to_utc(generator.updated)
        ).where(generator_table.c.id==generator.id))

    # Convert Activity
    activity_table = inspect_table(metadata, "core__activities")
    for activity in db.execute(activity_table.select()):
        db.execute(activity_table.update().values(
            published=dt_to_utc(activity.published),
            updated=dt_to_utc(activity.updated)
        ).where(activity_table.c.id==activity.id))

    # Commit this to the database
    db.commit()

##
# Migrations to handle migrating from activity specific foreign key to the
# new GenericForeignKey implementations. They have been split up to improve
# readability and minimise errors
##

class GenericModelReference_V0(declarative_base()):
    __tablename__ = "core__generic_model_reference"

    id = Column(Integer, primary_key=True)
    obj_pk = Column(Integer, nullable=False)
    model_type = Column(Unicode, nullable=False)

@RegisterMigration(27, MIGRATIONS)
def create_generic_model_reference(db):
    """ Creates the Generic Model Reference table """
    GenericModelReference_V0.__table__.create(db.bind)
    db.commit()

@RegisterMigration(28, MIGRATIONS)
def add_foreign_key_fields(db):
    """
    Add the fields for GenericForeignKey to the model under temporary name,
    this is so that later a data migration can occur. They will be renamed to
    the origional names.
    """
    metadata = MetaData(bind=db.bind)
    activity_table = inspect_table(metadata, "core__activities")

    # Create column and add to model.
    object_column = Column("temp_object", Integer, ForeignKey(GenericModelReference_V0.id))
    object_column.create(activity_table)

    target_column = Column("temp_target", Integer, ForeignKey(GenericModelReference_V0.id))
    target_column.create(activity_table)

    # Commit this to the database
    db.commit()

@RegisterMigration(29, MIGRATIONS)
def migrate_data_foreign_keys(db):
    """
    This will migrate the data from the old object and target attributes which
    use the old ActivityIntermediator to the new temparay fields which use the
    new GenericForeignKey.
    """

    metadata = MetaData(bind=db.bind)
    activity_table = inspect_table(metadata, "core__activities")
    ai_table = inspect_table(metadata, "core__activity_intermediators")
    gmr_table = inspect_table(metadata, "core__generic_model_reference")

    # Iterate through all activities doing the migration per activity.
    for activity in model_iteration_hack(db, activity_table.select()):
        # First do the "Activity.object" migration to "Activity.temp_object"
        # I need to get the object from the Activity, I can't use the old
        # Activity.get_object as we're in a migration.
        object_ai = db.execute(ai_table.select(
            ai_table.c.id==activity.object
        )).first()

        object_ai_type = ActivityIntermediator_R0.TABLENAMES[object_ai.type]
        object_ai_table = inspect_table(metadata, object_ai_type)

        activity_object = db.execute(object_ai_table.select(
            object_ai_table.c.activity==object_ai.id
        )).first()

        # If the object the activity is referecing doesn't revolve, then we
        # should skip it, it should be deleted when the AI table is deleted.
        if activity_object is None:
            continue

        # now we need to create the GenericModelReference
        object_gmr = db.execute(gmr_table.insert().values(
            obj_pk=activity_object.id,
            model_type=object_ai_type
        ))

        # Now set the ID of the GenericModelReference in the GenericForignKey
        db.execute(activity_table.update().values(
            temp_object=object_gmr.inserted_primary_key[0]
        ))

        # Now do same process for "Activity.target" to "Activity.temp_target"
        # not all Activities have a target so if it doesn't just skip the rest
        # of this.
        if activity.target is None:
            continue

        # Now get the target for the activity.
        target_ai = db.execute(ai_table.select(
            ai_table.c.id==activity.target
        )).first()

        target_ai_type = ActivityIntermediator_R0.TABLENAMES[target_ai.type]
        target_ai_table = inspect_table(metadata, target_ai_type)

        activity_target = db.execute(target_ai_table.select(
            target_ai_table.c.activity==target_ai.id
        )).first()

        # It's quite possible that the target, alike the object could also have
        # been deleted, if so we should just skip it
        if activity_target is None:
            continue

        # We now want to create the new target GenericModelReference
        target_gmr = db.execute(gmr_table.insert().values(
            obj_pk=activity_target.id,
            model_type=target_ai_type
        ))

        # Now set the ID of the GenericModelReference in the GenericForignKey
        db.execute(activity_table.update().values(
            temp_object=target_gmr.inserted_primary_key[0]
        ))

        # Commit to the database. We're doing it here rather than outside the
        # loop because if the server has a lot of data this can cause problems
        db.commit()

@RegisterMigration(30, MIGRATIONS)
def rename_and_remove_object_and_target(db):
    """
    Renames the new Activity.object and Activity.target fields and removes the
    old ones.
    """
    metadata = MetaData(bind=db.bind)
    activity_table = inspect_table(metadata, "core__activities")

    # Firstly lets remove the old fields.
    old_object_column = activity_table.columns["object"]
    old_target_column = activity_table.columns["target"]

    # Drop the tables.
    old_object_column.drop()
    old_target_column.drop()

    # Now get the new columns.
    new_object_column = activity_table.columns["temp_object"]
    new_target_column = activity_table.columns["temp_target"]

    # rename them to the old names.
    new_object_column.alter(name="object_id")
    new_target_column.alter(name="target_id")

    # Commit the changes to the database.
    db.commit()

@RegisterMigration(31, MIGRATIONS)
def remove_activityintermediator(db):
    """
    This removes the old specific ActivityIntermediator model which has been
    superseeded by the GenericForeignKey field.
    """
    metadata = MetaData(bind=db.bind)

    # Remove the columns which reference the AI
    collection_table = inspect_table(metadata, "core__collections")
    collection_ai_column = collection_table.columns["activity"]
    collection_ai_column.drop()

    media_entry_table = inspect_table(metadata, "core__media_entries")
    media_entry_ai_column = media_entry_table.columns["activity"]
    media_entry_ai_column.drop()

    comments_table = inspect_table(metadata, "core__media_comments")
    comments_ai_column = comments_table.columns["activity"]
    comments_ai_column.drop()

    user_table = inspect_table(metadata, "core__users")
    user_ai_column = user_table.columns["activity"]
    user_ai_column.drop()

    # Drop the table
    ai_table = inspect_table(metadata, "core__activity_intermediators")
    ai_table.drop()

    # Commit the changes
    db.commit()

##
# Migrations for converting the User model into a Local and Remote User
# setup.
##

class LocalUser_V0(declarative_base()):
    __tablename__ = "core__local_users"

    id = Column(Integer, ForeignKey(User.id), primary_key=True)
    username = Column(Unicode, nullable=False, unique=True)
    email = Column(Unicode, nullable=False)
    pw_hash = Column(Unicode)

    wants_comment_notification = Column(Boolean, default=True)
    wants_notifications = Column(Boolean, default=True)
    license_preference = Column(Unicode)
    uploaded = Column(Integer, default=0)
    upload_limit = Column(Integer)

class RemoteUser_V0(declarative_base()):
    __tablename__ = "core__remote_users"

    id = Column(Integer, ForeignKey(User.id), primary_key=True)
    webfinger = Column(Unicode, unique=True)

@RegisterMigration(32, MIGRATIONS)
def federation_user_create_tables(db):
    """
    Create all the tables
    """
    # Create tables needed
    LocalUser_V0.__table__.create(db.bind)
    RemoteUser_V0.__table__.create(db.bind)
    db.commit()

    metadata = MetaData(bind=db.bind)
    user_table = inspect_table(metadata, "core__users")

    # Create the fields
    updated_column = Column(
        "updated",
        DateTime,
        default=datetime.datetime.utcnow
    )
    updated_column.create(user_table)

    type_column = Column(
        "type",
        Unicode
    )
    type_column.create(user_table)

    name_column = Column(
        "name",
        Unicode
    )
    name_column.create(user_table)

    db.commit()

@RegisterMigration(33, MIGRATIONS)
def federation_user_migrate_data(db):
    """
    Migrate the data over to the new user models
    """
    metadata = MetaData(bind=db.bind)

    user_table = inspect_table(metadata, "core__users")
    local_user_table = inspect_table(metadata, "core__local_users")

    for user in model_iteration_hack(db, user_table.select()):
        db.execute(local_user_table.insert().values(
            id=user.id,
            username=user.username,
            email=user.email,
            pw_hash=user.pw_hash,
            wants_comment_notification=user.wants_comment_notification,
            wants_notifications=user.wants_notifications,
            license_preference=user.license_preference,
            uploaded=user.uploaded,
            upload_limit=user.upload_limit
        ))

        db.execute(user_table.update().where(user_table.c.id==user.id).values(
            updated=user.created,
            type=LocalUser.__mapper_args__["polymorphic_identity"]
        ))

        db.commit()

class User_vR2(declarative_base()):
    __tablename__ = "rename__users"

    id = Column(Integer, primary_key=True)
    url = Column(Unicode)
    bio = Column(UnicodeText)
    name = Column(Unicode)
    type = Column(Unicode)
    created = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    location = Column(Integer, ForeignKey(Location.id))

@RegisterMigration(34, MIGRATIONS)
def federation_remove_fields(db):
    """
    This removes the fields from User model which aren't shared
    """
    metadata = MetaData(bind=db.bind)

    user_table = inspect_table(metadata, "core__users")

    # Remove the columns moved to LocalUser from User
    username_column = user_table.columns["username"]
    username_column.drop()

    email_column = user_table.columns["email"]
    email_column.drop()

    pw_hash_column = user_table.columns["pw_hash"]
    pw_hash_column.drop()

    license_preference_column = user_table.columns["license_preference"]
    license_preference_column.drop()

    uploaded_column = user_table.columns["uploaded"]
    uploaded_column.drop()

    upload_limit_column = user_table.columns["upload_limit"]
    upload_limit_column.drop()

    # SQLLite can't drop booleans -.-
    if db.bind.url.drivername == 'sqlite':
        # Create the new hacky table
        User_vR2.__table__.create(db.bind)
        db.commit()
        new_user_table = inspect_table(metadata, "rename__users")
        replace_table_hack(db, user_table, new_user_table)
    else:
        wcn_column = user_table.columns["wants_comment_notification"]
        wcn_column.drop()

        wants_notifications_column = user_table.columns["wants_notifications"]
        wants_notifications_column.drop()

    db.commit()

@RegisterMigration(35, MIGRATIONS)
def federation_media_entry(db):
    metadata = MetaData(bind=db.bind)
    media_entry_table = inspect_table(metadata, "core__media_entries")

    # Add new fields
    public_id_column = Column(
        "public_id",
        Unicode,
        unique=True,
        nullable=True
    )
    public_id_column.create(
        media_entry_table,
        unique_name="media_public_id"
    )

    remote_column = Column(
        "remote",
        Boolean,
        default=False
    )
    remote_column.create(media_entry_table)

    updated_column = Column(
        "updated",
        DateTime,
        default=datetime.datetime.utcnow,
    )
    updated_column.create(media_entry_table)
    db.commit()

    # Data migration
    for entry in model_iteration_hack(db, media_entry_table.select()):
        db.execute(media_entry_table.update().values(
            updated=entry.created,
            remote=False
        ))

        db.commit()

@RegisterMigration(36, MIGRATIONS)
def create_oauth1_dummies(db):
    """
    Creates a dummy client, request and access tokens.

    This is used when invalid data is submitted but real clients and
    access tokens. The use of dummy objects prevents timing attacks.
    """
    metadata = MetaData(bind=db.bind)
    client_table = inspect_table(metadata, "core__clients")
    request_token_table = inspect_table(metadata, "core__request_tokens")
    access_token_table = inspect_table(metadata, "core__access_tokens")

    # Whilst we don't rely on the secret key being unique or unknown to prevent
    # unauthorized clients from using it to authenticate, we still as an extra
    # layer of protection created a cryptographically secure key individual to
    # each instance that should never be able to be known.
    client_secret = crypto.random_string(50)
    request_token_secret = crypto.random_string(50)
    request_token_verifier = crypto.random_string(50)
    access_token_secret = crypto.random_string(50)

    # Dummy created/updated datetime object
    epoc_datetime = datetime.datetime.fromtimestamp(0)

    # Create the dummy Client
    db.execute(client_table.insert().values(
        id=oauth.DUMMY_CLIENT_ID,
        secret=client_secret,
        application_type="dummy",
        created=epoc_datetime,
        updated=epoc_datetime
    ))

    # Create the dummy RequestToken
    db.execute(request_token_table.insert().values(
        token=oauth.DUMMY_REQUEST_TOKEN,
        secret=request_token_secret,
        client=oauth.DUMMY_CLIENT_ID,
        verifier=request_token_verifier,
        created=epoc_datetime,
        updated=epoc_datetime,
        callback="oob"
    ))

    # Create the dummy AccessToken
    db.execute(access_token_table.insert().values(
        token=oauth.DUMMY_ACCESS_TOKEN,
        secret=access_token_secret,
        request_token=oauth.DUMMY_REQUEST_TOKEN,
        created=epoc_datetime,
        updated=epoc_datetime
    ))

    # Commit the changes
    db.commit()

@RegisterMigration(37, MIGRATIONS)
def federation_collection_schema(db):
    """ Converts the Collection and CollectionItem """
    metadata = MetaData(bind=db.bind)
    collection_table = inspect_table(metadata, "core__collections")
    collection_items_table = inspect_table(metadata, "core__collection_items")
    media_entry_table = inspect_table(metadata, "core__media_entries")
    gmr_table = inspect_table(metadata, "core__generic_model_reference")

    ##
    # Collection Table
    ##

    # Add the fields onto the Collection model, we need to set these as
    # not null to avoid DB integreity errors. We will add the not null
    # constraint later.
    public_id_column = Column(
        "public_id",
        Unicode,
        unique=True
    )
    public_id_column.create(
        collection_table,
        unique_name="collection_public_id")

    updated_column = Column(
        "updated",
        DateTime,
        default=datetime.datetime.utcnow
    )
    updated_column.create(collection_table)

    type_column = Column(
        "type",
        Unicode,
    )
    type_column.create(collection_table)

    db.commit()

    # Iterate over the items and set the updated and type fields
    for collection in db.execute(collection_table.select()):
        db.execute(collection_table.update().where(
            collection_table.c.id==collection.id
        ).values(
            updated=collection.created,
            type="core-user-defined"
        ))

    db.commit()

    # Add the not null constraint onto the fields
    updated_column = collection_table.columns["updated"]
    updated_column.alter(nullable=False)

    type_column = collection_table.columns["type"]
    type_column.alter(nullable=False)

    db.commit()

    # Rename the "items" to "num_items" as per the TODO
    num_items_field = collection_table.columns["items"]
    num_items_field.alter(name="num_items")
    db.commit()

    ##
    # CollectionItem
    ##
    # Adding the object ID column, this again will have not null added later.
    object_id = Column(
        "object_id",
        Integer,
        ForeignKey(GenericModelReference_V0.id),
    )
    object_id.create(
        collection_items_table,
    )

    db.commit()

    # Iterate through and convert the Media reference to object_id
    for item in db.execute(collection_items_table.select()):
        # Check if there is a GMR for the MediaEntry
        object_gmr = db.execute(gmr_table.select(
            and_(
                gmr_table.c.obj_pk == item.media_entry,
                gmr_table.c.model_type == "core__media_entries"
            )
        )).first()

        if object_gmr:
            object_gmr = object_gmr[0]
        else:
            # Create a GenericModelReference
            object_gmr = db.execute(gmr_table.insert().values(
                obj_pk=item.media_entry,
                model_type="core__media_entries"
            )).inserted_primary_key[0]

        # Now set the object_id column to the ID of the GMR
        db.execute(collection_items_table.update().where(
            collection_items_table.c.id==item.id
        ).values(
            object_id=object_gmr
        ))

    db.commit()

    # Add not null constraint
    object_id = collection_items_table.columns["object_id"]
    object_id.alter(nullable=False)

    db.commit()

    # Now remove the old media_entry column
    media_entry_column = collection_items_table.columns["media_entry"]
    media_entry_column.drop()

    db.commit()

@RegisterMigration(38, MIGRATIONS)
def federation_actor(db):
    """ Renames refereces to the user to actor """
    metadata = MetaData(bind=db.bind)

    # RequestToken: user -> actor
    request_token_table = inspect_table(metadata, "core__request_tokens")
    rt_user_column = request_token_table.columns["user"]
    rt_user_column.alter(name="actor")

    # AccessToken: user -> actor
    access_token_table = inspect_table(metadata, "core__access_tokens")
    at_user_column = access_token_table.columns["user"]
    at_user_column.alter(name="actor")

    # MediaEntry: uploader -> actor
    media_entry_table = inspect_table(metadata, "core__media_entries")
    me_user_column = media_entry_table.columns["uploader"]
    me_user_column.alter(name="actor")

    # MediaComment: author -> actor
    media_comment_table = inspect_table(metadata, "core__media_comments")
    mc_user_column = media_comment_table.columns["author"]
    mc_user_column.alter(name="actor")

    # Collection: creator -> actor
    collection_table = inspect_table(metadata, "core__collections")
    mc_user_column = collection_table.columns["creator"]
    mc_user_column.alter(name="actor")

    # commit changes to db.
    db.commit()

class Graveyard_V0(declarative_base()):
    """ Where models come to die """
    __tablename__ = "core__graveyard"

    id = Column(Integer, primary_key=True)
    public_id = Column(Unicode, nullable=True, unique=True)

    deleted = Column(DateTime, nullable=False)
    object_type = Column(Unicode, nullable=False)

    actor_id = Column(Integer, ForeignKey(GenericModelReference_V0.id))

@RegisterMigration(39, MIGRATIONS)
def federation_graveyard(db):
    """ Introduces soft deletion to models

    This adds a Graveyard model which is used to copy (soft-)deleted models to.
    """
    metadata = MetaData(bind=db.bind)

    # Create the graveyard table
    Graveyard_V0.__table__.create(db.bind)

    # Commit changes to the db
    db.commit()

@RegisterMigration(40, MIGRATIONS)
def add_public_id(db):
    metadata = MetaData(bind=db.bind)

    # Get the table
    activity_table = inspect_table(metadata, "core__activities")
    activity_public_id = Column(
        "public_id",
        Unicode,
        unique=True,
        nullable=True
    )
    activity_public_id.create(
        activity_table,
        unique_name="activity_public_id"
    )

    # Commit this.
    db.commit()

class Comment_V0(declarative_base()):
    __tablename__ = "core__comment_links"

    id = Column(Integer, primary_key=True)
    target_id = Column(
        Integer,
        ForeignKey(GenericModelReference_V0.id),
        nullable=False
    )
    comment_id = Column(
        Integer,
        ForeignKey(GenericModelReference_V0.id),
        nullable=False
    )
    added = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
 

@RegisterMigration(41, MIGRATIONS)
def federation_comments(db):
    """
    This reworks the MediaComent to be a more generic Comment model.
    """
    metadata = MetaData(bind=db.bind)
    textcomment_table = inspect_table(metadata, "core__media_comments")
    gmr_table = inspect_table(metadata, "core__generic_model_reference")

    # First of all add the public_id field to the TextComment table
    comment_public_id_column = Column(
        "public_id",
        Unicode,
        unique=True
    )
    comment_public_id_column.create(
        textcomment_table,
        unique_name="public_id_unique"
    )

    comment_updated_column = Column(
        "updated",
        DateTime,
    )
    comment_updated_column.create(textcomment_table)


    # First create the Comment link table.
    Comment_V0.__table__.create(db.bind)
    db.commit()

    # now look up the comment table 
    comment_table = inspect_table(metadata, "core__comment_links")

    # Itierate over all the comments and add them to the link table.
    for comment in db.execute(textcomment_table.select()):
        # Check if there is a GMR to the comment.
        comment_gmr = db.execute(gmr_table.select().where(and_(
            gmr_table.c.obj_pk == comment.id,
            gmr_table.c.model_type == "core__media_comments"
        ))).first()

        if comment_gmr:
            comment_gmr = comment_gmr[0]
        else:
            comment_gmr = db.execute(gmr_table.insert().values(
                obj_pk=comment.id,
                model_type="core__media_comments"
            )).inserted_primary_key[0]

        # Get or create the GMR for the media entry
        entry_gmr = db.execute(gmr_table.select().where(and_(
            gmr_table.c.obj_pk == comment.media_entry,
            gmr_table.c.model_type == "core__media_entries"
        ))).first()

        if entry_gmr:
            entry_gmr = entry_gmr[0]
        else:
            entry_gmr = db.execute(gmr_table.insert().values(
                obj_pk=comment.media_entry,
                model_type="core__media_entries"
            )).inserted_primary_key[0] 

        # Add the comment link.
        db.execute(comment_table.insert().values(
            target_id=entry_gmr,
            comment_id=comment_gmr,
            added=datetime.datetime.utcnow()
        ))

        # Add the data to the updated field
        db.execute(textcomment_table.update().where(
            textcomment_table.c.id == comment.id
        ).values(
            updated=comment.created
        ))
    db.commit()
    
    # Add not null constraint
    textcomment_update_column = textcomment_table.columns["updated"]
    textcomment_update_column.alter(nullable=False)

    # Remove the unused fields on the TextComment model
    comment_media_entry_column = textcomment_table.columns["media_entry"]
    comment_media_entry_column.drop()
    db.commit()

@RegisterMigration(42, MIGRATIONS)
def consolidate_reports(db):
    """ Consolidates the report tables into just one """
    metadata = MetaData(bind=db.bind)

    report_table = inspect_table(metadata, "core__reports")
    comment_report_table = inspect_table(metadata, "core__reports_on_comments")
    media_report_table = inspect_table(metadata, "core__reports_on_media")
    gmr_table = inspect_table(metadata, "core__generic_model_reference")

    # Add the GMR object field onto the base report table
    report_object_id_column = Column(
        "object_id",
        Integer,
        ForeignKey(GenericModelReference_V0.id),
        nullable=True,
    )
    report_object_id_column.create(report_table)
    db.commit()

    # Iterate through the reports in the comment table and merge them in.
    for comment_report in db.execute(comment_report_table.select()):
        # If the comment is None it's been deleted, we should skip
        if comment_report.comment_id is None:
            continue

        # Find a GMR for this if one exists.
        crgmr = db.execute(gmr_table.select().where(and_(
            gmr_table.c.obj_pk == comment_report.comment_id,
            gmr_table.c.model_type == "core__media_comments"
        ))).first()

        if crgmr:
            crgmr = crgmr[0]
        else:
            crgmr = db.execute(gmr_table.insert().values(
                obj_pk=comment_report.comment_id,
                model_type="core__media_comments"
            )).inserted_primary_key[0]

        # Great now we can save this back onto the (base) report.
        db.execute(report_table.update().where(
            report_table.c.id == comment_report.id
        ).values(
            object_id=crgmr
        ))

    # Iterate through the Media Reports and do the save as above.
    for media_report in db.execute(media_report_table.select()):
        # If the media report is None then it's been deleted nd we should skip
        if media_report.media_entry_id is None:
            continue

        # Find Mr. GMR :)
        mrgmr = db.execute(gmr_table.select().where(and_(
            gmr_table.c.obj_pk == media_report.media_entry_id,
            gmr_table.c.model_type == "core__media_entries"
        ))).first()

        if mrgmr:
            mrgmr = mrgmr[0]
        else:
            mrgmr = db.execute(gmr_table.insert().values(
                obj_pk=media_report.media_entry_id,
                model_type="core__media_entries"
            )).inserted_primary_key[0]

        # Save back on to the base.
        db.execute(report_table.update().where(
            report_table.c.id == media_report.id
        ).values(
            object_id=mrgmr
        ))

    db.commit()

    # Now we can remove the fields we don't need anymore
    report_type = report_table.columns["type"]
    report_type.drop()

    # Drop both MediaReports and CommentTable.
    comment_report_table.drop()
    media_report_table.drop()

    # Commit we're done.
    db.commit()

@RegisterMigration(43, MIGRATIONS)
def consolidate_notification(db):
    """ Consolidates the notification models into one """
    metadata = MetaData(bind=db.bind)
    notification_table = inspect_table(metadata, "core__notifications")
    cn_table = inspect_table(metadata, "core__comment_notifications")
    cp_table = inspect_table(metadata, "core__processing_notifications")
    gmr_table = inspect_table(metadata, "core__generic_model_reference")

    # Add fields needed
    notification_object_id_column = Column(
        "object_id",
        Integer,
        ForeignKey(GenericModelReference_V0.id)
    )
    notification_object_id_column.create(notification_table)
    db.commit()

    # Iterate over comments and move to notification base table.
    for comment_notification in db.execute(cn_table.select()):
        # Find the GMR.
        cngmr = db.execute(gmr_table.select().where(and_(
            gmr_table.c.obj_pk == comment_notification.subject_id,
            gmr_table.c.model_type == "core__media_comments"
        ))).first()

        if cngmr:
            cngmr = cngmr[0]
        else:
            cngmr = db.execute(gmr_table.insert().values(
                obj_pk=comment_notification.subject_id,
                model_type="core__media_comments"
            )).inserted_primary_key[0]

        # Save back on notification
        db.execute(notification_table.update().where(
            notification_table.c.id == comment_notification.id
        ).values(
            object_id=cngmr
        ))
    db.commit()

    # Do the same for processing notifications
    for processing_notification in db.execute(cp_table.select()):
        cpgmr = db.execute(gmr_table.select().where(and_(
            gmr_table.c.obj_pk == processing_notification.subject_id,
            gmr_table.c.model_type == "core__processing_notifications"
        ))).first()

        if cpgmr:
            cpgmr = cpgmr[0]
        else:
            cpgmr = db.execute(gmr_table.insert().values(
                obj_pk=processing_notification.subject_id,
                model_type="core__processing_notifications"
            )).inserted_primary_key[0]

        db.execute(notification_table.update().where(
            notification_table.c.id == processing_notification.id
        ).values(
            object_id=cpgmr
        ))
    db.commit()

    # Add the not null constraint
    notification_object_id = notification_table.columns["object_id"]
    notification_object_id.alter(nullable=False)

    # Now drop the fields we don't need
    notification_type_column = notification_table.columns["type"]
    notification_type_column.drop()

    # Drop the tables we no longer need
    cp_table.drop()
    cn_table.drop()

    db.commit()

@RegisterMigration(44, MIGRATIONS)
def activity_cleanup(db):
    """
    This cleans up activities which are broken and have no graveyard object as
    well as removing the not null constraint on Report.object_id as that can
    be null when action has been taken to delete the reported content.

    Some of this has been changed in previous migrations so we need to check
    if there is anything to be done, there might not be. It was fixed as part
    of the #5369 fix. Some past migrations could have broken on some people so
    needed to be fixed then however for some they would have run fine.
    """
    metadata = MetaData(bind=db.bind)
    report_table = inspect_table(metadata, "core__reports")
    activity_table = inspect_table(metadata, "core__activities")
    gmr_table = inspect_table(metadata, "core__generic_model_reference")

    # Remove not null on Report.object_id
    object_id_column = report_table.columns["object_id"]
    if not object_id_column.nullable:
        object_id_column.alter(nullable=False)
    db.commit()

    # Go through each activity and verify the object and if a target is
    # specified both exist.
    for activity in db.execute(activity_table.select()):
        # Get the GMR 
        obj_gmr = db.execute(gmr_table.select().where(
            gmr_table.c.id == activity.object_id,
        )).first()

        # Get the object the GMR points to, might be null.
        obj_table = inspect_table(metadata, obj_gmr.model_type)
        obj = db.execute(obj_table.select().where(
            obj_table.c.id == obj_gmr.obj_pk
        )).first()

        if obj is None:
            # Okay we need to delete the activity and move to the next
            db.execute(activity_table.delete().where(
                activity_table.c.id == activity.id
            ))
            continue

        # If there is a target then check that too, if not that's fine
        if activity.target_id == None:
            continue

        # Okay check the target is valid
        target_gmr = db.execute(gmr_table.select().where(
            gmr_table.c.id == activity.target_id
        )).first()

        target_table = inspect_table(metadata, target_gmr.model_type)
        target = db.execute(target_table.select().where(
            target_table.c.id == target_gmr.obj_pk
        )).first()

        # If it doesn't exist, delete the activity.
        if target is None:
            db.execute(activity_table.delete().where(
                activity_table.c.id == activity.id
            ))
