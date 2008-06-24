# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# timeline.py - Timeline Classes
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# kaa-candy - Third generation Canvas System using Clutter as backend
# Copyright (C) 2008 Dirk Meyer, Jason Tackaberry
#
# Please see the file AUTHORS for a complete list of authors.
#
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version
# 2.1 as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301 USA
#
# -----------------------------------------------------------------------------

__all__ = [ 'Timeline', 'MasterTimeline' ]

import sys
# check if kaa.candy is initialized in the thread
if not 'clutter' in sys.modules.keys():
    raise RuntimeError('kaa.candy not initialized')

import clutter

#: Basic Timeline class from clutter
Timeline = clutter.Timeline

class MasterTimeline(object):
    """
    Python implementation of clutter.Score since the clutter.Score
    prints warnings.
    """
    def __init__(self):
        """
        Create a new MasterTimeline
        """
        self._timelines = []
        self._signals = []

    def append(self, timeline, parent=None):
        """
        Append a timeline
        """
        if parent:
            signal = parent.connect('completed', lambda x: timeline.start())
            self._signals.append((parent, signal))
        self._timelines.append(timeline)

    def start(self):
        """
        Start the MasterTimeline
        """
        self._timelines[0].start()

    def stop(self):
        """
        Stop the MasterTimeline
        """
        for timeline in self._timelines:
            if timeline.is_playing():
                timeline.stop()

    def is_playing(self):
        """
        Return True if at least one child timeline is_playing()
        """
        for timeline in self._timelines:
            if timeline.is_playing():
                return True
        return False

    def __del__(self):
        """
        Delete MasterTimeline by disconnecting the children
        """
        for parent, signal in self._signals:
            parent.disconnect(signal)
