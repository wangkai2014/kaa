#if 0 /*
# -----------------------------------------------------------------------
# datainfo.py - info about a normal data disc
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# Copyright (C) 2003 Thomas Schueppel, Dirk Meyer
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
# ----------------------------------------------------------------------- */
#endif


from mmpython import mediainfo
from discinfo import DiscInfo

class DataDiscInfo(DiscInfo):
    def __init__(self,device):
        DiscInfo.__init__(self)
        self.context = 'unknwon'
        self.offset = 0
        self.valid = self.isDisc(device)
        self.mime = 'unknown/unknown'
        self.type = 'data disc'

    def isDisc(self, device):
        if DiscInfo.isDisc(self, device) != 2:
            return 0

        return 1



factory = mediainfo.get_singleton()  
factory.register( 'cd/unknown', mediainfo.DEVICE, mediainfo.TYPE_NONE, DataDiscInfo )
