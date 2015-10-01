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
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import inspect

from mediagoblin.tools.transition import DISABLE_GLOBALS

if not DISABLE_GLOBALS:
    from sqlalchemy.orm import scoped_session, sessionmaker
    Session = scoped_session(sessionmaker())


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
        tombstone.save()

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
