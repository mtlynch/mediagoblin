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

from mediagoblin.tools import pluginapi
import os

PLUGIN_DIR = os.path.dirname(__file__)

def setup_plugin():
    config = pluginapi.get_config('mediagoblin.plugins.subtitles')

    routes = [
        ('mediagoblin.plugins.subtitles.customize',
         '/u/<string:user>/m/<int:media_id>/customize/<int:id>',
         'mediagoblin.plugins.subtitles.views:custom_subtitles'),
        ('mediagoblin.plugins.subtitles.subtitles',
         '/u/<string:user>/m/<int:media_id>/subtitles/',
         'mediagoblin.plugins.subtitles.views:edit_subtitles'),
        ('mediagoblin.plugins.subtitles.delete_subtitles',
         '/u/<string:user>/m/<int:media_id>/delete/<int:id>',
         'mediagoblin.plugins.subtitles.views:delete_subtitles')]

    pluginapi.register_routes(routes)

    # Register the template path.
    pluginapi.register_template_path(os.path.join(PLUGIN_DIR, 'templates'))

    pluginapi.register_template_hooks(
        {"customize_subtitles": "mediagoblin/plugins/subtitles/custom_subtitles.html",
         "add_subtitles": "mediagoblin/plugins/subtitles/subtitles.html",
         "subtitle_sidebar": "mediagoblin/plugins/subtitles/subtitle_media_block.html"})



hooks = {
    'setup': setup_plugin
    }
