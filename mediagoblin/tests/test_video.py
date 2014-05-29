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

import tempfile
import shutil
import os
import pytest
from contextlib import contextmanager
import logging
import imghdr

#TODO: this should be skipped if video plugin is not enabled
import pygst
pygst.require('0.10')
import gst

from mediagoblin.media_types.video.transcoders import capture_thumb

@contextmanager
def create_data(suffix):
    video = tempfile.NamedTemporaryFile()
    src = gst.element_factory_make('videotestsrc')
    src.set_property('num-buffers', 50)
    enc = gst.element_factory_make('theoraenc')
    mux = gst.element_factory_make('oggmux')
    dst = gst.element_factory_make('filesink')
    dst.set_property('location', video.name)
    pipeline = gst.Pipeline()
    pipeline.add(src, enc, mux, dst)
    gst.element_link_many(src, enc, mux, dst)
    pipeline.set_state(gst.STATE_PLAYING)
    # wait for finish
    bus = pipeline.get_bus()
    message = bus.timed_pop_filtered(gst.CLOCK_TIME_NONE,
                                     gst.MESSAGE_ERROR | gst.MESSAGE_EOS)
    thumb = tempfile.NamedTemporaryFile(suffix=suffix)
    pipeline.set_state(gst.STATE_NULL)
    yield (video.name, thumb.name)


#TODO: this should be skipped if video plugin is not enabled
def test_thumbnails():
    '''
    Test thumbnails generation.
    1. Create a video from gst's videotestsrc
    3. Capture thumbnail
    4. Remove it
    '''
    #data  create_data() as (video_name, thumbnail_name):
    test_formats = [('.png', 'png'), ('.jpg', 'jpeg'), ('.gif', 'gif')]
    for suffix, format in test_formats:
        with create_data(suffix) as (video_name, thumbnail_name):
            capture_thumb(video_name, thumbnail_name, width=40)
            # check if png
            assert imghdr.what(thumbnail_name) == format
            # TODO: check height and width
            # FIXME: it doesn't work with small width, say, 10px. This should be
            # fixed somehow
