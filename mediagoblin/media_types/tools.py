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

from mediagoblin import mg_globals

_log = logging.getLogger(__name__)


def media_type_warning():
    if mg_globals.app_config.get('media_types'):
        _log.warning('Media_types have been converted to plugins. Old'
                     ' media_types will no longer work. Please convert them'
                     ' to plugins to continue using them.')


def discover(src):
    '''
    Discover properties about a media file
    '''
    # GStreamer might be not installed, so it should not be initialized on
    # import, or an exception will be raised.
    import gi
    gi.require_version('Gst', '1.0')
    from gi.repository import GObject, Gst, GstPbutils, GLib
    Gst.init(None)

    _log.info('Discovering {0}...'.format(src))
    uri = 'file://{0}'.format(src)
    discoverer = GstPbutils.Discoverer.new(60 * Gst.SECOND)
    return discoverer.discover_uri(uri)
