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


import os
import pkg_resources
import shutil

import six

from paste.deploy import loadapp
from webtest import TestApp

from mediagoblin import mg_globals
from mediagoblin.db.models import User, LocalUser, MediaEntry, Collection, TextComment, \
    CommentSubscription, Notification, Privilege, Report, Client, \
    RequestToken, AccessToken, Activity, Generator, Comment
from mediagoblin.tools import testing
from mediagoblin.init.config import read_mediagoblin_config
from mediagoblin.db.base import Session
from mediagoblin.meddleware import BaseMeddleware
from mediagoblin.auth import gen_password_hash
from mediagoblin.gmg_commands.dbupdate import run_dbupdate
from mediagoblin.tools.crypto import random_string

from datetime import datetime


MEDIAGOBLIN_TEST_DB_NAME = u'__mediagoblin_tests__'
TEST_SERVER_CONFIG = pkg_resources.resource_filename(
    'mediagoblin.tests', 'test_paste.ini')
TEST_APP_CONFIG = pkg_resources.resource_filename(
    'mediagoblin.tests', 'test_mgoblin_app.ini')


USER_DEV_DIRECTORIES_TO_SETUP = ['media/public', 'media/queue']


class TestingMeddleware(BaseMeddleware):
    """
    Meddleware for the Unit tests

    It might make sense to perform some tests on all
    requests/responses. Or prepare them in a special
    manner. For example all html responses could be tested
    for being valid html *after* being rendered.

    This module is getting inserted at the front of the
    meddleware list, which means: requests are handed here
    first, responses last. So this wraps up the "normal"
    app.

    If you need to add a test, either add it directly to
    the appropiate process_request or process_response, or
    create a new method and call it from process_*.
    """

    def process_response(self, request, response):
        # All following tests should be for html only!
        if getattr(response, 'content_type', None) != "text/html":
            # Get out early
            return

        # If the template contains a reference to
        # /mgoblin_static/ instead of using
        # /request.staticdirect(), error out here.
        # This could probably be implemented as a grep on
        # the shipped templates easier...
        if response.text.find("/mgoblin_static/") >= 0:
            raise AssertionError(
                "Response HTML contains reference to /mgoblin_static/ "
                "instead of staticdirect. Request was for: "
                + request.full_path)

        return


def get_app(request, paste_config=None, mgoblin_config=None):
    """Create a MediaGoblin app for testing.

    Args:
     - request: Not an http request, but a pytest fixture request.  We
       use this to make temporary directories that pytest
       automatically cleans up as needed.
     - paste_config: particular paste config used by this application.
     - mgoblin_config: particular mediagoblin config used by this
       application.
    """
    paste_config = paste_config or TEST_SERVER_CONFIG
    mgoblin_config = mgoblin_config or TEST_APP_CONFIG

    # This is the directory we're copying the paste/mgoblin config stuff into
    run_dir = request.config._tmpdirhandler.mktemp(
        'mgoblin_app', numbered=True)
    user_dev_dir = run_dir.mkdir('user_dev').strpath

    new_paste_config = run_dir.join('paste.ini').strpath
    new_mgoblin_config = run_dir.join('mediagoblin.ini').strpath
    shutil.copyfile(paste_config, new_paste_config)
    shutil.copyfile(mgoblin_config, new_mgoblin_config)

    Session.rollback()
    Session.remove()

    # install user_dev directories
    for directory in USER_DEV_DIRECTORIES_TO_SETUP:
        full_dir = os.path.join(user_dev_dir, directory)
        os.makedirs(full_dir)

    # Get app config
    global_config, validation_result = read_mediagoblin_config(new_mgoblin_config)
    app_config = global_config['mediagoblin']

    # Run database setup/migrations
    # @@: The *only* test that doesn't pass if we remove this is in
    #   test_persona.py... why?
    run_dbupdate(app_config, global_config)

    # setup app and return
    test_app = loadapp(
        'config:' + new_paste_config)

    # Insert the TestingMeddleware, which can do some
    # sanity checks on every request/response.
    # Doing it this way is probably not the cleanest way.
    # We'll fix it, when we have plugins!
    mg_globals.app.meddleware.insert(0, TestingMeddleware(mg_globals.app))

    app = TestApp(test_app)
    return app


def install_fixtures_simple(db, fixtures):
    """
    Very simply install fixtures in the database
    """
    for collection_name, collection_fixtures in six.iteritems(fixtures):
        collection = db[collection_name]
        for fixture in collection_fixtures:
            collection.insert(fixture)


def assert_db_meets_expected(db, expected):
    """
    Assert a database contains the things we expect it to.

    Objects are found via 'id', so you should make sure your document
    has an id.

    Args:
     - db: pymongo or mongokit database connection
     - expected: the data we expect.  Formatted like:
         {'collection_name': [
             {'id': 'foo',
              'some_field': 'some_value'},]}
    """
    for collection_name, collection_data in six.iteritems(expected):
        collection = db[collection_name]
        for expected_document in collection_data:
            document = collection.query.filter_by(id=expected_document['id']).first()
            assert document is not None  # make sure it exists
            assert document == expected_document  # make sure it matches


