# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2016 MediaGoblin contributors.  See AUTHORS.
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
from sqlalchemy import Column, Integer, Unicode, ForeignKey
from sqlalchemy.orm import relationship

from mediagoblin.db.models import User
from mediagoblin.db.base import Base,MediaEntry

class MediaSubtitleFile(Base):
    __tablename__ = "core__subtitle_files"

    id = Column(Integer, primary_key=True)
    media_entry = Column(
        Integer, ForeignKey(MediaEntry.id),
        nullable=False)
    name = Column(Unicode, nullable=False)
    filepath = Column(PathTupleWithSlashes)
    created = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    @property
    def dict_view(self):
        """A dict like view on this object"""
        return DictReadAttrProxy(self)

    subtitle_files_helper = relationship("MediaSubtitleFile",
        cascade="all, delete-orphan",
        order_by="MediaSubtitleFile.created"
        )
    subtitle_files = association_proxy("subtitle_files_helper", "dict_view",
        creator=lambda v: MediaSubtitleFile(
            name=v["name"], filepath=v["filepath"])
        )

MODELS = [
    MediaSubtitleFile
]
