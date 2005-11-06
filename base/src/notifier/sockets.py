# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# sockets.py - Socket (fd) classes for the notifier
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# kaa-notifier - Notifier Wrapper
# Copyright (C) 2005 Dirk Meyer, et al.
#
# First Version: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
# Please see the file doc/AUTHORS for a complete list of authors.
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

__all__ = [ 'WeakCallback', 'WeakSocketDispatcher', 'Socket',
            'IO_READ', 'IO_WRITE', 'IO_EXCEPT' ]

import socket, StringIO
from callback import NotifierCallback, WeakNotifierCallback, Callback, Signal, notifier
from thread import MainThreadCallback, Thread, is_mainthread

IO_READ   = notifier.IO_READ
IO_WRITE  = notifier.IO_WRITE
IO_EXCEPT = notifier.IO_EXCEPT


class SocketDispatcher(NotifierCallback):

    def __init__(self, callback, *args, **kwargs):
        super(SocketDispatcher, self).__init__(callback, *args, **kwargs)
        self.set_ignore_caller_args()


    def register(self, fd, condition = IO_READ):
        if self.active():
            return
        if not is_mainthread():
            return MainThreadCallback(self.register, fd, condition)()
        notifier.addSocket(fd, self, condition)
        self._condition = condition
        self._id = fd


    def unregister(self):
        if not self.active():
            return
        if not is_mainthread():
            return MainThreadCallback(self.unregister)()
        notifier.removeSocket(self._id, self._condition)
        super(SocketDispatcher, self).unregister()



class WeakSocketDispatcher(WeakNotifierCallback, SocketDispatcher):
    pass


class Socket(object):
    """
    Notifier-aware socket class.
    """
    def __init__(self, addr = None, listen = False, async = None):
        self._addr = self._socket = None
        self._write_buffer = ""
        self._read_delim = None

        self.signals = {
            "closed": Signal(),
            "read": Signal()
        }

        self._rmon = SocketDispatcher(self._handle_read)
        self._wmon = SocketDispatcher(self._handle_write)

        if addr:
            if not listen:
                self.connect(addr, async = async)

    def _make_socket(self, addr):
        if ":" in addr:
            addr = addr.split(":")
            assert(len(addr) == 2)
            addr[1] = int(addr[1])
            addr = tuple(addr)

        if self._socket:
            self.close()

        assert(type(addr) in (str, tuple))

        if type(addr) == str:
            self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        else:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self._addr = addr


    def connect(self, addr, async = None):
        """
        Connects to the host specified in addr.  If addr is a string in the
        form host:port, or a tuple the form (host, port), a TCP socket is
        established.  Otherwise a Unix socket is established and addr is 
        treated as a filename.

        If async is not None, it is a callback that will be invoked when the
        connection has been established.  This callback takes one parameter,
        which is True if the connection was established successfully, or an
        Exception object otherwise.

        If async is None, this call will block until either connected or an
        exception is raised.  Although this call blocks, the notifier loop
        remains active.
        """
        assert(async == None or callable(async))
        self._make_socket(addr)


        thread = Thread(self._connect_thread)
        result_holder = []
        cb = async
        if not cb:
            cb = Callback(lambda res, x: x.append(res), result_holder)

        thread.signals["completed"].connect(cb)
        thread.signals["exception"].connect(cb)
        thread.start()

        if async != None:
            return

        while len(result_holder) == 0:
            notifier.step()

        if isinstance(result_holder[0], Exception):
            raise result_holder[0]


    def _connect_thread(self):
        if type(self._addr) == str:
            # Unix socket, just connect.
            self._socket.connect(self._addr)
        else:
            host, port = self._addr
            if not host.replace(".", "").isdigit():
                # Resolve the hostname.
                host = socket.gethostbyname(host)
            self._socket.connect((host, port))

        self._socket.setblocking(False)

        self._rmon.register(self._socket, IO_READ)
        if self._write_buffer:
            self._wmon.register(self._socket, IO_WRITE)

        return True

    def _handle_read(self):
        try:
            data = self._socket.recv(1024*1024)
        except socket.error, (errno, msg):
            if errno == 11:
                # Resource temporarily unavailable -- we are trying to read
                # data on a socket when none is available.
                return
            # If we're here, then the socket is likely disconnected.
            data = None

        if not data:
            return self.close(False)
    
        self.signals["read"].emit(data)


    def close(self, expected = True):
        self._rmon.unregister()
        self._wmon.unregister()
        self._write_buffer = ""

        self._socket.close()
        self._socket = None
        self.signals["closed"].emit(expected)


    def write(self, data):
        self._write_buffer += data
        if self._socket and not self._wmon.active():
            self._wmon.register(self._socket, IO_WRITE)

    def _handle_write(self):
        if len(self._write_buffer) == 0:
            return

        try:
            sent = self._socket.send(self._write_buffer)
            self._write_buffer = self._write_buffer[sent:]
            if not self._write_buffer:
                self._wmon.unregister()
        except socket.error, (errno, msg):
            if errno == 11:
                # Resource temporarily unavailable -- we are trying to write
                # data to a socket when none is available.
                return
            # If we're here, then the socket is likely disconnected.
            self.close(False)


    def is_connected(self):
        return self._socket != None
