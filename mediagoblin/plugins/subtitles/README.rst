================
Subtitles plugin
================

This plugin enables text captioning of videos (though not yet audio). Once the
plugin is enabled, you'll see a link to upload subtitles in `WebVTT format`_ as
supported by the Video.js `Text Tracks`_ feature.

.. _WebVTT format: https://en.wikipedia.org/wiki/WebVTT
.. _Text Tracks: https://docs.videojs.com/docs/guides/text-tracks.html

.. _subtitles-setup:

Enabling the subtitles plugin
=============================

1. Add the following to your MediaGoblin .ini file in the ``[plugins]`` section::

    [[mediagoblin.plugins.subtitles]]

2. Run::

    $ ./bin/gmg dbupdate

3. Restart your MediaGoblin process.
