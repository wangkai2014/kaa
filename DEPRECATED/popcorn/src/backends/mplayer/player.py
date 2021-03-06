# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# mplayer/player.py - mplayer backend
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# kaa.popcorn - Generic Player API
# Copyright (C) 2006 Jason Tackaberry, Dirk Meyer
#
# Please see the file AUTHORS for a complete list of authors.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MER-
# CHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# -----------------------------------------------------------------------------

# python imports
import logging
import os
import re
import string
import stat
import threading
import struct

# kaa imports
import kaa
from kaa import shm
import kaa.utils
import kaa.display

# kaa.popcorn base imports
from kaa.popcorn.backends.base import MediaPlayer, runtime_policy, \
     APPLY_ALWAYS, IGNORE_UNLESS_PLAYING, DEFER_UNTIL_PLAYING
from kaa.popcorn.ptypes import *
from kaa.popcorn.config import config

# special mplayer ipc handling
from ipc import ChildProcess

BUFFER_UNLOCKED = 0x10
BUFFER_LOCKED = 0x20

# get logging object
log = logging.getLogger('popcorn.mplayer')
childlog = logging.getLogger('popcorn.child').debug

# A cache holding values specific to an MPlayer executable (version,
# filter list, video/audio driver list, input keylist).  This dict is
# keyed on the full path of the MPlayer binary.
_cache = {}

def _get_mplayer_info(path, callback = None, mtime = None):
    """
    Fetches info about the given MPlayer executable.  If the values are
    cached and the cache is fresh, it returns a dict immediately.  If it
    needs to load MPlayer to fetch the values and callback is specified,
    it does so in a thread, and calls callback with the results on
    completion.  If callback is None and no information is in the cache,
    this function blocks.

    If 'mtime' is not None, it means we've called ourself as a thread.
    """

    if not mtime:
        # Fetch the mtime of the binary
        try:
            mtime = os.stat(path)[stat.ST_MTIME]
        except (OSError, TypeError):
            return None

        if path in _cache and _cache[path]["mtime"] == mtime:
            # Cache isn't stale, so return that.
            return _cache[path]

        if callback:
            # We need to run MPlayer to get these values.  Create a signal,
            # call ourself as a thread, and return the signal back to the
            # caller.
            async = kaa.ThreadCallable(_get_mplayer_info, path, None, mtime)()
            # ThreadCallable class ensures the callbacks get invoked in the main
            # thread.
            async.connect_both(callback, callback)
            return None

    # At this point we're running in a thread.
    info = {
        "version": None,
        "mtime": mtime,
        "video_filters": {},
        "video_drivers": {},
        "audio_filters": {},
        "audio_drivers": {},
        "keylist": []
    }

    groups = {
        'video_filters': ('Available video filters', r'\s*(\w+)\s+:\s+(.*)'),
        'video_drivers': ('Available video output', r'\s*(\w+)\s+(.*)'),
        'audio_filters': ('Available audio filters', r'\s*(\w+)\s+:\s+(.*)'),
        'audio_drivers': ('Available audio output', r'\s*(\w+)\s+(.*)')
    }
    curgroup = None
    for line in os.popen('%s -vf help -af help -vo help -ao help' % path):
        # Check version
        if line.startswith("MPlayer "):
            info['version'] = line.split()[1]
        # Find current group.
        for group, (header, regexp) in groups.items():
            if line.startswith(header):
                curgroup = group
                break
        if not curgroup:
            continue

        # Check regexp
        m = re.match(groups[curgroup][1], line.strip())
        if not m:
            continue

        if len(m.groups()) == 2:
            info[curgroup][m.group(1)] = m.group(2)
        else:
            info[curgroup].append(m.group(1))

    # Another pass for key list.
    for line in os.popen('%s -input keylist' % path):
        # Check regexp
        m = re.match(r'^(\w+)$', line.strip())
        if not m:
            continue
        info['keylist'].append(m.group(1))


    _cache[path] = info
    return info


