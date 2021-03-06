# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# device.py - General Device Wrapper
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# kaa-record - A recording module
# Copyright (C) 2007 S�nke Schwardt, Dirk Meyer
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
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

__all__ = [ 'Device' ]

# python imports
import logging

# gstreamer imports
import pygst
pygst.require('0.10')
import gst

# kaa.record imports
import dvb

# get logging object
log = logging.getLogger('record.gstreamer')

class Device(object):
    """
    kaa.record device.
    """
    def __init__(self, device):

        # create gstreamer pipline
        self.pipeline = gst.Pipeline()
        self.pipeline.get_bus().add_watch(self._gst_event)

        if device.startswith('dvb'):
            self.device = dvb.DVBsrc()
            self.device.set_property('adapter', int(device[3:]))

        self.pipeline.add(self.device)
        # FIXME: set to playing when needed
        self.pipeline.set_state(gst.STATE_PLAYING)


    def _gst_event(self, bus, message):
        """
        Internal gstreamer debug for this pipeline.
        """
        t = message.type
        if t == gst.MESSAGE_EOS:
            log.info('EOS')
        elif t == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            log.error('%s: %s', err, debug)
        else:
            log.info(str(message))
        return True


    def get_status(self):
        """
        Return status information of the device.
        """
        return self.device.get_property('status')


    def has_signal(self):
        """
        Return True if the device has a lock on the signal and is
        ready for recording.
        """
        return self.device.get_property('has_signal')


    def start_recording(self, channel, output):
        """
        Start a recording.
        """
        element = output.element
        self.pipeline.add(element)
        element.set_state(gst.STATE_PLAYING)
        sink = element.get_pad('sink')
        # tune to the channel
        self.device.set_property('channel', channel)
        # FIXME: Clean up needed. Which apid should be used? How to handle
        # analog cards without pids.
        pids = int(channel.config['vpid']), int(channel.config['apids'][0][0])
        self.device.get_request_pad(*pids).link(sink)


    def stop_recording(self, output):
        """
        Stop a recording.
        """
        element = output.element
        pad = element.get_pad('sink')
        peer = pad.get_peer()
        peer.unlink(pad)
        self.device.remove_pad(peer)
        element.unparent()
        element.set_state(gst.STATE_NULL)
