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

from mediagoblin import mg_globals
import os

def open_subtitle(path):
    status = True
    subtitle_public_filepath = path
    try:
        with mg_globals.public_store.get_file(
                subtitle_public_filepath, 'rb') as subtitle_public_file:
                text = subtitle_public_file.read().decode('utf-8','ignore')
                return (text,status)
    except:
        status = False
        return ('',status)

def save_subtitle(path,text):
    status = True
    subtitle_public_filepath = path
    try:
        with mg_globals.public_store.get_file(
                subtitle_public_filepath, 'wb') as subtitle_public_file:
            subtitle_public_file.write(text.encode('utf-8','ignore'))
            return status
    except:
        status = False
        return (status)
