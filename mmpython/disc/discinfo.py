# -----------------------------------------------------------------------
# discinfo.py - basic class for any discs containing collections of
# media.
# -----------------------------------------------------------------------
# $Id$
#
# $Log$
# Revision 1.3  2003/06/10 22:11:36  dischi
# some fixes
#
# Revision 1.2  2003/06/10 11:50:52  dischi
# Moved all ioctl calls for discs to discinfo.cdrom_disc_status. This function
# uses try catch around ioctl so it will return 0 (== no disc) for systems
# without ioctl (e.g. Windows)
#
# Revision 1.1  2003/06/10 10:56:54  the_krow
# - Build try-except blocks around disc imports to make it run on platforms
#   not compiling / running the C extensions.
# - moved DiscInfo class to disc module
# - changed video.VcdInfo to be derived from CollectionInfo instead of
#   DiskInfo so it can be used without the cdrom extensions which are
#   hopefully not needed for bin-files.
#
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
import os
import re

try:
    from fcntl import ioctl
    import DiscID
except:
    print 'WARNING: failed to import ioctl, discinfo won\' work'


def cdrom_disc_status(device):
    """
    check the current disc in device
    return: no disc (0), audio cd (1), data cd (2)
    """
    CDROM_DRIVE_STATUS=0x5326
    CDSL_CURRENT=( (int ) ( ~ 0 >> 1 ) )
    CDROM_DISC_STATUS=0x5327
    CDS_AUDIO=100
    CDS_MIXED=105
    
    try:
        fd = os.open(device, os.O_RDONLY | os.O_NONBLOCK)
        s = ioctl(fd, CDROM_DRIVE_STATUS, CDSL_CURRENT)
    except:
        # maybe we need to close the fd if ioctl fails, maybe
        # open fails and there is no fd, maye we aren't running
        # linux and don't have ioctl
        try:
            os.close(fd)
        except:
            pass
        return 0

    s = ioctl(fd, CDROM_DISC_STATUS)
    os.close(fd)
    if s == CDS_AUDIO or s == CDS_MIXED:
        return 1
    return 2
    

def cdrom_disc_id(device):
    """
    return the disc id of the device or None if no disc is there
    """
    disc_type = cdrom_disc_status(device)
    if disc_type == 0:
        return None
        
    elif disc_type == 1:
        disc_id = DiscID.disc_id(DiscID.open(device))
        return '%08lx_%d' % (disc_id[0], disc_id[1])

    else:
        f = open(device,'rb')

        f.seek(0x0000832d)
        id = f.read(16)
        f.seek(32808, 0)
        label = f.read(32)
        f.close()
            
        m = re.match("^(.*[^ ]) *$", label)
        if m:
            return '%s%s' % (id, m.group(1))
        return id


class DiscInfo(mediainfo.CollectionInfo):
    def isDisc(self, device):
        type = cdrom_disc_status(device)
        if type != 2:
            return type
        
        self.id = cdrom_disc_id(device)
        if len(self.id) == 16:
            self.label = ''
        else:
            self.label = self.id[16:]

        self.keys.append('label')
        return 2
