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
import logging
import shutil
import tempfile

from mediagoblin.tools.pluginapi import hook_handle
from mediagoblin.tools.translate import lazy_pass_to_ugettext as _

_log = logging.getLogger(__name__)


class FileTypeNotSupported(Exception):
    pass


class TypeNotFound(FileTypeNotSupported):
    '''Raised if no mediagoblin plugin supporting this file type was found'''
    pass


class MissingComponents(FileTypeNotSupported):
    '''Raised if plugin found, but it can't process the file for some reason'''
    pass


class MediaManagerBase(object):
    "Base class for all media managers"

    # Please override in actual media managers
    media_fetch_order = None

    @staticmethod
    def sniff_handler(*args, **kwargs):
        return False

    def __init__(self, entry):
        self.entry = entry

    def __getitem__(self, i):
        return getattr(self, i)

    def __contains__(self, i):
        return hasattr(self, i)


def sniff_media_contents(media_file, filename):
    '''
    Check media contents using 'expensive' scanning. For example, for video it
    is checking the contents using gstreamer
    :param media_file: file-like object with 'name' attribute
    :param filename: expected filename of the media
    '''
    media_type = hook_handle('sniff_handler', media_file, filename)
    if media_type:
        _log.info('{0} accepts the file'.format(media_type))
        return media_type, hook_handle(('media_manager', media_type))
    else:
        _log.debug('{0} did not accept the file'.format(media_type))
        raise FileTypeNotSupported(
            # TODO: Provide information on which file types are supported
            _(u'Sorry, I don\'t support that file type :('))

def get_media_type_and_manager(filename):
    '''
    Try to find the media type based on the file name, extension
    specifically. This is used as a speedup, the sniffing functionality
    then falls back on more in-depth bitsniffing of the source file.

    This hook is deprecated, 'type_match_handler' should be used instead
    '''
    if filename.find('.') > 0:
        # Get the file extension
        ext = os.path.splitext(filename)[1].lower()

        # Omit the dot from the extension and match it against
        # the media manager
        if hook_handle('get_media_type_and_manager', ext[1:]):
            return hook_handle('get_media_type_and_manager', ext[1:])
    else:
        _log.info('File {0} has no file extension, let\'s hope the sniffers get it.'.format(
            filename))

    raise TypeNotFound(
        _(u'Sorry, I don\'t support that file type :('))

def type_match_handler(media_file, filename):
    '''Check media file by name and then by content

    Try to find the media type based on the file name, extension
    specifically. After that, if media type is one of supported ones, check the
    contents of the file
    '''
    if filename.find('.') > 0:
        # Get the file extension
        ext = os.path.splitext(filename)[1].lower()

        # Omit the dot from the extension and match it against
        # the media manager
        hook_result = hook_handle('type_match_handler', ext[1:])
        if hook_result:
            _log.info('Info about file found, checking further')
            MEDIA_TYPE, Manager, sniffer = hook_result
            if not sniffer:
                _log.debug('sniffer is None, plugin trusts the extension')
                return MEDIA_TYPE, Manager
            _log.info('checking the contents with sniffer')
            try:
                sniffer(media_file)
                _log.info('checked, found')
                return MEDIA_TYPE, Manager
            except Exception as e:
                _log.info('sniffer says it will not accept the file')
                _log.debug(e)
                raise
        else:
            _log.info('No plugins handled extension {0}'.format(ext))
    else:
        _log.info('File {0} has no known file extension, let\'s hope '
                'the sniffers get it.'.format(filename))
    raise TypeNotFound(_(u'Sorry, I don\'t support that file type :('))


def sniff_media(media_file, filename):
    '''
    Iterate through the enabled media types and find those suited
    for a certain file.
    '''
    # copy the contents to a .name-enabled temporary file for further checks
    # TODO: there are cases when copying is not required
    tmp_media_file = tempfile.NamedTemporaryFile()
    shutil.copyfileobj(media_file, tmp_media_file)
    media_file.seek(0)
    try:
        return type_match_handler(tmp_media_file, filename)
    except TypeNotFound as e:
        _log.info('No plugins using two-step checking found')

    # keep trying, using old `get_media_type_and_manager`
    try:
        return get_media_type_and_manager(filename)
    except TypeNotFound as e:
        # again, no luck. Do it expensive way
        _log.info('No media handler found by file extension')
    _log.info('Doing it the expensive way...')
    return sniff_media_contents(tmp_media_file, filename)

