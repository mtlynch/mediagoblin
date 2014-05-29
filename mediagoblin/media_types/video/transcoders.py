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

from __future__ import division

import os
import sys
import logging
import urllib
import multiprocessing
import gobject

old_argv = sys.argv
sys.argv = []

import pygst
pygst.require('0.10')
import gst

sys.argv = old_argv
import struct
try:
    from PIL import Image
except ImportError:
    import Image

from gst.extend import discoverer

_log = logging.getLogger(__name__)

gobject.threads_init()

CPU_COUNT = 2

try:
    CPU_COUNT = multiprocessing.cpu_count()
except NotImplementedError:
    _log.warning('multiprocessing.cpu_count not implemented')

os.putenv('GST_DEBUG_DUMP_DOT_DIR', '/tmp')


def pixbuf_to_pilbuf(buf):
    data = list()
    for i in range(0, len(buf)-4, 4):
        r, g, b, x = struct.unpack('BBBB', buf[i:i + 4])
        # XXX: can something be done with the 'X' part of RGBX?
        data.append((r, g, b))
    return data

def capture_thumb(video_path, dest_path, width=None, height=None, percent=0.5):
    def pad_added(element, pad, connect_to):
        caps = pad.get_caps()
        name = caps[0].get_name()
        _log.debug('on_pad_added: {0}'.format(name))
        if name.startswith('video') and not connect_to.is_linked():
            pad.link(connect_to)
    # construct pipeline: uridecodebin ! ffmpegcolorspace ! videoscale ! \
    # ! CAPS ! appsink
    pipeline = gst.Pipeline()
    uridecodebin = gst.element_factory_make('uridecodebin')
    uridecodebin.set_property('uri', 'file://{0}'.format(video_path))
    ffmpegcolorspace = gst.element_factory_make('ffmpegcolorspace')
    uridecodebin.connect('pad-added', pad_added,
                         ffmpegcolorspace.get_pad('sink'))
    videoscale = gst.element_factory_make('videoscale')
    filter = gst.element_factory_make('capsfilter', 'filter')
    # create caps for video scaling
    caps_struct = gst.Structure('video/x-raw-rgb')
    caps_struct.set_value('pixel-aspect-ratio', gst.Fraction(1, 1))
    if height:
        caps_struct.set_value('height', height)
    if width:
        caps_struct.set_value('width', width)
    caps = gst.Caps(caps_struct)
    filter.set_property('caps', caps)
    appsink = gst.element_factory_make('appsink')
    pipeline.add(uridecodebin, ffmpegcolorspace, videoscale, filter, appsink)
    gst.element_link_many(ffmpegcolorspace, videoscale, filter, appsink)
    # pipeline constructed, starting playing, but first some preparations
    if pipeline.set_state(gst.STATE_PAUSED) == gst.STATE_CHANGE_FAILURE:
        _log.warning('state change failed')
    pipeline.get_state()
    duration = pipeline.query_duration(gst.FORMAT_TIME, None)[0]
    if duration == gst.CLOCK_TIME_NONE:
        _log.warning('query_duration failed')
        duration = 0  # XXX
    seek_to = int(duration * int(percent * 100) / 100)
    _log.debug('Seeking to {0} of {1}'.format(
            seek_to / gst.SECOND, duration / gst.SECOND))
    seek = pipeline.seek_simple(gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, seek_to)
    if not seek:
        _log.warning('seek failed')
    # get sample, retrieve it's format and save
    sample = appsink.emit("pull-preroll")
    if not sample:
        _log.warning('could not get sample')
        return
    caps = sample.get_caps()
    if not caps:
        _log.warning('could not get snapshot format')
    structure = caps.get_structure(0)
    (success, width) = structure.get_int('width')
    (success, height) = structure.get_int('height')
    buffer = sample.get_buffer()
    im = Image.frombytes('RGB', (width, height),
                         buffer.extract_dup(0, buffer.get_size()))
    im.save(dest_path)
    _log.info('thumbnail saved to {0}'.format(dest_path))
    # cleanup
    pipeline.set_state(gst.STATE_NULL)


