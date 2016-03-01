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
import six
import copy

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import inspect

from mediagoblin.tools.transition import DISABLE_GLOBALS

if not DISABLE_GLOBALS:
    from sqlalchemy.orm import scoped_session, sessionmaker
    Session = scoped_session(sessionmaker())

class FakeCursor(object):

    def __init__ (self, cursor, mapper, filter=None):
        self.cursor = cursor
        self.mapper = mapper
        self.filter = filter

    def count(self):
        return self.cursor.count()

    def __copy__(self):
        # Or whatever the function is named to make
        # copy.copy happy?
        return FakeCursor(copy.copy(self.cursor), self.mapper, self.filter)

    def __iter__(self):
        return six.moves.filter(self.filter, six.moves.map(self.mapper, self.cursor))

    def __getitem__(self, key):
        return self.mapper(self.cursor[key])

    def slice(self, *args, **kwargs):
        r = self.cursor.slice(*args, **kwargs)
        return list(six.moves.filter(self.filter, six.moves.map(self.mapper, r)))

class GMGTableBase(object):
    # Deletion types
    HARD_DELETE = "hard-deletion"
    SOFT_DELETE = "soft-deletion"

    deletion_mode = HARD_DELETE

    @property
    def _session(self):
        return inspect(self).session

    @property
    def _app(self):
        return self._session.bind.app

    if not DISABLE_GLOBALS:
        query = Session.query_property()

    def get(self, key):
        return getattr(self, key)

    def setdefault(self, key, defaultvalue):
        # The key *has* to exist on sql.
        return getattr(self, key)

    def save(self, commit=True):
        sess = self._session
        if sess is None and not DISABLE_GLOBALS:
            sess = Session()
        assert sess is not None, "Can't save, %r has a detached session" % self
        sess.add(self)
        if commit:
            sess.commit()
        else:
            sess.flush()

    def delete(self, commit=True, deletion=None):
        """ Delete the object either using soft or hard deletion """
        # Get the setting in the model args if none has been specified.
        if deletion is None:
            deletion = self.deletion_mode

        # If the item is in any collection then it should be removed, this will
        # cause issues if it isn't. See #5382.
        # Import here to prevent cyclic imports.
        from mediagoblin.db.models import CollectionItem, GenericModelReference, \
                                          Report, Notification, Comment
        
        # Some of the models don't have an "id" field which means they can't be
        # used with GMR, these models won't be in collections because they
        # can't be. We can skip all of this.
        if hasattr(self, "id"):
            # First find the GenericModelReference for this object
            gmr = GenericModelReference.query.filter_by(
                obj_pk=self.id,
                model_type=self.__tablename__
            ).first()

            # If there is no gmr then we've got lucky, a GMR is a requirement of
            # being in a collection.
            if gmr is not None:
                # Delete collections found
                items = CollectionItem.query.filter_by(
                    object_id=gmr.id
                )
                items.delete()

                # Delete notifications found
                notifications = Notification.query.filter_by(
                    object_id=gmr.id
                )
                notifications.delete()
                
                # Delete this as a comment
                comments = Comment.query.filter_by(
                    comment_id=gmr.id
                )
                comments.delete()

                # Set None on reports found
                reports = Report.query.filter_by(
                    object_id=gmr.id
                )
                for report in reports:
                    report.object_id = None
                    report.save(commit=commit)

        # Hand off to the correct deletion function.
        if deletion == self.HARD_DELETE:
            return self.hard_delete(commit=commit)
        elif deletion == self.SOFT_DELETE:
            return self.soft_delete(commit=commit)
        else:
            raise ValueError(
                "Invalid deletion mode {mode!r}".format(
                    mode=deletion
                )
            )

    def soft_delete(self, commit):
        # Create the graveyard version of this model
        # Importing this here due to cyclic imports
        from mediagoblin.db.models import User, Graveyard, GenericModelReference
        
        tombstone = Graveyard()
        if getattr(self, "public_id", None) is not None:
            tombstone.public_id = self.public_id

        # This is a special case, we don't want to save any actor if the thing
        # being soft deleted is a User model as this would create circular
        # ForeignKeys
        if not isinstance(self, User):
            tombstone.actor = User.query.filter_by(
                id=self.actor
            ).first()
        tombstone.object_type = self.object_type
        tombstone.save(commit=False)

        # There will be a lot of places where the GenericForeignKey will point
        # to the model, we want to remap those to our tombstone.
        gmrs = GenericModelReference.query.filter_by(
            obj_pk=self.id,
            model_type=self.__tablename__
        ).update({
            "obj_pk": tombstone.id,
            "model_type": tombstone.__tablename__,
        })

        
        # Now we can go ahead and actually delete the model.
        return self.hard_delete(commit=commit)

    def hard_delete(self, commit):
        """Delete the object and commit the change immediately by default"""
        sess = self._session
        assert sess is not None, "Not going to delete detached %r" % self
        sess.delete(self)
        if commit:
            sess.commit()


Base = declarative_base(cls=GMGTableBase)


class DictReadAttrProxy(object):
    """
    Maps read accesses to obj['key'] to obj.key
    and hides all the rest of the obj
    """
    def __init__(self, proxied_obj):
        self.proxied_obj = proxied_obj

    def __getitem__(self, key):
        try:
            return getattr(self.proxied_obj, key)
        except AttributeError:
            raise KeyError("%r is not an attribute on %r"
                % (key, self.proxied_obj))
