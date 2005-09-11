# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# output.py - Output plugins
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# kaa-record - A recording module
# Copyright (C) 2005 S�nke Schwardt, Dirk Meyer
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
# Please see the file doc/CREDITS for a complete list of authors.
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

# kaa.record imports
import _filter

# get logging object
log = logging.getLogger('record')

class Chain(list):

    def __init__(self):
        list.__init__(self)
        self.vpid = 0
        self.apid = 0

    def set_pids(self, vpid, apid):
        self.vpid = vpid
        self.apid = apid

    def _create(self):
        log.debug('create filter chain')
        chain = _filter.Chain()
        chain.add_pid(self.vpid)
        chain.add_pid(self.apid)
        for filter in self:
            if isinstance(filter, Remux):
                filter.vpid = self.vpid
                filter.apid = self.apid
            chain.append(filter)
        return chain.get_chain()
    
    
class Remux(object):
    def __init__(self):
        log.info('add filter Remux')
        self.vpid = 0
        self.apid = 0

    def _create(self):
        return _filter.Remux(self.vpid, self.apid)
        
    
class Filewriter(object):
    def __init__(self, filename, chunksize=0):
        log.info('add filter Filewriter::%s' % filename)
        self.filename = filename
        self.chunksize = chunksize

    def _create(self):
        return _filter.Filewriter(self.filename, self.chunksize)
        

class UDPSend(object):
    def __init__(self, addr):
        log.info('add filter UDPSend::%s' % addr)
        self.addr = addr

    def _create(self):
        return _filter.UDPSend(self.addr)
        