def fixture_add_user(username=u'chris', password=u'toast',
                     privileges=[], wants_comment_notification=True):
    # Reuse existing user or create a new one
    test_user = LocalUser.query.filter(LocalUser.username==username).first()
    if test_user is None:
        test_user = LocalUser()
    test_user.username = username
    test_user.email = username + u'@example.com'
    if password is not None:
        test_user.pw_hash = gen_password_hash(password)
    test_user.wants_comment_notification = wants_comment_notification
    for privilege in privileges:
        query = Privilege.query.filter(Privilege.privilege_name==privilege)
        if query.count():
            test_user.all_privileges.append(query.one())

    test_user.save()

    # Reload - The `with_polymorphic` needs to be there to eagerly load
    # the attributes on the LocalUser as this can't be done post detachment.
    user_query = LocalUser.query.with_polymorphic(LocalUser)
    test_user = user_query.filter(LocalUser.username==username).first()

    # ... and detach from session:
    Session.expunge(test_user)

    return test_user


def fixture_comment_subscription(entry, notify=True, send_email=None):
    if send_email is None:
        actor = LocalUser.query.filter_by(id=entry.actor).first()
        send_email = actor.wants_comment_notification

    cs = CommentSubscription(
        media_entry_id=entry.id,
        user_id=entry.actor,
        notify=notify,
        send_email=send_email)

    cs.save()

    cs = CommentSubscription.query.filter_by(id=cs.id).first()

    Session.expunge(cs)

    return cs


def fixture_add_comment_notification(entry, subject, user,
                                     seen=False):
    cn = Notification(
        user_id=user,
        seen=seen,
    )
    cn.obj = subject
    cn.save()

    cn = Notification.query.filter_by(id=cn.id).first()

    Session.expunge(cn)

    return cn


def fixture_media_entry(title=u"Some title", slug=None,
                        uploader=None, save=True, gen_slug=True,
                        state=u'unprocessed', fake_upload=True,
                        expunge=True):
    """
    Add a media entry for testing purposes.

    Caution: if you're adding multiple entries with fake_upload=True,
    make sure you save between them... otherwise you'll hit an
    IntegrityError from multiple newly-added-MediaEntries adding
    FileKeynames at once.  :)
    """
    if uploader is None:
        uploader = fixture_add_user().id

    entry = MediaEntry()
    entry.title = title
    entry.slug = slug
    entry.actor = uploader
    entry.media_type = u'image'
    entry.state = state

    if fake_upload:
        entry.media_files = {'thumb': ['a', 'b', 'c.jpg'],
                             'medium': ['d', 'e', 'f.png'],
                             'original': ['g', 'h', 'i.png']}
        entry.media_type = u'mediagoblin.media_types.image'

    if gen_slug:
        entry.generate_slug()

    if save:
        entry.save()

    if expunge:
        entry = MediaEntry.query.filter_by(id=entry.id).first()

        Session.expunge(entry)

    return entry


def fixture_add_collection(name=u"My first Collection", user=None,
                           collection_type=Collection.USER_DEFINED_TYPE):
    if user is None:
        user = fixture_add_user()
    coll = Collection.query.filter_by(
        actor=user.id,
        title=name,
        type=collection_type
    ).first()
    if coll is not None:
        return coll
    coll = Collection()
    coll.actor = user.id
    coll.title = name
    coll.type = collection_type
    coll.generate_slug()
    coll.save()

    # Reload
    Session.refresh(coll)

    # ... and detach from session:
    Session.expunge(coll)

    return coll

def fixture_add_comment(author=None, media_entry=None, comment=None):
    if author is None:
        author = fixture_add_user().id

    if media_entry is None:
        media_entry = fixture_media_entry()

    if comment is None:
        comment = \
            'Auto-generated test comment by user #{0} on media #{0}'.format(
                author, media_entry)

    text_comment = TextComment(
        actor=author,
        content=comment
    )
    text_comment.save()

    comment_link = Comment()
    comment_link.target = media_entry
    comment_link.comment = text_comment
    comment_link.save()

    Session.expunge(comment_link)

    return text_comment

def fixture_add_comment_report(comment=None, reported_user=None,
        reporter=None, created=None, report_content=None):
    if comment is None:
        comment = fixture_add_comment()

    if reported_user is None:
        reported_user = fixture_add_user()

    if reporter is None:
        reporter = fixture_add_user()

    if created is None:
        created=datetime.now()

    if report_content is None:
        report_content = \
            'Auto-generated test report'

    comment_report = Report()
    comment_report.obj = comment
    comment_report.reported_user = reported_user
    comment_report.reporter = reporter
    comment_report.created = created
    comment_report.report_content = report_content
    comment_report.obj = comment
    comment_report.save()

    Session.expunge(comment_report)

    return comment_report

def fixture_add_activity(obj, verb="post", target=None, generator=None, actor=None):
    if generator is None:
        generator = Generator(
            name="GNU MediaGoblin",
            object_type="service"
        )
        generator.save()

    if actor is None:
        actor = fixture_add_user()

    activity = Activity(
        verb=verb,
        actor=actor.id,
        generator=generator.id,
    )

    activity.set_object(obj)

    if target is not None:
        activity.set_target(target)

    activity.save()
    return activity
