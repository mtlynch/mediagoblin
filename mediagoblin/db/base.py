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
import datetime

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

    __default_model_args__ = {
        "deletion": HARD_DELETE,
        "soft_deletion_field": "deleted",
        "soft_deletion_retain": ("id",)
    }

    @property
    def _session(self):
        return inspect(self).session

    @property
    def _app(self):
        return self._session.bind.app

    if not DISABLE_GLOBALS:
        query = Session.query_property()

    def get_model_arg(self, argument):
        model_args = self.__default_model_args__.copy()
        model_args.update(getattr(self, "__model_args__", {}))
        return model_args.get(argument)

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

    def delete(self, commit=True):
        """ Delete the object either using soft or hard deletion """
        if self.get_model_arg("deletion") == self.HARD_DELETE:
            return self.hard_delete(commit)
        elif self.get_model_arg("deletion") == self.SOFT_DELETE:
            return self.soft_delete(commit)
        else:
            raise ValueError(
                "__model_args__['deletion'] is an invalid value %s" % (
                    self.get_model_arg("deletion")
                ))

    def soft_delete(self, commit):
        # Find the deletion field
        field_name = self.get_model_arg("soft_deletion_field")

        # We can't use self.__table__.columns as it only shows it of the
        # current model and no parent if polymorphism is being used. This
        # will cause problems for example for the User model.
        if field_name not in dir(type(self)):
            raise ValueError("Cannot find soft_deletion_field")

        # Store a value in the deletion field
        setattr(self, field_name, datetime.datetime.utcnow())

        # Iterate through the fields and remove data
        retain_fields = self.get_model_arg("soft_deletion_retain")
        for field_name in self.__table__.columns.keys():
            # should we skip this field?
            if field_name in retain_fields:
                continue

            setattr(self, field_name, None)

        # Save the changes
        self.save(commit)

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
