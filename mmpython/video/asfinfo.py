#if 0
# $Id$
# $Log$
# Revision 1.11  2003/06/12 00:36:30  the_krow
# ASF Audio parsing
#
# Revision 1.10  2003/06/12 00:27:25  the_krow
# More asf parsing: Width, Height, Video Codec
#
# Revision 1.9  2003/06/11 20:51:00  the_krow
# Title, Artist and some other data sucessfully parsed from wmv, asf, wma
#
# Revision 1.8  2003/06/11 19:07:57  the_krow
# asf,wmv,wma now get the guids right...
#
# Revision 1.7  2003/06/11 16:11:08  the_krow
# asf parsing... asf is really an ugly format.
#
# Revision 1.6  2003/06/08 19:53:21  dischi
# also give the filename to init for additional data tests
#
# Revision 1.5  2003/06/08 15:40:26  dischi
# catch exception, raised for small text files
#
# Revision 1.4  2003/06/08 13:44:58  dischi
# Changed all imports to use the complete mmpython path for mediainfo
#
# Revision 1.3  2003/06/08 13:11:38  dischi
# removed print at the end and moved it into register
#
# Revision 1.2  2003/05/13 12:31:43  the_krow
# + Copyright Notice
#
#
# MMPython - Media Metadata for Python
# Copyright (C) 2003 Thomas Schueppel
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
# -----------------------------------------------------------------------
#endif

import re
import struct
import string
import fourcc

from mmpython import mediainfo

def _guid(input):
    # Remove any '-'
    s = string.join(string.split(input,'-'), '')
    r = ''
    if len(s) != 32:
        return ''
    x = ''
    for i in range(0,16):
        r+=chr(int(s[2*i:2*i+2],16))
    guid = struct.unpack('<IHHBB6s',r)
    return guid

