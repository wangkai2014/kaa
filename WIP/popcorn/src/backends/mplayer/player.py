# -*- coding: iso-8859-1 -*-
# $Id$
# -----------------------------------------------------------------------------
# player.py - mplayer backend
# -----------------------------------------------------------------------------
# kaa.popcorn - Generic Player API
# Copyright (C) 2008 Jason Tackaberry, Dirk Meyer
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
# -----------------------------------------------------------------------------

__all__ = [ 'MPlayer' ]

# python imports
import logging
import re
import os
import stat

# kaa imports
import kaa
import kaa.utils
from kaa.utils import property

# kaa.popcorn imports
from kaa.popcorn2.common import *
from kaa.popcorn2.config import config
from utils import *

# get logging object
log = logging.getLogger('popcorn.mplayer')

# Global constants
# regexp whose groups() is (vpos, apos, speed)
RE_STATUS = re.compile(r'(?:V:\s*([\d.]+)|A:\s*([\d.]+)\s\W).*\s([\d.]+x)? ')
RE_ERROR = re.compile(r'^(File not found|Failed to open|MPlayer interrupt|Unknown option|Error parsing)')

STREAM_INFO_MAP = { 
    'VIDEO_FORMAT': ('vfourcc', str),
    'VIDEO_CODEC': ('vcodec', str),
    'VIDEO_BITRATE': ('vbitrate', int),
    'VIDEO_WIDTH': ('width', int),
    'VIDEO_HEIGHT': ('height', int),
    'VIDEO_FPS': ('fps', float),
    'VIDEO_ASPECT': ('aspect', float),
    'AUDIO_FORMAT': ('afourcc', str),
    'AUDIO_CODEC': ('acodec', str),
    'AUDIO_BITRATE': ('abitrate', int),
    'AUDIO_NCH': ('channels', int),
    'LENGTH': ('length', float),
    'FILENAME': ('uri', str),
    'SEEKABLE': ('seekable', bool),
}