class VideoTranscoder(object):
    '''
    Video transcoder

    Transcodes the SRC video file to a VP8 WebM video file at DST

     - Does the same thing as VideoThumbnailer, but produces a WebM vp8
       and vorbis video file.
     - The VideoTranscoder exceeds the VideoThumbnailer in the way
       that it was refined afterwards and therefore is done more
       correctly.
    '''
    def __init__(self):
        _log.info('Initializing VideoTranscoder...')
        self.progress_percentage = None
        self.loop = gobject.MainLoop()

    def transcode(self, src, dst, **kwargs):
        '''
        Transcode a video file into a 'medium'-sized version.
        '''
        self.source_path = src
        self.destination_path = dst

        # vp8enc options
        self.destination_dimensions = kwargs.get('dimensions', (640, 640))
        self.vp8_quality = kwargs.get('vp8_quality', 8)
        # Number of threads used by vp8enc:
        # number of real cores - 1 as per recommendation on
        # <http://www.webmproject.org/tools/encoder-parameters/#6-multi-threaded-encode-and-decode>
        self.vp8_threads = kwargs.get('vp8_threads', CPU_COUNT - 1)

        # 0 means auto-detect, but dict.get() only falls back to CPU_COUNT
        # if value is None, this will correct our incompatibility with
        # dict.get()
        # This will also correct cases where there's only 1 CPU core, see
        # original self.vp8_threads assignment above.
        if self.vp8_threads == 0:
            self.vp8_threads = CPU_COUNT

        # vorbisenc options
        self.vorbis_quality = kwargs.get('vorbis_quality', 0.3)

        self._progress_callback = kwargs.get('progress_callback') or None

        if not type(self.destination_dimensions) == tuple:
            raise Exception('dimensions must be tuple: (width, height)')

        self._setup()
        self._run()

    # XXX: This could be a static method.
    def discover(self, src):
        '''
        Discover properties about a media file
        '''
        _log.info('Discovering {0}'.format(src))

        self.source_path = src
        self._setup_discover(discovered_callback=self.__on_discovered)

        self.discoverer.discover()

        self.loop.run()
        if hasattr(self, '_discovered_data'):
            return self._discovered_data.__dict__
        else:
            return None

    def __on_discovered(self, data, is_media):
        _log.debug('Discovered: {0}'.format(data))
        if not is_media:
            self.__stop()
            raise Exception('Could not discover {0}'.format(self.source_path))

        self._discovered_data = data

        self.__stop_mainloop()

    def _setup(self):
        self._setup_discover()
        self._setup_pipeline()

    def _run(self):
        _log.info('Discovering...')
        self.discoverer.discover()
        _log.info('Done')

        _log.debug('Initializing MainLoop()')
        self.loop.run()

    def _setup_discover(self, **kw):
        _log.debug('Setting up discoverer')
        self.discoverer = discoverer.Discoverer(self.source_path)

        # Connect self.__discovered to the 'discovered' event
        self.discoverer.connect(
            'discovered',
            kw.get('discovered_callback', self.__discovered))

    def __discovered(self, data, is_media):
        '''
        Callback for media discoverer.
        '''
        if not is_media:
            self.__stop()
            raise Exception('Could not discover {0}'.format(self.source_path))

        _log.debug('__discovered, data: {0}'.format(data.__dict__))

        self.data = data

        # Launch things that should be done after discovery
        self._link_elements()
        self.__setup_videoscale_capsfilter()

        # Tell the transcoding pipeline to start running
        self.pipeline.set_state(gst.STATE_PLAYING)
        _log.info('Transcoding...')

    def _setup_pipeline(self):
        _log.debug('Setting up transcoding pipeline')
        # Create the pipeline bin.
        self.pipeline = gst.Pipeline('VideoTranscoderPipeline')

        # Create all GStreamer elements, starting with
        # filesrc & decoder
        self.filesrc = gst.element_factory_make('filesrc', 'filesrc')
        self.filesrc.set_property('location', self.source_path)
        self.pipeline.add(self.filesrc)

        self.decoder = gst.element_factory_make('decodebin2', 'decoder')
        self.decoder.connect('new-decoded-pad', self._on_dynamic_pad)
        self.pipeline.add(self.decoder)

        # Video elements
        self.videoqueue = gst.element_factory_make('queue', 'videoqueue')
        self.pipeline.add(self.videoqueue)

        self.videorate = gst.element_factory_make('videorate', 'videorate')
        self.pipeline.add(self.videorate)

        self.ffmpegcolorspace = gst.element_factory_make(
            'ffmpegcolorspace', 'ffmpegcolorspace')
        self.pipeline.add(self.ffmpegcolorspace)

        self.videoscale = gst.element_factory_make('ffvideoscale', 'videoscale')
        #self.videoscale.set_property('method', 2)  # I'm not sure this works
        #self.videoscale.set_property('add-borders', 0)
        self.pipeline.add(self.videoscale)

        self.capsfilter = gst.element_factory_make('capsfilter', 'capsfilter')
        self.pipeline.add(self.capsfilter)

        self.vp8enc = gst.element_factory_make('vp8enc', 'vp8enc')
        self.vp8enc.set_property('quality', self.vp8_quality)
        self.vp8enc.set_property('threads', self.vp8_threads)
        self.vp8enc.set_property('max-latency', 25)
        self.pipeline.add(self.vp8enc)

        # Audio elements
        self.audioqueue = gst.element_factory_make('queue', 'audioqueue')
        self.pipeline.add(self.audioqueue)

        self.audiorate = gst.element_factory_make('audiorate', 'audiorate')
        self.audiorate.set_property('tolerance', 80000000)
        self.pipeline.add(self.audiorate)

        self.audioconvert = gst.element_factory_make('audioconvert', 'audioconvert')
        self.pipeline.add(self.audioconvert)

        self.audiocapsfilter = gst.element_factory_make('capsfilter',
                                                        'audiocapsfilter')
        audiocaps = ['audio/x-raw-float']
        self.audiocapsfilter.set_property(
            'caps',
            gst.caps_from_string(
                ','.join(audiocaps)))
        self.pipeline.add(self.audiocapsfilter)

        self.vorbisenc = gst.element_factory_make('vorbisenc', 'vorbisenc')
        self.vorbisenc.set_property('quality', self.vorbis_quality)
        self.pipeline.add(self.vorbisenc)

        # WebMmux & filesink
        self.webmmux = gst.element_factory_make('webmmux', 'webmmux')
        self.pipeline.add(self.webmmux)

        self.filesink = gst.element_factory_make('filesink', 'filesink')
        self.filesink.set_property('location', self.destination_path)
        self.pipeline.add(self.filesink)

        # Progressreport
        self.progressreport = gst.element_factory_make(
            'progressreport', 'progressreport')
        # Update every second
        self.progressreport.set_property('update-freq', 1)
        self.progressreport.set_property('silent', True)
        self.pipeline.add(self.progressreport)

    def _link_elements(self):
        '''
        Link all the elements

        This code depends on data from the discoverer and is called
        from __discovered
        '''
        _log.debug('linking elements')
        # Link the filesrc element to the decoder. The decoder then emits
        # 'new-decoded-pad' which links decoded src pads to either a video
        # or audio sink
        self.filesrc.link(self.decoder)

        # Link all the video elements in a row to webmmux
        gst.element_link_many(
            self.videoqueue,
            self.videorate,
            self.ffmpegcolorspace,
            self.videoscale,
            self.capsfilter,
            self.vp8enc,
            self.webmmux)

        if self.data.is_audio:
            # Link all the audio elements in a row to webmux
            gst.element_link_many(
                self.audioqueue,
                self.audiorate,
                self.audioconvert,
                self.audiocapsfilter,
                self.vorbisenc,
                self.webmmux)

        gst.element_link_many(
            self.webmmux,
            self.progressreport,
            self.filesink)

        # Setup the message bus and connect _on_message to the pipeline
        self._setup_bus()

    def _on_dynamic_pad(self, dbin, pad, islast):
        '''
        Callback called when ``decodebin2`` has a pad that we can connect to
        '''
        # Intersect the capabilities of the video sink and the pad src
        # Then check if they have no common capabilities.
        if self.ffmpegcolorspace.get_pad_template('sink')\
                .get_caps().intersect(pad.get_caps()).is_empty():
            # It is NOT a video src pad.
            pad.link(self.audioqueue.get_pad('sink'))
        else:
            # It IS a video src pad.
            pad.link(self.videoqueue.get_pad('sink'))

    def _setup_bus(self):
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message', self._on_message)

    def __setup_videoscale_capsfilter(self):
        '''
        Sets up the output format (width, height) for the video
        '''
        caps = ['video/x-raw-yuv', 'pixel-aspect-ratio=1/1', 'framerate=30/1']

        if self.data.videoheight > self.data.videowidth:
            # Whoa! We have ourselves a portrait video!
            caps.append('height={0}'.format(
                    self.destination_dimensions[1]))
        else:
            # It's a landscape, phew, how normal.
            caps.append('width={0}'.format(
                    self.destination_dimensions[0]))

        self.capsfilter.set_property(
            'caps',
            gst.caps_from_string(
                ','.join(caps)))

    def _on_message(self, bus, message):
        _log.debug((bus, message, message.type))

        t = message.type

        if message.type == gst.MESSAGE_EOS:
            self._discover_dst_and_stop()
            _log.info('Done')

        elif message.type == gst.MESSAGE_ELEMENT:
            if message.structure.get_name() == 'progress':
                data = dict(message.structure)
                # Update progress state if it has changed
                if self.progress_percentage != data.get('percent'):
                    self.progress_percentage = data.get('percent')
                    if self._progress_callback:
                        self._progress_callback(data.get('percent'))

                    _log.info('{percent}% done...'.format(
                            percent=data.get('percent')))
                _log.debug(data)

        elif t == gst.MESSAGE_ERROR:
            _log.error((bus, message))
            self.__stop()

    def _discover_dst_and_stop(self):
        self.dst_discoverer = discoverer.Discoverer(self.destination_path)

        self.dst_discoverer.connect('discovered', self.__dst_discovered)

        self.dst_discoverer.discover()

    def __dst_discovered(self, data, is_media):
        self.dst_data = data

        self.__stop()

    def __stop(self):
        _log.debug(self.loop)

        if hasattr(self, 'pipeline'):
            # Stop executing the pipeline
            self.pipeline.set_state(gst.STATE_NULL)

        # This kills the loop, mercifully
        gobject.idle_add(self.__stop_mainloop)

    def __stop_mainloop(self):
        '''
        Wrapper for gobject.MainLoop.quit()

        This wrapper makes us able to see if self.loop.quit has been called
        '''
        _log.info('Terminating MainLoop')

        self.loop.quit()


