#if 0 /*
# -----------------------------------------------------------------------
# dvdinfo.py - parse dvd title structure
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


import ifoparser
from mmpython import mediainfo
import mmpython
from discinfo import DiscInfo

class DVDAudio(mediainfo.AudioInfo):
    def __init__(self, title, number):
        mediainfo.AudioInfo.__init__(self)
        self.number = number
        self.title  = title
        self.id, self.language, self.codec, self.channels, self.samplerate = \
                 ifoparser.audio(title, number)


class DVDTitle(mediainfo.AVInfo):
    def __init__(self, number):
        mediainfo.AVInfo.__init__(self)
        self.number = number
        self.chapters, self.angles, self.length, audio_num, \
                       subtitles_num = ifoparser.title(number)

        self.mime = 'video/mpeg'
        for a in range(1, audio_num+1):
            self.audio.append(DVDAudio(number, a))
            
        for s in range(1, subtitles_num+1):
            self.subtitles.append(ifoparser.subtitle(number, s)[0])
            
class DVDInfo(DiscInfo):
    def __init__(self,device):
        DiscInfo.__init__(self)
        self.context = 'video'
        self.offset = 0
        self.valid = self.isDisc(device)
        self.mime = 'video/dvd'
        self.type = 'DVD'
        self.subtype = 'video'

    def isDisc(self, device):
        if DiscInfo.isDisc(self, device) != 2:
            return 0

        # brute force reading of the device to find out if it is a DVD
        f = open(device,'rb')
        f.seek(32808, 0)
        buffer = f.read(50000)

        if buffer.find('UDF') == -1:
            f.close()
            return 0

        # seems to be a DVD, read a little bit more
        buffer += f.read(550000)
        f.close()

        if buffer.find('VIDEO_TS') == -1 and buffer.find('VIDEO_TS.IFO') == -1 and \
               buffer.find('OSTA UDF Compliant') == -1:
            return 0

        # OK, try libdvdread
        title_num = ifoparser.open(device)

        if not title_num:
            return 0

        for title in range(1, title_num+1):
            ti = DVDTitle(title)
            ti.trackno = title
            ti.trackof = title_num
            self.appendtrack(ti)

        ifoparser.close()
        return 1



mmpython.registertype( 'video/dvd', mediainfo.EXTENSION_DEVICE, mediainfo.TYPE_AV, DVDInfo )
