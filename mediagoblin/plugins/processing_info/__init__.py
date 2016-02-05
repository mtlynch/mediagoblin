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
import os

from mediagoblin.tools.pluginapi import get_config
from mediagoblin.db.models import MediaEntry
from mediagoblin.tools import pluginapi

_log = logging.getLogger(__name__)

PLUGIN_DIR = os.path.dirname(__file__)

def setup_plugin():
    pluginapi.register_template_path(os.path.join(PLUGIN_DIR, 'templates'))
    pluginapi.register_template_hooks(
            {'header_left': 'mediagoblin/processing_info/header_left.html'})
    return

def make_stats(context):
    request = context['request']
    user = request.user
    if user:
        num_queued = MediaEntry.query.filter_by(
                actor=user.id, state=u'processing').count()
        context['num_queued'] = num_queued
        num_failed = MediaEntry.query.filter_by(
                actor=user.id, state=u'failed').count()
        context['num_failed'] = num_failed
    return context


hooks = {
    'setup': setup_plugin,
    'template_context_prerender': make_stats
    }
