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

import sys

import six

from mediagoblin.db.models import LocalUser
from mediagoblin.gmg_commands import util as commands_util
from mediagoblin import auth
from mediagoblin import mg_globals

def adduser_parser_setup(subparser):
    subparser.add_argument(
        '--username','-u',
        help="Username used to login")
    subparser.add_argument(
        '--password','-p',
        help="Your supersecret word to login, beware of storing it in bash history")
    subparser.add_argument(
        '--email','-e',
        help="Email to receive notifications")


def adduser(args):
    #TODO: Lets trust admins this do not validate Emails :)
    commands_util.setup_app(args)

    args.username = six.text_type(commands_util.prompt_if_not_set(args.username, "Username:"))
    args.password = commands_util.prompt_if_not_set(args.password, "Password:",True)
    args.email = commands_util.prompt_if_not_set(args.email, "Email:")

    db = mg_globals.database
    users_with_username = \
        db.LocalUser.query.filter(
            LocalUser.username==args.username.lower()
        ).count()

    if users_with_username:
        print(u'Sorry, a user with that name already exists.')
        sys.exit(1)

    else:
        # Create the user
        entry = db.LocalUser()
        entry.username = six.text_type(args.username.lower())
        entry.email = six.text_type(args.email)
        entry.pw_hash = auth.gen_password_hash(args.password)
        default_privileges = [
            db.Privilege.query.filter(
                db.Privilege.privilege_name==u'commenter').one(),
            db.Privilege.query.filter(
                db.Privilege.privilege_name==u'uploader').one(),
            db.Privilege.query.filter(
                db.Privilege.privilege_name==u'reporter').one(),
            db.Privilege.query.filter(
                db.Privilege.privilege_name==u'active').one()
        ]
        entry.all_privileges = default_privileges
        entry.save()

        print(u"User created (and email marked as verified).")


def makeadmin_parser_setup(subparser):
    subparser.add_argument(
        'username',
        help="Username to give admin level",
        type=six.text_type)


def makeadmin(args):
    commands_util.setup_app(args)

    db = mg_globals.database

    user = db.LocalUser.query.filter(
        LocalUser.username==args.username.lower()
    ).first()
    if user:
        user.all_privileges.append(
            db.Privilege.query.filter(
                db.Privilege.privilege_name==u'admin').one()
        )
        user.save()
        print(u'The user %s is now an admin.' % args.username)
    else:
        print(u'The user %s doesn\'t exist.' % args.username)
        sys.exit(1)


def changepw_parser_setup(subparser):
    subparser.add_argument(
        'username',
        help="Username used to login",
        type=six.text_type)
    subparser.add_argument(
        'password',
        help="Your NEW supersecret word to login")


def changepw(args):
    commands_util.setup_app(args)

    db = mg_globals.database

    user = db.LocalUser.query.filter(
        LocalUser.username==args.username.lower()
    ).first()
    if user:
        user.pw_hash = auth.gen_password_hash(args.password)
        user.save()
        print(u'Password successfully changed for user %s.' % args.username)
    else:
        print(u'The user %s doesn\'t exist.' % args.username)
        sys.exit(1)


def deleteuser_parser_setup(subparser):
    subparser.add_argument(
        'username',
        help="Username to delete",
        type=six.text_type)


def deleteuser(args):
    commands_util.setup_app(args)

    db = mg_globals.database

    user = db.LocalUser.query.filter(
        LocalUser.username==args.username.lower()
    ).first()
    if user:
        user.delete()
        print('The user %s has been deleted.' % args.username)
    else:
        print('The user %s doesn\'t exist.' % args.username)
        sys.exit(1)