class MPlayer(object):

    def __init__(self, proxy):
        #self._proxy = kaa.weakref.weakref(proxy)
        self._proxy = proxy
        self._state = STATE_NOT_RUNNING
        # Internal error signal.  Not all errors emitted to this signal are
        # meant to be visible to the proxy.
        self._error_signal = kaa.Signal()
        self._error_message = None

        # A kaa.Process object if mplayer is running.
        self._child = None
        self._mp_cmd = config.mplayer.path
        self._reset_stream()

        # TODO: use these.
        self._filters_pre = []
        self._filters_add = []

        if not self._mp_cmd:
            self._mp_cmd = kaa.utils.which('mplayer')
            if not self._mp_cmd:
                raise PlayerError('No mplayer executable found in PATH')

        # Fetch info for this mplayer.  It's almost guaranteed that this
        # will returned a cached value, so it won't block.
        self._mp_info = get_mplayer_info(self._mp_cmd)
        if not self._mp_info:
            # It is extremely unlikely this will happen, because the backend manager
            # will alraedy have called get_mplayer_info and the proxy would not
            # have received us as a suitable player class if it failed.
            raise PlayerError("MPlayer at %s (found in PATH) isn't behaving as expected" % self._mp_cmd)


    #########################################
    # Properties

    @property
    def state(self):
        # The state property is not accessible from the outside, so we don't
        # need to worry about anyone messing with our state.
        return self._state

    @state.setter
    def state(self, value):
        if self._state != value:
            log.info('State change: %s -> %s', self._state, value)
            self._state = value

    @property
    def position(self):
        return self._position

    @property
    def width(self):
        return self._stream_info.get('width')

    @property
    def height(self):
        return self._stream_info.get('height')

    @property
    def aspect(self):
        return self._stream_info.get('aspect')

    @property
    def vfourcc(self):
        return self._stream_info.get('vfourcc')

    @property
    def afourcc(self):
        return self._stream_info.get('afourcc')

    @property
    def length(self):
        return self._stream_info.get('length')

    @property
    def uri(self):
        return self._stream_info.get('uri')

    @property
    def seekable(self):
        if self._stream_info.get('seekable'):
            # MPlayer's ID_SEEKABLE is not reliable, so if kaa.metadata says
            # the file is corrupt, treat that as authoritative.
            if (not hasattr(self._media, 'corrupt') or not self._media.corrupt):
                return True
        return False

    @property
    def audio_delay(self):
        return self._stream_info.get('audio_delay', 0.0)

    @audio_delay.setter
    def audio_delay(self, value):
        self._stream_info['audio_delay'] = -float(value)
        if self._child:
            self._slave_cmd('audio_delay %f 1' % -float(value))

    @property
    def cache(self):
        return self._stream_info.get('cache', 'auto')

    @cache.setter
    def cache(self, value):
        # Cache is not settable while MPlayer is running.
        self._stream_info['cache'] = value


    #########################################
    # Private Methods

    def _handle_child_exit(self, code):
        self._child = None
        if self.state in (STATE_PLAYING, STATE_PAUSED):
            # Child died when we didn't expect it to.  Adjust state now and
            # emit appropriate signals.
            cause = self._error_message if self._error_message else 'Unknown failure caused abort'
            log.error('MPlayer child aborted abnormally, state=%s: %s', self.state, cause)
            exc = PlayerError(cause)
            self._proxy._emit_finished(exc)
            self._proxy.signals['error'].emit(exc, self.state, STATE_NOT_RUNNING)
            self.state = STATE_NOT_RUNNING

        else:
            log.info('MPlayer child exited: state=%s', self.state)


    def _spawn(self, args, interactive=False):
        self._child = kaa.Process(self._mp_cmd)
        self._child.delimiter = ['\r', '\n']
        if interactive:
            self._child.stop_command = 'quit\nquit\n'

        self._child.signals['finished'].connect_weak(self._handle_child_exit)
        self._child.signals['readline'].connect_weak(self._handle_child_line)
        return self._child.start([ str(x) for x in args ])

    def _slave_cmd(self, cmd, *args):
        output = 'pausing_keep %s %s' % (cmd, ' '.join([ str(x) for x in args]))
        log.info('Slave cmd: %s', output)
        self._child.write(output.strip() + '\n')


    def _handle_child_line(self, line):
        #log.debug(line)
        # TODO: if we get ID_* other than ID_EXIT while playing, emit stream-changed,
        # but does this ever happen?

        if line.startswith('V:') or line.startswith('A:'):
            m = RE_STATUS.search(line)
            if not m:
                return

            old = self._position
            self._position = float((m.group(1) or m.group(2)).replace(',', '.'))
            if self._just_seeked:
                self._just_seeked = False
                log.info('MPlayer seeked to %f', self._position)
                self._proxy.signals['seek'].emit(old, self._position)
            elif self.state == STATE_PAUSED:
                self.state = STATE_PLAYING
                self._proxy.signals['play'].emit()
            elif self.state == STATE_OPEN:
                self.state = STATE_PLAYING
                self._proxy.signals['stream-changed'].emit()
                self._proxy.signals['start'].emit()
                self._proxy.signals['play'].emit()

            self._proxy.signals['position-changed'].emit(old, self._position)


        elif line.startswith('SEEK:'):
            # We've seeked, ensure we submit a seek
            self._just_seeked = True

        elif line.startswith('ID_PAUSED'):
            self.state = STATE_PAUSED
            self._proxy.signals['pause'].emit()

        elif line.startswith('ID_') and '=' in line:
            attr, value = line.rstrip().split('=', 1)
            attr, tp = STREAM_INFO_MAP.get(attr[3:], (None, None))
            if attr:
                self._stream_info[attr] = tp(value)

        elif line.startswith('EOF code'):
            self.state = STATE_NOT_RUNNING
            self._proxy._emit_finished(None)

        elif re.match(RE_ERROR, line):
            self._error_message = line
            self._error_signal.emit(PlayerError(line))


    def _reset_stream(self):
        """
        Resets stream parameters.
        """
        # Stream info as fetched by -identify as well as some custom attrs.
        # We initialize it with global defaults from the proxy.
        self._stream_info = {
            'audio_delay': self._proxy.audio_delay,
            'deinterlace': self._proxy.deinterlace,
            'cache': self._proxy.cache
        }
        # Position in seconds in stream (float)
        self._position = 0.0
        # Start seek position, set when seek() is called in STATE_OPEN
        self._ss_seek = None
        # Flag indicating we finished seeking; next status line cause
        # seek signal emission.
        self._just_seeked = False
        self._error_message = None


    @kaa.coroutine()
    def _handle_fatal_error(self, msg):
        # Store current state in case we call self.stop() which will
        # modify state.  We want to pass the current state when we emit
        # the error signal.
        orig_state = self.state

        # Stop MPlayer process.  In normal cases (that is, where MPlayer
        # isn't hung on the file), the child process is probably exited by
        # now, we just haven't reaped it. Before raising the open failure
        # exception, we'll wait for the child to die.  In the worst case,
        # where MPlayer is stuck and kill -15 doesn't dispense with it,
        # this should take not longer than 6 seconds.
        yield self.stop()

        # At this point child is dead and state is STATE_NOT_RUNNING (from
        # stop()).  Construct exception and emit catch-all error signal.
        exc = PlayerError(msg)
        self._proxy.signals['error'].emit(exc, orig_state, STATE_NOT_RUNNING)
        raise exc


    @kaa.coroutine()
    def _wait_for_signals(self, *signals, **opts):
        signals = self._proxy.signals.subset(*signals).values()
        ip = kaa.InProgressAny(self._child, self._error_signal, *signals)
        # If proxy calls abort() on IP yielded by the open() coroutine, then
        # this IPAny we're about to yield will get aborted too, just before
        # this coroutine is aborted.  Make the IPAny abortable.
        ip.abortable = True
        n, args = yield ip

        if n == 1 or (n == 0 and args != 0):
            # Either error signal was emitted or MPlayer returned non-zero.
            cause = args.message if n else '%s failed for unknown reason' % args#opts['task']
            yield self._handle_fatal_error(cause)
        yield n-2


    #########################################
    # Public Methods

    @precondition(states=STATE_NOT_RUNNING)
    @kaa.coroutine()
    def open(self, media):
        """
        Opens an MRL.

        :param media: the object representing the file to load.
        :type media: :class:`kaa.metadata.Media`
        :returns: :class:`~kaa.InProgress`
        
        Required state is STATE_NOT_RUNNING, which we expect the proxy to
        enforce.  State is immediately changed to STATE_OPENING.  The returned
        InProgress is finished and state set to STATE_OPEN upon successful open
        of the mrl.  The open may be aborted (when in STATE_OPENING) by calling
        stop().
        """

        log.debug('mplayer backend: opening %s', media.url)

        args = ArgumentList()
        if media.scheme == 'dvd':
            file, title = re.search('(.*?)(\/\d+)?$', media.url[4:]).groups()
            if file.replace('/', ''):
                if not os.path.exists(file):
                    raise ValueError('Invalid ISO file: %s' % file)
                args.add(dvd_device=os.path.normpath(file))
            args.append('dvd://%s' % (title[1:] if title else ''))
        else:
            args.append(media.url)

        # Universal mplayer args
        args.extend('-nolirc -nojoystick -identify')
        media._mplayer_args = args[:]
        self._media = media
        self._reset_stream()
        self.state = STATE_OPENING

        # The 'open' function is used to open the stream and provide
        # information about it. After that, the caller can still change stuff
        # before calling play. MPlayer doesn't work that way so we have to run
        # mplayer with -identify first.
        args.extend('-vo null -ao null -frames 0 -nocache -demuxer lavf')
        self._spawn(args)

        yield self._wait_for_signals(task='Open')

        # If we're here, identify was successful, so we're open for business.
        self.state = STATE_OPEN
        self._proxy.signals['open'].emit()


    @precondition(states=STATE_OPEN)
    @kaa.coroutine()
    def play(self):
        vf = []
        args = self._media._mplayer_args
        args.extend('-slave -v -osdlevel 0 -fixed-vo -identify')

        if self.audio_delay:
            args.add(delay=-self.audio_delay)
        if self.cache == 'none':
            args.add(nocache=True)
        elif isinstance(self.cache, (long, float, int)) or self.cache.isdigit():
            args.add(cache=self.cache)
        if self._ss_seek:
            args.add(ss=self._ss_seek)
            self._ss_seek = None

        if self._media.get('corrupt'):
            # Index for the given file is corrupt.  Must add -idx to allow
            # seeking.  FIXME: for large filesthis can take a while.  We
            # should: 1. provide progress feedback, 2. use -saveidx to keep
            # the index for next time.
            args.append('-idx')

        if vf:
            args.add(vf=','.join(vf))


        log.debug('Starting MPlayer with args: %s', str(args))
        self._spawn(args, interactive=True)

        yield self._wait_for_signals('play', task='Play')

        # Play has begun successfully.  _handle_child_line() will already
        # have set state to STATE_PLAYING.


    @kaa.coroutine(policy=kaa.POLICY_SINGLETON)
    def stop(self):
        log.info('Stopping mplayer, state=%s', self.state)
        if self.state == STATE_NOT_RUNNING:
            # Nothing to do.  Don't need to test that state is STATE_STOPPING,
            # because POLICY_SINGLETON makes sure we don't reenter until stopped.
            yield True

        log.info('Stopping mplayer (running: %s)', 'yes' if self._child else 'no')
        orig_state = self.state
        self.state = STATE_STOPPING
        if self._child:
            # Tell child to quit; this will issue quit slave command twice in
            # case mplayer is paused.
            yield self._child.stop()
            # Once we get here, self._child is None.

        # Child is dead, adjust state.
        self.state = STATE_NOT_RUNNING
        self._reset_stream()
        if orig_state in (STATE_PLAYING, STATE_PAUSED):
            self._proxy.signals['stop'].emit()


    @precondition(states=STATE_PLAYING)
    @kaa.coroutine(policy=kaa.POLICY_SINGLETON)
    def pause(self):
        self._slave_cmd('pause')
        yield self._wait_for_signals('pause', task='Pause')
 

    @precondition(states=STATE_PAUSED)
    @kaa.coroutine(policy=kaa.POLICY_SINGLETON)
    def resume(self):
        self._slave_cmd('pause')
        yield self._wait_for_signals('play', task='Resume')


    @precondition(states=(STATE_OPEN, STATE_PLAYING, STATE_PAUSED))
    @kaa.coroutine(policy=kaa.POLICY_PASS_LAST)
    def seek(self, value, type, last=None):
        if self._state == STATE_OPEN:
            if type == SEEK_PERCENTAGE:
                # Translate to absolute position.
                value = self._stream_info['length'] * value / 100
            self._ss_seek = value
            yield None
            
        s = [SEEK_RELATIVE, SEEK_PERCENTAGE, SEEK_ABSOLUTE]
        self._slave_cmd('seek', value, s.index(type))
        if last:
            # seek has already been called.  wait for the last week
            # to complete before we terminate this coroutine.
            yield last
        # Now the next seek event from mplayer is ours.  Wait for that one. 
        yield self._wait_for_signals('seek', task='Seek')
        # Done seeking.  Return current position to caller.
        yield self.position


    def reset(self):
        """
        Proxy is going to reuse us for a new file.  Reset all stream parameters.
        """
        # Proxy ensures reset() does not get called until stop() is finished.  If
        # we're stopped, stream is already reset.  So reset() is a no-op for this
        # backend.
        print "Mplayer: reset"


    def release(self):
        """
        Proxy is going to use a different backend for a new file.  Must release
        all resources so the new backend can grab them.
        """
        # Proxy ensures release() does not get called until stop() is finished.  If
        # we're stopped, MPlayer is exited and therefore obviously is not holding
        # any resources.  So release() is a no-op for this backend.
        print 'mplayer: release'