if __name__ == '__main__':
    os.nice(19)
    from optparse import OptionParser

    parser = OptionParser(
        usage='%prog [-v] -a [ video | thumbnail | discover ] SRC [ DEST ]')

    parser.add_option('-a', '--action',
                      dest='action',
                      help='One of "video", "discover" or "thumbnail"')

    parser.add_option('-v',
                      dest='verbose',
                      action='store_true',
                      help='Output debug information')

    parser.add_option('-q',
                      dest='quiet',
                      action='store_true',
                      help='Dear program, please be quiet unless *error*')

    parser.add_option('-w', '--width',
                      type=int,
                      default=180)

    (options, args) = parser.parse_args()

    if options.verbose:
        _log.setLevel(logging.DEBUG)
    else:
        _log.setLevel(logging.INFO)

    if options.quiet:
        _log.setLevel(logging.ERROR)

    _log.debug(args)

    if not len(args) == 2 and not options.action == 'discover':
        parser.print_help()
        sys.exit()

    transcoder = VideoTranscoder()

    if options.action == 'thumbnail':
        args.append(options.width)
        VideoThumbnailerMarkII(*args)
    elif options.action == 'video':
        def cb(data):
            print('I\'m a callback!')
        transcoder.transcode(*args, progress_callback=cb)
    elif options.action == 'discover':
        print transcoder.discover(*args)
