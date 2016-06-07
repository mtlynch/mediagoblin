from mediagoblin.tools import pluginapi
import os

PLUGIN_DIR = os.path.dirname(__file__)

def setup_plugin():
    config = pluginapi.get_config('mediagoblin.plugins.custom_subtitles')

    # Register the template path.
    pluginapi.register_template_path(os.path.join(PLUGIN_DIR, 'templates'))



hooks = {
    'setup': setup_plugin
    }
