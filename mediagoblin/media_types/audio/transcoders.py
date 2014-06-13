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
try:
    from PIL import Image
except ImportError:
    import Image

from mediagoblin.media_types.audio import audioprocessing

_log = logging.getLogger(__name__)

CPU_COUNT = 2  # Just assuming for now

# IMPORT MULTIPROCESSING
try:
    import multiprocessing
    try:
        CPU_COUNT = multiprocessing.cpu_count()
    except NotImplementedError:
        _log.warning('multiprocessing.cpu_count not implemented!\n'
                     'Assuming 2 CPU cores')
except ImportError:
    _log.warning('Could not import multiprocessing, assuming 2 CPU cores')

# uncomment this to get a lot of logs from gst
# import os;os.environ['GST_DEBUG'] = '5,python:5'

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst
Gst.init(None)

import numpy


class AudioThumbnailer(object):
    def __init__(self):
        _log.info('Initializing {0}'.format(self.__class__.__name__))

    def spectrogram(self, src, dst, **kw):
        width = kw['width']
        height = int(kw.get('height', float(width) * 0.3))
        fft_size = kw.get('fft_size', 2048)
        callback = kw.get('progress_callback')
        processor = audioprocessing.AudioProcessor(
            src,
            fft_size,
            numpy.hanning)

        samples_per_pixel = processor.audio_file.nframes / float(width)

        spectrogram = audioprocessing.SpectrogramImage(width, height, fft_size)

        for x in range(width):
            if callback and x % (width / 10) == 0:
                callback((x * 100) / width)

            seek_point = int(x * samples_per_pixel)

            (spectral_centroid, db_spectrum) = processor.spectral_centroid(
                seek_point)

            spectrogram.draw_spectrum(x, db_spectrum)

        if callback:
            callback(100)

        spectrogram.save(dst)

    def thumbnail_spectrogram(self, src, dst, thumb_size):
        '''
        Takes a spectrogram and creates a thumbnail from it
        '''
        if not (type(thumb_size) == tuple and len(thumb_size) == 2):
            raise Exception('thumb_size argument should be a tuple(width, height)')

        im = Image.open(src)

        im_w, im_h = [float(i) for i in im.size]
        th_w, th_h = [float(i) for i in thumb_size]

        wadsworth_position = im_w * 0.3

        start_x = max((
                wadsworth_position - ((im_h * (th_w / th_h)) / 2.0),
                0.0))

        stop_x = start_x + (im_h * (th_w / th_h))

        th = im.crop((
                int(start_x), 0,
                int(stop_x), int(im_h)))

        th.thumbnail(thumb_size, Image.ANTIALIAS)

        th.save(dst)


class AudioTranscoder(object):
    def __init__(self):
        _log.info('Initializing {0}'.format(self.__class__.__name__))

        # Instantiate MainLoop
        self._loop = GObject.MainLoop()
        self._failed = None

    def transcode(self, src, dst, mux_name='webmmux',quality=0.3,
                  progress_callback=None, **kw):
        def _on_pad_added(element, pad, connect_to):
            caps = pad.query_caps(None)
            name = caps.to_string()
            _log.debug('on_pad_added: {0}'.format(name))
            if name.startswith('audio') and not connect_to.is_linked():
                pad.link(connect_to)
        _log.info('Transcoding {0} into {1}'.format(src, dst))
        self.__on_progress = progress_callback
        # Set up pipeline
        tolerance = 80000000
        self.pipeline = Gst.Pipeline()
        filesrc = Gst.ElementFactory.make('filesrc', 'filesrc')
        filesrc.set_property('location', src)
        decodebin = Gst.ElementFactory.make('decodebin', 'decodebin')
        queue = Gst.ElementFactory.make('queue', 'queue')
        decodebin.connect('pad-added', _on_pad_added,
                          queue.get_static_pad('sink'))
        audiorate = Gst.ElementFactory.make('audiorate', 'audiorate')
        audiorate.set_property('tolerance', tolerance)
        audioconvert = Gst.ElementFactory.make('audioconvert', 'audioconvert')
        caps_struct = Gst.Structure.new_empty('audio/x-raw')
        caps_struct.set_value('channels', 2)
        caps = Gst.Caps.new_empty()
        caps.append_structure(caps_struct)
        capsfilter = Gst.ElementFactory.make('capsfilter', 'capsfilter')
        capsfilter.set_property('caps', caps)
        enc = Gst.ElementFactory.make('vorbisenc', 'enc')
        enc.set_property('quality', quality)
        mux = Gst.ElementFactory.make(mux_name, 'mux')
        progressreport = Gst.ElementFactory.make('progressreport', 'progress')
        progressreport.set_property('silent', True)
        sink = Gst.ElementFactory.make('filesink', 'sink')
        sink.set_property('location', dst)
        # add to pipeline
        for e in [filesrc, decodebin, queue, audiorate, audioconvert,
                  capsfilter, enc, mux, progressreport, sink]:
            self.pipeline.add(e)
        # link elements
        filesrc.link(decodebin)
        decodebin.link(queue)
        queue.link(audiorate)
        audiorate.link(audioconvert)
        audioconvert.link(capsfilter)
        capsfilter.link(enc)
        enc.link(mux)
        mux.link(progressreport)
        progressreport.link(sink)
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message', self.__on_bus_message)
        # run
        self.pipeline.set_state(Gst.State.PLAYING)
        self._loop.run()

    def __on_bus_message(self, bus, message):
        _log.debug(message.type)
        if (message.type == Gst.MessageType.ELEMENT
                and message.has_name('progress')):
            structure = message.get_structure()
            (success, percent) = structure.get_int('percent')
            if self.__on_progress and success:
                self.__on_progress(percent)
            _log.info('{0}% done...'.format(percent))
        elif message.type == Gst.MessageType.EOS:
            _log.info('Done')
            self.halt()
        elif message.type == Gst.MessageType.ERROR:
            _log.error(message.parse_error())
            self.halt()

    def halt(self):
        if getattr(self, 'pipeline', False):
            self.pipeline.set_state(Gst.State.NULL)
            del self.pipeline
        _log.info('Quitting MainLoop gracefully...')
        GObject.idle_add(self._loop.quit)

if __name__ == '__main__':
    import sys
    logging.basicConfig()
    _log.setLevel(logging.INFO)

    #transcoder = AudioTranscoder()
    #data = transcoder.discover(sys.argv[1])
    #res = transcoder.transcode(*sys.argv[1:3])

    thumbnailer = AudioThumbnailer()

    thumbnailer.spectrogram(*sys.argv[1:], width=640)
