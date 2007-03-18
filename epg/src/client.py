# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# client.py - client part of the epg
# -----------------------------------------------------------------------------
# $Id$
# -----------------------------------------------------------------------------
# kaa.epg - EPG Database
# Copyright (C) 2004-2006 Jason Tackaberry, Dirk Meyer, Rob Shortt
#
# First Edition: Jason Tackaberry <tack@sault.org>
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

__all__ = ['Client']

# python imports
import logging

# kaa imports
import kaa.db
import kaa.rpc
import kaa.notifier
from kaa.notifier import Signal, OneShotTimer, execute_in_timer

# kaa.epg imports
from channel import Channel
from program import Program
from util import cmp_channel

# get logging object
log = logging.getLogger('epg')

DISCONNECTED, CONNECTING, CONNECTED = range(3)

def yield_execution_while_connecting():
    """
    Decorator that wraps kaa.notifier.yield_execution, raising an exception if
    the client is disconnected, YieldContinue if the client is in the process
    of connecting, or the actual return value of the decorated function if the
    client is connected.
    """
    def decorator(func):
        def newfunc(client, *args, **kwargs):
            if client.status == DISCONNECTED:
                raise SystemError('Client is disconnected')
            while client.status == CONNECTING:
                yield kaa.notifier.YieldContinue
            yield func(client, *args, **kwargs)

        newfunc.func_name = func.func_name
        return kaa.notifier.yield_execution()(newfunc)
    return decorator

       

class Client(object):
    """
    EPG client class to access the epg on server side.
    """
    def __init__(self):
        self.status = DISCONNECTED
        self.server = None

        self._channels_list = []
        self.signals = {
            "updated": Signal(),
            "connected": Signal(),
            "disconnected": Signal()
        }

        self._channels_by_name = {}
        self._channels_by_db_id = {}
        self._channels_by_tuner_id = {}
        self._channels_list = []



    def connect(self, server_or_socket, auth_secret = ''):
        """
        Connect to EPG server.
        """
        self.status = CONNECTING
        self.server = kaa.rpc.Client(server_or_socket, auth_secret = auth_secret)
        self.server.connect(self)
        self.server.signals['closed'].connect_weak(self._handle_disconnected)

        
    def _handle_disconnected(self):
        """
        Signal callback when server disconnects.
        """
        log.debug('kaa.epg client disconnected')
        self.status = DISCONNECTED
        self.signals["disconnected"].emit()
        self.server = None


    @kaa.rpc.expose('guide.update')
    def _handle_guide_update(self, (epgdata, max_program_length, num_programs)):
        """
        (re)load some static information
        """
        self._channels_by_name = {}
        self._channels_by_db_id = {}
        self._channels_by_tuner_id = {}
        self._channels_list = []

        for row in epgdata:
            db_id, tuner_id, name, long_name = row
            chan = Channel(tuner_id, name, long_name, self)
            chan.db_id = db_id
            self._channels_by_name[name] = chan
            self._channels_by_db_id[db_id] = chan
            for t in tuner_id:
                if self._channels_by_tuner_id.has_key(t):
                    log.warning('loading channel %s with tuner_id %s '+\
                                'allready claimed by channel %s',
                                chan.name, t,
                                self._channels_by_tuner_id[t].name)
                else:
                    self._channels_by_tuner_id[t] = chan
            self._channels_list.append(chan)

        # get attributes from server and store local
        self._max_program_length = max_program_length
        self._num_programs = num_programs

        if self.status == CONNECTING:
            self.status = CONNECTED
            self.signals["connected"].emit()
        self.signals["updated"].emit()


    @kaa.notifier.yield_execution()
    def search(self, channel=None, time=None, **kwargs):
        """
        Search the db. This will call the search function on server side using
        kaa.ipc. This function will always return an InProgress object, even when
        the client is disconnected.
        """
        if self.status == DISCONNECTED:
            # make sure we always return InProgress
            yield kaa.notifier.YieldContinue
            yield []

        while self.status == CONNECTING:
            yield kaa.notifier.YieldContinue

        if channel is not None:
            if isinstance(channel, Channel):
                kwargs["channel"] = channel.db_id
            if isinstance(channel, (tuple, list)):
                kwargs["channel"] = [ c.db_id for c in channel ]

        if time is not None:
            if isinstance(time, (int, float, long)):
                # Find all programs currently playing at the given time.  We
                # add 1 second as a heuristic to prevent duplicates if the
                # given time occurs on a boundary between 2 programs.
                start, stop = time + 1, time + 1
            else:
                start, stop = time

            max = self._max_program_length
            kwargs["start"] = kaa.db.QExpr("range", (int(start) - max, int(stop)))
            kwargs["stop"]  = kaa.db.QExpr(">=", int(start))

        query_data = self.server.rpc('guide.query', type='program', **kwargs)
        # wait for the rpc to finish
        yield query_data
        # get data
        query_data = query_data()

        # Convert raw search result data
        if kwargs.get('attrs'):
            attrs = kwargs.get('attrs')
            def combine_attrs(row):
                return [ row.get(a) for a in attrs ]
            yield [ combine_attrs(row) for row in query_data ]
        
        # Convert raw search result data from the server into python objects.
        results = []
        channel = None
        for row in query_data:
            if not channel or row['parent_id'] != channel.db_id:
                if row['parent_id'] not in self._channels_by_db_id:
                    continue
                channel = self._channels_by_db_id[row['parent_id']]
            results.append(Program(channel, row))
        yield results


    def new_channel(self, tuner_id=None, name=None, long_name=None):
        """
        Returns a channel object that is not associated with the EPG.
        This is useful for clients that have channels that do not appear
        in the EPG but wish to handle them anyway.
        """

        # require at least one field
        if not tuner_id and not name and not long_name:
            log.error('need at least one field to create a channel')
            return None

        if not name:
            # then there must be one of the others
            if tuner_id:
                name = tuner_id[0]
            else:
                name = long_name

        if not long_name:
            # then there must be one of the others
            if name:
                long_name = name
            elif tuner_id:
                long_name = tuner_id[0]

        return Channel(tuner_id, name, long_name, epg=None)


    @yield_execution_while_connecting()
    def get_channel(self, name):
        """
        Get channel by name.
        """
        if name not in self._channels_by_name:
            return None
        return self._channels_by_name[name]


    @yield_execution_while_connecting()
    def get_channel_by_db_id(self, db_id):
        """
        Get channel by database id.
        """
        if db_id not in self._channels_by_db_id:
            return None
        return self._channels_by_db_id[db_id]


    @yield_execution_while_connecting()
    def get_channel_by_tuner_id(self, tuner_id):
        """
        Get channel by tuner id.
        """
        if tuner_id not in self._channels_by_tuner_id:
            return None
        return self._channels_by_tuner_id[tuner_id]


    @yield_execution_while_connecting()
    def get_channels(self, sort=False):
        """
        Get all channels
        """
        if sort:
            channels = self._channels_list[:]
            channels.sort(lambda a, b: cmp(a.name, b.name))
            channels.sort(lambda a, b: cmp_channel(a, b))
            return channels
        return self._channels_list


    def update(self, *args, **kwargs):
        """
        Update the database. This will call the update function in the server
        and the server needs to be configured for that.
        """
        if self.status == DISCONNECTED:
            return False
        return self.server.rpc('guide.update', *args, **kwargs)