GUIDS = {        
'ASF_Header_Object' : _guid('75B22630-668E-11CF-A6D9-00AA0062CE6C'),
#'ASF_Header_Object2' : _guid('3026B275-8E66-CF11-A6D9-00AA0062CE6C'),
'ASF_Data_Object' : _guid('75B22636-668E-11CF-A6D9-00AA0062CE6C'),
'ASF_Simple_Index_Object' : _guid('33000890-E5B1-11CF-89F4-00A0C90349CB'),
'ASF_Index_Object' : _guid('D6E229D3-35DA-11D1-9034-00A0C90349BE'),
'ASF_Media_Object_Index_Object' : _guid('FEB103F8-12AD-4C64-840F-2A1D2F7AD48C'),
'ASF_Timecode_Index_Object' : _guid('3CB73FD0-0C4A-4803-953D-EDF7B6228F0C'),

'ASF_File_Properties_Object' : _guid('8CABDCA1-A947-11CF-8EE4-00C00C205365'),
'ASF_Stream_Properties_Object' : _guid('B7DC0791-A9B7-11CF-8EE6-00C00C205365'),
'ASF_Header_Extension_Object' : _guid('5FBF03B5-A92E-11CF-8EE3-00C00C205365'),
'ASF_Codec_List_Object' : _guid('86D15240-311D-11D0-A3A4-00A0C90348F6'),
'ASF_Script_Command_Object' : _guid('1EFB1A30-0B62-11D0-A39B-00A0C90348F6'),
'ASF_Marker_Object' : _guid('F487CD01-A951-11CF-8EE6-00C00C205365'),
'ASF_Bitrate_Mutual_Exclusion_Object' : _guid('D6E229DC-35DA-11D1-9034-00A0C90349BE'),
'ASF_Error_Correction_Object' : _guid('75B22635-668E-11CF-A6D9-00AA0062CE6C'),
'ASF_Content_Description_Object' : _guid('75B22633-668E-11CF-A6D9-00AA0062CE6C'),
'ASF_Extended_Content_Description_Object' : _guid('D2D0A440-E307-11D2-97F0-00A0C95EA850'),
'ASF_Content_Branding_Object' : _guid('2211B3FA-BD23-11D2-B4B7-00A0C955FC6E'),
'ASF_Stream_Bitrate_Properties_Object' : _guid('7BF875CE-468D-11D1-8D82-006097C9A2B2'),
'ASF_Content_Encryption_Object' : _guid('2211B3FB-BD23-11D2-B4B7-00A0C955FC6E'),
'ASF_Extended_Content_Encryption_Object' : _guid('298AE614-2622-4C17-B935-DAE07EE9289C'),
'ASF_Alt_Extended_Content_Encryption_Obj' : _guid('FF889EF1-ADEE-40DA-9E71-98704BB928CE'),
'ASF_Digital_Signature_Object' : _guid('2211B3FC-BD23-11D2-B4B7-00A0C955FC6E'),
'ASF_Padding_Object' : _guid('1806D474-CADF-4509-A4BA-9AABCB96AAE8'),

'ASF_Extended_Stream_Properties_Object' : _guid('14E6A5CB-C672-4332-8399-A96952065B5A'),
'ASF_Advanced_Mutual_Exclusion_Object' : _guid('A08649CF-4775-4670-8A16-6E35357566CD'),
'ASF_Group_Mutual_Exclusion_Object' : _guid('D1465A40-5A79-4338-B71B-E36B8FD6C249'),
'ASF_Stream_Prioritization_Object' : _guid('D4FED15B-88D3-454F-81F0-ED5C45999E24'),
'ASF_Bandwidth_Sharing_Object' : _guid('A69609E6-517B-11D2-B6AF-00C04FD908E9'),
'ASF_Language_List_Object' : _guid('7C4346A9-EFE0-4BFC-B229-393EDE415C85'),
'ASF_Metadata_Object' : _guid('C5F8CBEA-5BAF-4877-8467-AA8C44FA4CCA'),
'ASF_Metadata_Library_Object' : _guid('44231C94-9498-49D1-A141-1D134E457054'),
'ASF_Index_Parameters_Object' : _guid('D6E229DF-35DA-11D1-9034-00A0C90349BE'),
'ASF_Media_Object_Index_Parameters_Obj' : _guid('6B203BAD-3F11-4E84-ACA8-D7613DE2CFA7'),
'ASF_Timecode_Index_Parameters_Object' : _guid('F55E496D-9797-4B5D-8C8B-604DFE9BFB24'),

'ASF_Audio_Media' : _guid('F8699E40-5B4D-11CF-A8FD-00805F5C442B'),
'ASF_Video_Media' : _guid('BC19EFC0-5B4D-11CF-A8FD-00805F5C442B'),
'ASF_Command_Media' : _guid('59DACFC0-59E6-11D0-A3AC-00A0C90348F6'),
'ASF_JFIF_Media' : _guid('B61BE100-5B4E-11CF-A8FD-00805F5C442B'),
'ASF_Degradable_JPEG_Media' : _guid('35907DE0-E415-11CF-A917-00805F5C442B'),
'ASF_File_Transfer_Media' : _guid('91BD222C-F21C-497A-8B6D-5AA86BFC0185'),
'ASF_Binary_Media' : _guid('3AFB65E2-47EF-40F2-AC2C-70A90D71D343'),

'ASF_Web_Stream_Media_Subtype' : _guid('776257D4-C627-41CB-8F81-7AC7FF1C40CC'),
'ASF_Web_Stream_Format' : _guid('DA1E6B13-8359-4050-B398-388E965BF00C'),

'ASF_No_Error_Correction' : _guid('20FB5700-5B55-11CF-A8FD-00805F5C442B'),
'ASF_Audio_Spread' : _guid('BFC3CD50-618F-11CF-8BB2-00AA00B4E220'),
}

_print = mediainfo._debug

