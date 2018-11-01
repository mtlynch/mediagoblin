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
import os
from contextlib import contextmanager
import imghdr

#os.environ['GST_DEBUG'] = '4,python:4'
import pytest
pytest.importorskip("gi.repository.Gst")

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
Gst.init(None)

from mediagoblin.media_types.video.transcoders import (capture_thumb,
        VideoTranscoder)
from mediagoblin.media_types.video.util import ACCEPTED_RESOLUTIONS
from mediagoblin.media_types.tools import discover
from mediagoblin.tests.tools import get_app

@contextmanager
def create_data(suffix=None, make_audio=False):
    video = tempfile.NamedTemporaryFile()
    src = Gst.ElementFactory.make('videotestsrc', None)
    src.set_property('num-buffers', 10)
    videorate = Gst.ElementFactory.make('videorate', None)
    enc = Gst.ElementFactory.make('theoraenc', None)
    mux = Gst.ElementFactory.make('oggmux', None)
    dst = Gst.ElementFactory.make('filesink', None)
    dst.set_property('location', video.name)
    pipeline = Gst.Pipeline()
    pipeline.add(src)
    pipeline.add(videorate)
    pipeline.add(enc)
    pipeline.add(mux)
    pipeline.add(dst)
    src.link(videorate)
    videorate.link(enc)
    enc.link(mux)
    mux.link(dst)
    if make_audio:
        audio_src = Gst.ElementFactory.make('audiotestsrc', None)
        audio_src.set_property('num-buffers', 10)
        audiorate = Gst.ElementFactory.make('audiorate', None)
        audio_enc = Gst.ElementFactory.make('vorbisenc', None)
        pipeline.add(audio_src)
        pipeline.add(audio_enc)
        pipeline.add(audiorate)
        audio_src.link(audiorate)
        audiorate.link(audio_enc)
        audio_enc.link(mux)
    pipeline.set_state(Gst.State.PLAYING)
    state = pipeline.get_state(3 * Gst.SECOND)
    assert state[0] == Gst.StateChangeReturn.SUCCESS
    bus = pipeline.get_bus()
    message = bus.timed_pop_filtered(
            3 * Gst.SECOND,
            Gst.MessageType.ERROR | Gst.MessageType.EOS)
    pipeline.set_state(Gst.State.NULL)
    if suffix:
        result = tempfile.NamedTemporaryFile(suffix=suffix)
    else:
        result = tempfile.NamedTemporaryFile()
    yield (video.name, result.name)


@pytest.mark.skipif(os.getenv('DOCKER', 'false') == 'true',
                    reason='Test currently fails in Docker container')
def test_thumbnails():
    '''
    Test thumbnails generation.
    1. Create a video (+audio) from gst's videotestsrc
    2. Capture thumbnail
    3. Everything should get removed because of temp files usage
    '''
    #data  create_data() as (video_name, thumbnail_name):
    test_formats = [('.png', 'png'), ('.jpg', 'jpeg'), ('.gif', 'gif')]
    for suffix, format in test_formats:
        with create_data(suffix) as (video_name, thumbnail_name):
            capture_thumb(video_name, thumbnail_name, width=40)
            # check result file format
            assert imghdr.what(thumbnail_name) == format
            # TODO: check height and width
            # FIXME: it doesn't work with small width, say, 10px. This should be
            # fixed somehow
    suffix, format = test_formats[0]
    with create_data(suffix, True) as (video_name, thumbnail_name):
        capture_thumb(video_name, thumbnail_name, width=40)
        assert imghdr.what(thumbnail_name) == format
    with create_data(suffix, True) as (video_name, thumbnail_name):
        capture_thumb(video_name, thumbnail_name, width=10)  # smaller width
        assert imghdr.what(thumbnail_name) == format
    with create_data(suffix, True) as (video_name, thumbnail_name):
        capture_thumb(video_name, thumbnail_name, width=100)  # bigger width
        assert imghdr.what(thumbnail_name) == format


@pytest.mark.skipif(os.getenv('DOCKER', 'false') == 'true',
                    reason='Test currently fails in Docker container')
def test_transcoder():
    # test without audio
    with create_data() as (video_name, result_name):
        transcoder = VideoTranscoder()
        transcoder.transcode(
                video_name, result_name,
                '480p', 1,
                vp8_quality=8,
                vp8_threads=0,  # autodetect
                vorbis_quality=0.3,
                dimensions=(640, 640))
        assert len(discover(result_name).get_video_streams()) == 1
    # test with audio
    with create_data(make_audio=True) as (video_name, result_name):
        transcoder = VideoTranscoder()
        transcoder.transcode(
                video_name, result_name,
                '480p', 1,
                vp8_quality=8,
                vp8_threads=0,  # autodetect
                vorbis_quality=0.3,
                dimensions=(640, 640))
        assert len(discover(result_name).get_video_streams()) == 1
        assert len(discover(result_name).get_audio_streams()) == 1

def test_accepted_resolutions():
    accepted_resolutions = {
        '144p': (256, 144),
        '240p': (352, 240),
        '360p': (480, 360),
        '480p': (858, 480),
        '720p': (1280, 720),
        '1080p': (1920, 1080),
        'webm': (640, 640),
    }
    assert accepted_resolutions == ACCEPTED_RESOLUTIONS
