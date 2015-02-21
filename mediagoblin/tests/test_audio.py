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

#os.environ['GST_DEBUG'] = '4,python:4'

pytest.importorskip("gi.repository.Gst")
pytest.importorskip("scikits.audiolab")
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
Gst.init(None)

from mediagoblin.media_types.audio.transcoders import (AudioTranscoder,
        AudioThumbnailer)
from mediagoblin.media_types.tools import discover


@contextmanager
def create_audio():
    audio = tempfile.NamedTemporaryFile()
    src = Gst.ElementFactory.make('audiotestsrc', None)
    src.set_property('num-buffers', 50)
    enc = Gst.ElementFactory.make('flacenc', None)
    dst = Gst.ElementFactory.make('filesink', None)
    dst.set_property('location', audio.name)
    pipeline = Gst.Pipeline()
    pipeline.add(src)
    pipeline.add(enc)
    pipeline.add(dst)
    src.link(enc)
    enc.link(dst)
    pipeline.set_state(Gst.State.PLAYING)
    state = pipeline.get_state(3 * Gst.SECOND)
    assert state[0] == Gst.StateChangeReturn.SUCCESS
    bus = pipeline.get_bus()
    bus.timed_pop_filtered(
            3 * Gst.SECOND,
            Gst.MessageType.ERROR | Gst.MessageType.EOS)
    pipeline.set_state(Gst.State.NULL)
    yield (audio.name)


@contextmanager
def create_data_for_test():
    with create_audio() as audio_name:
        second_file = tempfile.NamedTemporaryFile()
        yield (audio_name, second_file.name)


def test_transcoder():
    '''
    Tests AudioTransocder's transcode method
    '''
    transcoder = AudioTranscoder()
    with create_data_for_test() as (audio_name, result_name):
        transcoder.transcode(audio_name, result_name, quality=0.3,
                             progress_callback=None)
        info = discover(result_name)
        assert len(info.get_audio_streams()) == 1
        transcoder.transcode(audio_name, result_name, quality=0.3,
                             mux_name='oggmux', progress_callback=None)
        info = discover(result_name)
        assert len(info.get_audio_streams()) == 1


def test_thumbnails():
    '''Test thumbnails generation.

    The code below heavily repeats
    audio.processing.CommonAudioProcessor.create_spectrogram
    1. Create test audio
    2. Convert it to OGG source for spectogram using transcoder
    3. Create spectogram in jpg

    '''
    thumbnailer = AudioThumbnailer()
    transcoder = AudioTranscoder()
    with create_data_for_test() as (audio_name, new_name):
        transcoder.transcode(audio_name, new_name, mux_name='oggmux')
        thumbnail = tempfile.NamedTemporaryFile(suffix='.jpg')
        # fft_size below is copypasted from config_spec.ini
        thumbnailer.spectrogram(new_name, thumbnail.name, width=100,
                                fft_size=4096)
        assert imghdr.what(thumbnail.name) == 'jpeg'