class AsfInfo(mediainfo.AVInfo):
    def __init__(self,file,filename):
        mediainfo.AVInfo.__init__(self)
        self.context = 'video'
        self.valid = 0
        self.mime = 'video/asf'
        self.type = 'asf video'
        h = file.read(30)
        if len(h) < 30:
            return
        self.valid = 1
        (guidstr,objsize,objnum,reserved1,reserved2) = struct.unpack('<16sQIBB',h)                
        guid = struct.unpack('>IHHBB6s', guidstr)
        if (guid != GUIDS['ASF_Header_Object']):
            self.valid = 0
            return
        if reserved1 != 0x01 or reserved2 != 0x02:
            self.valid = 0
        print "asf header size: %d / %d objects" % (objsize,objnum)
        header = file.read(objsize-30)
        for i in range(0,objnum):
            h = self._getnextheader(header)
            header = header[h[1]:]
            
    def _printguid(self,guid):
        r = "%.8X-%.4X-%.4X-%.2X%.2X-%s" % guid
        return r 
        
    def _getnextheader(self,s):
        r = struct.unpack('<16sQ',s[:24])
        (guidstr,objsize) = r
        guid = struct.unpack('>IHHBB6s', guidstr)
        if guid == GUIDS['ASF_File_Properties_Object']:
            print "File Properties Object"
            val = struct.unpack('<16s6Q4I',s[24:24+80])
            (fileid, size, date, packetcount, duration, \
             senddur, preroll, flags, minpack, maxpack, maxbr) = \
             val
            pass
        elif guid == GUIDS['ASF_Stream_Properties_Object']:
            print "Stream Properties Object [%d]" % objsize
            streamtype = struct.unpack('>IHHBB6s', s[24:40])
            errortype = struct.unpack('>IHHBB6s', s[40:56])
            offset, typelen, errorlen, flags = struct.unpack('>QIIH4x', s[56:78])
            if streamtype == GUIDS['ASF_Video_Media']:
                print "Is Video"
                vi = mediainfo.VideoInfo()
                #vi.width, vi.height, formatsize = struct.unpack('<IIxH', s[78:89])
                vi.width, vi.height, depth, codec, = struct.unpack('<4xII2xH4s', s[89:89+20])
                vi.codec = fourcc.RIFFCODEC[codec]
                self.video.append(vi)  
            elif streamtype == GUIDS['ASF_Audio_Media']:
                print "Is Audio"
                ai = mediainfo.AudioInfo()
                twocc, ai.channels, ai.samplerate, bitrate, block, ai.samplebits, = struct.unpack('<HHIIHH', s[78:78+16])
                ai.bitrate = 8*bitrate  # XXX Is this right?
                ai.codec = fourcc.RIFFWAVE[twocc]
                self.video.append(ai)  
            pass
        elif guid == GUIDS['ASF_Header_Extension_Object']:
            print "ASF_Header_Extension_Object %d" % objsize
            size = struct.unpack('<I',s[42:46])[0]
            data = s[46:46+size]
            while len(data):
                print "Sub:"
                h = self._getnextheader(data)
                data = data[h[1]:]
            
        elif guid == GUIDS['ASF_Codec_List_Object']:
            print "List Object"
            pass
        elif guid == GUIDS['ASF_Error_Correction_Object']:
            print "Error Correction"
            pass
        elif guid == GUIDS['ASF_Content_Description_Object']:
            print "Content Description Object"
            val = struct.unpack('<5H', s[24:24+10])
            pos = 34
            strings = []
            for i in val:
                strings.append(s[pos:pos+i])
                pos+=i
            #(title, artist, copyright, caption, rating) = tuple(strings)
            (self.title, self.artist, self.copyright, self.caption, rating) = tuple(strings)
        else:
            print "unknown: %s %d" % (self._printguid(guid), objsize)
        return r
        
factory = mediainfo.get_singleton()  
factory.register( 'video/asf', ('asf','wmv','wma'), mediainfo.TYPE_AV, AsfInfo )
