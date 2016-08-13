# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2013 MediaGoblin contributors.  See AUTHORS.
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

from mediagoblin.tests import tools
from mediagoblin import mg_globals
from mediagoblin.db.models import User, MediaEntry
from mediagoblin.db.base import Session
from mediagoblin.tools.testing import _activate_testing
from mediagoblin.tests.tools import fixture_add_user, fixture_media_entry
from mediagoblin.plugins.subtitles.tools import open_subtitle, save_subtitle

# Checking if the subtitle entry is working

def test_add_subtitle_entry(test_app):
    user_a = fixture_add_user(u"test_user")

    media = fixture_media_entry(uploader=user_a.id, save=False, expunge=False)
    media.subtitle_files.append(dict(
            name=u"some name",
            filepath=[u"does", u"not", u"exist"],
            ))
    Session.add(media)
    Session.flush()

    MediaEntry.query.get(media.id).delete()
    User.query.get(user_a.id).delete()

# Checking the tools written for subtitles

def test_read_write_file(test_app):
    test_filepath = ['test']
    
    status = save_subtitle(test_filepath,"Testing!!!")
    text = open_subtitle(test_filepath)[0]
    
    assert status == True
    assert text == "Testing!!!"
    
    mg_globals.public_store.delete_file(test_filepath)

# Checking the customize exceptions

def test_customize_subtitle(test_app):
    user_a = fixture_add_user(u"test_user")

    media = fixture_media_entry(uploader=user_a.id, save=False, expunge=False)
    media.subtitle_files.append(dict(
            name=u"some name",
            filepath=[u"does", u"not", u"exist"],
            ))
    Session.add(media)
    Session.flush()

    for subtitle in media.subtitle_files:
        assert '' == open_subtitle(subtitle['filepath'])[0]
