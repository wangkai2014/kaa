# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# ptypes.py - Types and constants used by kaa.popcorn
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

CAP_NONE  = 0
CAP_OSD   = 3
CAP_DVD = 4
CAP_DVD_MENUS = 5
CAP_DYNAMIC_FILTERS = 6
CAP_VARIABLE_SPEED = 7
CAP_VISUALIZATION = 8
CAP_DEINTERLACE = 9
CAP_CANVAS = 10

STATE_NOT_RUNNING = 'STATE_NOT_RUNNING'
STATE_IDLE = 'STATE_IDLE'
STATE_OPENING = 'STATE_OPENING'
STATE_OPEN = 'STATE_OPEN'
STATE_PLAYING = 'STATE_PLAYING'
STATE_PAUSED = 'STATE_PAUSED'
STATE_STOPPING = 'STATE_STOPPING'
STATE_SHUTDOWN = 'STATE_SHUTDOWN'

SEEK_RELATIVE = 'SEEK_RELATIVE'
SEEK_ABSOLUTE = 'SEEK_ABSOLUTE'
SEEK_PERCENTAGE = 'SEEK_PERCENTAGE'

class PlayerError(Exception):
    pass

class PlayerCapError(PlayerError):
    pass