class MPlayer(MediaPlayer):

    RE_STATUS = re.compile("V:\s*([\d+\.]+)|A:\s*([\d+\.]+)\s\W")
    RE_SWS = re.compile("^SwScaler: [0-9]+x[0-9]+ -> ([0-9]+)x([0-9]+)")

    def __init__(self, properties):
        super(MPlayer, self).__init__(properties)
        self.state = STATE_NOT_RUNNING
        self._mp_cmd = config.mplayer.path
        if not self._mp_cmd:
            self._mp_cmd = kaa.utils.which("mplayer")

        if not self._mp_cmd:
            raise PlayerError, "No MPlayer executable found in PATH"

        self._mplayer = None

        self._filters_pre = []
        self._filters_add = []

        self._mp_info = _get_mplayer_info(self._mp_cmd, self._handle_mp_info)
        self._check_new_frame_t = kaa.WeakTimer(self._check_new_frame)
        self._cur_outbuf_mode = [True, False, None] # vo, shmem, size


    def __del__(self):
        if self._frame_shmem:
            self._frame_shmem.detach()
        if self._osd_shmem:
            self._osd_shmem.detach()


    def _handle_mp_info(self, info, exception=None, traceback=None):
        if exception is not None:
            self.state = STATE_NOT_RUNNING
            # TODO: handle me
            raise info
        self._mp_info = info



    #
    # child IO
    #

    def _child_handle_line(self, line):
        if re.search("@@@|outbuf|overlay", line, re.I):
            childlog(line)
        elif line[:2] not in ("A:", "V:"):
            childlog(line)

        if line.startswith("V:") or line.startswith("A:"):
            m = MPlayer.RE_STATUS.search(line)
            if m:
                old_pos = self.position
                p = (m.group(1) or m.group(2)).replace(",", ".")
                self.position = float(p)
                # if self.position - old_pos < 0 or \
                # self.position - old_pos > 1:
                # self.signals["seek"].emit(self.position)

                # XXX this logic won't work with seek-while-paused patch; state
                # will be "playing" after a seek.
                if self.state == STATE_PAUSED:
                    self.state = STATE_PLAYING
                if self.state == STATE_OPEN:
                    self.set_frame_output_mode()
                    self._mplayer.sub_visibility(False)
                    self.state = STATE_PLAYING
                    self.signals["stream_changed"].emit()

        elif line.startswith("  =====  PAUSE"):
            self.state = STATE_PAUSED

        elif line.startswith("ID_") and line.find("=") != -1:
            attr, value = line.split('=', 1)
            attr = attr[3:]
            info = { "VIDEO_FORMAT": ("vfourcc", str),
                     "VIDEO_BITRATE": ("vbitrate", int),
                     "VIDEO_WIDTH": ("width", int),
                     "VIDEO_HEIGHT": ("height", int),
                     "VIDEO_FPS": ("fps", float),
                     "VIDEO_ASPECT": ("aspect", float),
                     "AUDIO_FORMAT": ("afourcc", str),
                     "AUDIO_CODEC": ("acodec", str),
                     "AUDIO_BITRATE": ("abitrate", int),
                     "AUDIO_NCH": ("channels", int),
                     "LENGTH": ("length", float),
                     "FILENAME": ("filename", str) }
            if attr in info:
                self.streaminfo[info[attr][0]] = info[attr][1](value)

        elif line.startswith("Movie-Aspect"):
            aspect = line[16:].split(":")[0].replace(",", ".")
            if aspect[0].isdigit():
                self.streaminfo["aspect"] = float(aspect)

        elif line.startswith("VO:"):
            m = re.search("=> (\d+)x(\d+)", line)
            if m:
                vo_w, vo_h = int(m.group(1)), int(m.group(2))
                if "aspect" not in self.streaminfo or \
                       self.streaminfo["aspect"] == 0:
                    # No aspect defined, so base it on vo size.
                    self.streaminfo["aspect"] = vo_w / float(vo_h)

        elif line.startswith("overlay:") and line.find("reusing") == -1:
            m = re.search("(\d+)x(\d+)", line)
            if m:
                width, height = int(m.group(1)), int(m.group(2))
                try:
                    if self._osd_shmem:
                        self._osd_shmem.detach()
                except shm.error:
                    pass
                self._osd_shmem = shm.memory(\
                    shm.getshmid(self._osd_shmkey))
                self._osd_shmem.attach()

                self.signals["osd_configure"].emit(\
                    width, height, self._osd_shmem.addr + 16, width, height)

        elif line.startswith("outbuf:") and line.find("shmem key") != -1:
            try:
                if self._frame_shmem:
                    self._frame_shmem.detach()
            except shm.error:
                pass
            self._frame_shmem = shm.memory(shm.getshmid(self._frame_shmkey))
            self._frame_shmem.attach()
            self.set_frame_output_mode()  # Sync

        elif line.startswith("EOF code"):
            if self.state in (STATE_PLAYING, STATE_PAUSED):
                # The player may be idle bow, but we can't set the
                # state. If we do, generic will start a new file while
                # the mplayer process is still running and that does
                # not work. Unless we reuse mplayer proccesses we
                # don't react on EOF and only handle the dead
                # proccess.
                # self.state = STATE_IDLE
                pass

        elif line.startswith("FATAL:"):
            log.error(line.strip())


    def _child_exited(self, exitcode):
        log.info('mplayer exited')
        self.state = STATE_NOT_RUNNING


    def _is_alive(self):
        return self._mplayer and self._mplayer.running



    #
    # Methods for MediaPlayer subclasses
    #

    def open(self, media):
        """
        Open media.
        """
        if self.state != STATE_NOT_RUNNING:
            raise RuntimeError('mplayer not in STATE_NOT_RUNNING')

        args = []
        if media.scheme == "dvd":
            file, title = re.search("(.*?)(\/\d+)?$", media.url[4:]).groups()
            if file.replace('/', ''):
                if not os.path.isfile(file):
                    raise ValueError, "Invalid ISO file: %s" % file
                args.extend(('-dvd-device', file))
            args.append("dvd://")
            if title:
                args[-1] += title[1:]
        else:
            args.append(media.url)

        self._media = media
        self._media.mplayer_args = args
        self.state = STATE_OPENING

        # We have a problem at this point. The 'open' function is used to
        # open the stream and provide information about it. After that, the
        # caller can still change stuff before calling play. Mplayer doesn't
        # work that way so we have to run mplayer with -identify first.
        args = "-nolirc -nojoystick -identify -vo null -ao null -frames 0 -nocache"
        ident = kaa.Process(self._mp_cmd)
        ident.delimiter = ['\n', '\r']
        signal = ident.start(args.split(' ') + self._media.mplayer_args)
        signal.connect_weak(self._ident_exited)
        ident.signals['readline'].connect_weak(self._child_handle_line)


    def _ident_exited(self, code):
        """
        mplayer -identify finished
        """
        self.state = STATE_OPEN


    def configure_video(self):
        """
        Configure arguments and filter for video.
        """
        # get argument and filter list
        args, filters = self._mplayer.args, self._mplayer.filters

        # create filter list
        filters.extend(self._filters_pre[:])
        # FIXME: all this code seems to work. But I guess it has
        # some problems when we don't have an 1:1 pixel aspect
        # ratio on the monitor and using software scaler.

        aspect, dsize = self.aspect
        if hasattr(self._window, 'get_size'):
            size = self._window.get_size()
        else:
            # kaa.candy widget
            size = self._window.width, self._window.height
        # This may be needed for some non X based displays
        args.add(screenw=size[0], screenh=size[1])

        if not self._properties['scale'] == SCALE_IGNORE:
            # Expand to fit the given aspect. In scaled mode we don't
            # do that which will result in a scaled image filling
            # the whole screen
            filters.append('expand=:::::%s/%s' % tuple(aspect))
            # The expand filter has some strange side-effect on 4:3 content
            # on a 16:9 screen. With software scaling instead of black bars
            # on both sides you see garbage, without sws and xv output mplayer
            # uses gray bars. The following line removed that.
            args.append('-noslices')
            
        # FIXME: this only works if the window has the the aspect
        # as the full screen. In all other cases the window is not
        # fully used but at least with black bars.
        if self._properties['scale'] == SCALE_ZOOM:
            # This DOES NOT WORK as it should. The hardware scaler
            # will ignore the settings and keep aspect and does
            # not crop as default.  When using vo x11 and software
            # scaling, this lines do what they are supposed to do.
            filters.append('dsize=%s:%s:1' % size)
        else:
            # scale to window size
            # FIXME: add SCALE_4_3 and SCALE_16_9
            filters.append('dsize=%s:%s:0' % size)

        # add software scaler based on dsize arguments
        if self._properties.get('software-scaler') or \
               config.video.driver in ('x11',):
            filters.append('scale=0:0')
            args.add(sws=2)

        # add postprocessing
        if self._properties.get('postprocessing'):
            filters.append('pp')
            args.add(autoq=100)

        try:
            cpus = kaa.utils.get_num_cpus()
            args.add(lavdopts='fast:skiploopfilter=nonref:threads=%d' % cpus)
        except RuntimeError:
            pass

        # set monitor aspect (needed sometimes, not sure when and why)
        args.add(monitoraspect='%s:%s' % tuple(aspect))

        filters += self._filters_add
        #if 'overlay' in self._mp_info['video_filters']:
        #    filters.append("overlay=%s" % self._osd_shmkey)

        if isinstance(self._window, kaa.display.X11Window):
            if config.mplayer.embedded:
                args.add(wid="0x%x" % self._window.get_id())
            else:
                args.append('-fs')
            display = self._window.get_display().get_string()
            args.add(vo=config.video.driver, display=display,
                     colorkey=config.video.colorkey)
        elif self._window:
            args.append('-fs')
            args.add(vo=config.video.driver, colorkey=config.video.colorkey)
        else:
            args.add(vo='null')


    def configure_audio(self):
        """
        Configure arguments and filter for video.
        """
        # get argument and filter list
        args, filters = self._mplayer.args, self._mplayer.filters

        if config.audio.passthrough:
            args.add(ac='hwac3,hwdts,%s' % config.mplayer.audiocodecs)
        else:
            if config.mplayer.audiocodecs:
                args.add(ac='%s' % config.mplayer.audiocodecs)
            args.add(channels=config.audio.channels)

        args.add(ao=config.audio.driver)

        if config.audio.driver == 'alsa':
            args[-1] += ":noblock"
            n_channels = self.streaminfo.get('channels')
            if self.streaminfo.get('acodec') in ('a52', 'hwac3', 'ffdts', 'hwdts'):
                device = config.audio.device.passthrough
            elif n_channels == 1:
                device = config.audio.device.mono
            elif n_channels <= 4:
                device = config.audio.device.surround40
            elif n_channels <= 6:
                device = config.audio.device.surround51
            else:
                device = config.audio.device.stereo
            if device != '':
                args[-1] += ':device=' + device.replace(':', '=')

        # set property audio filename
        if self._properties.get('audio-filename'):
            args.add(audiofile=self._properties.get('audio-filename'))

        # set property audio track
        if self._properties.get('audio-track') is not None:
            args.add(aid=self._properties.get('audio-track'))


    def play(self):
        """
        Start playback.
        """
        log.debug('mplayer start playback')

        # we know that self._mp_info has to be there or the object would
        # not be selected by the generic one. FIXME: verify that!
        assert(self._mp_info)

        # create mplayer object
        self._mplayer = ChildProcess(self._mp_cmd, gdb = log.getEffectiveLevel() == logging.DEBUG)

        # get argument and filter list
        args, filters = self._mplayer.args, self._mplayer.filters

        if 'x11' in self._mp_info['video_drivers']:
            args.append('-nomouseinput')

        #if 'outbuf' in self._mp_info['video_filters']:
        #    filters.append("outbuf=%s:yv12" % self._frame_shmkey)

        if self._properties['deinterlace'] == True or \
               (self._properties['deinterlace'] == 'auto' and \
                self._media.get('interlaced')):
            # add deinterlacer
            filters.append(config.mplayer.deinterlacer)


        if self._media.get('corrupt'):
            # File marked as corrupt. This happens for avi and mkv files
            # with no index. To make seeking work, add -idx
            args.append('-idx')
            
        # FIXME: self._filters_pre / add doesn't get included if no window.
        if self._window:
            self.configure_video()
        else:
            args.add(vo='null')

        self.configure_audio()

        # There is no way to make MPlayer ignore keys from the X11 window.  So
        # this hack makes a temp input file that maps all keys to a dummy (and
        # non-existent) command which causes MPlayer not to react to any key
        # presses, allowing us to implement our own handlers.  The temp file is
        # deleted once MPlayer has read it.
        tempfile = kaa.tempfile('popcorn/mplayer-input.conf')
        if not os.path.isfile(tempfile):
            keys = filter(lambda x: x not in string.whitespace, string.printable)
            keys = list(keys) + self._mp_info["keylist"]
            fd = open(tempfile, 'w')
            for key in keys:
                fd.write("%s noop\n" % key)
            fd.close()
        # only prevent input if the player is embedded
        if config.mplayer.embedded:
            args.add(input='conf=%s' % tempfile)

        # set properties subtitle filename and subtitle track
        if self._properties.get('subtitle-filename'):
            sub = self._properties.get('subtitle-filename')
            if os.path.splitext(sub)[1].lower() in ('.ifo', '.idx', '.sub'):
                args.add(vobsub=os.path.splitext(sub)[0],
                         vobsubid=self._properties.get('subtitle-track'))
            else:
                args.add(subfile=sub)
        elif self._properties.get('subtitle-track') != None:
            args.add(sid=self._properties.get('subtitle-track'))

        if self._properties.get('cache') == 'auto':
            if self._media.scheme == "dvd":
                args.add(cache=8192)
            if self._media.scheme == "vcd":
                args.add(cache=4096)
            if self._media.scheme == "dvb":
                args.add(cache=1024)
            if self._media.scheme == "http":
                args.add(cache=8192, cache_min=5)
            else:
                args.add(cache=5000)
        else:
            args.add(cache=self._properties.get('cache'))

        # connect to signals
        self._mplayer.signals['readline'].connect_weak(self._child_handle_line)

        # start playback
        self._mplayer.start(self._media).connect_weak(self._child_exited)


    def stop(self):
        """
        Stop playback.
        """
        if self._mplayer:
            self._mplayer.stop()
            self.state = STATE_SHUTDOWN


    def pause(self):
        """
        Pause playback.
        """
        self._mplayer.pause()


    def resume(self):
        """
        Resume playback.
        """
        self._mplayer.pause()


    def seek(self, value, type):
        """
        SEEK_RELATIVE, SEEK_ABSOLUTE and SEEK_PERCENTAGE.
        """
        s = [SEEK_RELATIVE, SEEK_PERCENTAGE, SEEK_ABSOLUTE]
        self._mplayer.seek(value, s.index(type))


    #
    # Property settings
    #

    @runtime_policy(DEFER_UNTIL_PLAYING)
    def _set_prop_audio_delay(self, delay):
        """
        Sets audio delay. Positive value defers audio by delay.
        """
        self._mplayer.audio_delay(-delay, 1)


    @runtime_policy(IGNORE_UNLESS_PLAYING)
    def _set_prop_audio_track(self, id):
        """
        Change audio track (mpeg and mkv only)
        """
        self._mplayer.switch_audio(id)


    @runtime_policy(IGNORE_UNLESS_PLAYING)
    def _set_prop_subtitle_track(self, id):
        """
        Change subtitle track
        """
        self._mplayer.sub_select(id)


    @runtime_policy(IGNORE_UNLESS_PLAYING)
    def _set_prop_subtitle_filename(self, filename):
        """
        Change subtitle filename
        """
        self._mplayer.sub_load(filename)


    @runtime_policy(DEFER_UNTIL_PLAYING)
    def _set_prop_subtitle_visibility(self, enabled):
        """
        Change subtitle visibility
        """
        self._mplayer.sub_visibility(int(enabled))

    #
    # Methods for filter handling (not yet in generic and base)
    #
    # FIXME: no distinction between audio and video filters

    def prepend_filter(self, filter):
        """
        Add filter to the prepend list.
        """
        self._filters_pre.append(filter)


    def append_filter(self, filter):
        """
        Add filter to the normal filter list.
        """
        self._filters_add.append(filter)


    def get_filters(self):
        """
        Return all filter set.
        """
        return self._filters_pre + self._filters_add


    def remove_filter(self, filter):
        """
        Remove filter for filter list.
        """
        for l in (self._filters_pre, self._filters_add):
            if filter in l:
                l.remove(filter)


    #
    # Methods and helper for MediaPlayer subclasses for CAP_OSD
    #

    def osd_can_update(self):
        """
        Returns True if it is safe to write to the player's shared memory
        buffer used for OSD, and False otherwise.  If this buffer is written
        to even though this function returns False, the OSD may exhibit
        corrupt output or tearing during animations.
        See generic.osd_can_update for details.
        """
        if not self._osd_shmem:
            return False

        try:
            if ord(self._osd_shmem.read(1)) == BUFFER_UNLOCKED:
                return True
        except shm.error:
            self._osd_shmem.detach()
            self._osd_shmem = None

        return False



    def osd_update(self, alpha = None, visible = None, invalid_regions = None):
        """
        Updates the OSD of the player based on the given argments:
        See generic.osd_update for details.
        """
        cmd = []
        if alpha != None:
            cmd.append("alpha=%d" % alpha)
        if visible != None:
            cmd.append("visible=%d" % int(visible))
        if invalid_regions:
            for (x, y, w, h) in invalid_regions:
                cmd.append("invalidate=%d:%d:%d:%d" % (x, y, w, h))
        self._mplayer.overlay(','.join(cmd))
        self._overlay_set_lock(BUFFER_LOCKED)


    def _overlay_set_lock(self, byte):
        try:
            if self._osd_shmem and self._osd_shmem.attached:
                self._osd_shmem.write(chr(byte))
        except shm.error:
            self._osd_shmem.detach()
            self._osd_shmem = None



    #
    # Methods and helper for MediaPlayer subclasses for CAP_CANVAS
    #


    def set_frame_output_mode(self, vo = None, notify = None, size = None):
        """
        Controls if and how frames are delivered via the 'frame' signal, and
        whether or not frames are drawn to the vo driver's video window.
        See generic.set_frame_output_mode for details.
        """
        if vo != None:
            self._cur_outbuf_mode[0] = vo
        if notify != None:
            self._cur_outbuf_mode[1] = notify
            if notify:
                self._check_new_frame_t.start(0.01)
            else:
                self._check_new_frame_t.stop()
        if size != None:
            self._cur_outbuf_mode[2] = size

        if not self._is_alive():
            return

        mode = { (False, False): 0, (True, False): 1,
                 (False, True): 2, (True, True): 3 }
        mode = mode[tuple(self._cur_outbuf_mode[:2])]

        size = self._cur_outbuf_mode[2]
        if size == None:
            self._mplayer.outbuf(mode)
        else:
            self._mplayer.outbuf(mode, size[0], size[1])


    def unlock_frame_buffer(self):
        """
        Unlocks the frame buffer provided by the last 'frame' signal
        See generic.unlock_frame_buffer for details.
        """
        try:
            self._frame_shmem.write(chr(BUFFER_UNLOCKED))
        except shm.error:
            self._frame_shmem.detach()
            self._frame_shmem = None


    def _check_new_frame(self):
        if not self._frame_shmem:
            return

        try:
            lock, width, height, aspect = \
                  struct.unpack("hhhd", self._frame_shmem.read(16))
        except shm.error:
            self._frame_shmem.detach()
            self._frame_shmem = None
            return

        if lock & BUFFER_UNLOCKED:
            return

        if width > 0 and height > 0 and aspect > 0:
            self.signals["frame"].emit(\
                width, height, aspect, self._frame_shmem.addr + 16, "yv12")
