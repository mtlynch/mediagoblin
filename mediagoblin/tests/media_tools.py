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

from contextlib import contextmanager
import tempfile

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
Gst.init(None)

@contextmanager
def create_av(make_video=False, make_audio=False):
    'creates audio/video in `path`, throws AssertionError on any error'
    media = tempfile.NamedTemporaryFile(suffix='.ogg')
    pipeline = Gst.Pipeline()
    mux = Gst.ElementFactory.make('oggmux', 'mux')
    pipeline.add(mux)
    if make_video:
        video_src = Gst.ElementFactory.make('videotestsrc', 'video_src')
        video_src.set_property('num-buffers', 20)
        video_enc = Gst.ElementFactory.make('theoraenc', 'video_enc')
        pipeline.add(video_src)
        pipeline.add(video_enc)
        assert video_src.link(video_enc)
        assert video_enc.link(mux)
    if make_audio:
        audio_src = Gst.ElementFactory.make('audiotestsrc', 'audio_src')
        audio_src.set_property('num-buffers', 20)
        audio_enc = Gst.ElementFactory.make('vorbisenc', 'audio_enc')
        pipeline.add(audio_src)
        pipeline.add(audio_enc)
        assert audio_src.link(audio_enc)
        assert audio_enc.link(mux)
    sink = Gst.ElementFactory.make('filesink', 'sink')
    sink.set_property('location', media.name)
    pipeline.add(sink)
    mux.link(sink)
    pipeline.set_state(Gst.State.PLAYING)
    state = pipeline.get_state(Gst.SECOND)
    assert state[0] == Gst.StateChangeReturn.SUCCESS
    bus = pipeline.get_bus()
    message = bus.timed_pop_filtered(
            Gst.SECOND,  # one second should be more than enough for 50-buf vid
            Gst.MessageType.ERROR | Gst.MessageType.EOS)
    assert message.type == Gst.MessageType.EOS
    pipeline.set_state(Gst.State.NULL)
    yield media.name
