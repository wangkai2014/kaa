# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# xmlinfo.py - detect xml and fxd files
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# kaa-Metadata - Media Metadata for Python
# Copyright (C) 2003-2005 Thomas Schueppel, Dirk Meyer
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

# python imports
import os
import logging
import xml

# kaa imports
from kaa.metadata import factory
from kaa.metadata import mediainfo

# get logging object
log = logging.getLogger('metadata')

XML_TAG_INFO = {
    'image':  'Bins Image Description',
    'freevo': 'Freevo XML Definition'
    }

class XMLInfo(mediainfo.MediaInfo):

    def __init__(self,file):
        if not os.path.splitext(file.name)[1].lower() in ('.xml', '.fxd'):
            raise mediainfo.KaaMetadataParseError()

        mediainfo.MediaInfo.__init__(self)

        self.mime  = 'text/xml'
        self.type  = ''

        xml.SAXParseFile(self, file.name, 10)


    def startElement(self, tag, attrs):
        """
        Callback for <tag>
        """
        if self.type:
            return

        if tag in XML_TAG_INFO:
            self.type = XML_TAG_INFO[tag]
        else:
            self.type = 'XML file'


factory.register( 'text/xml', ('xml', 'fxd'), mediainfo.TYPE_MISC, XMLInfo )
