#if 0
# $Id$
# $Log$
# Revision 1.21  2004/06/21 20:37:34  dischi
# basic support for mpeg-ts
#
# Revision 1.20  2004/03/13 23:41:59  dischi
# add AudioInfo to mpeg for all streams
#
# Revision 1.19  2004/02/11 20:11:54  dischi
# Updated length calculation for mpeg files. This may not work for all files.
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
import os
import struct
import string
import fourcc

from mmpython import mediainfo
import mmpython
import stat

##------------------------------------------------------------------------
## START_CODE
##
## Start Codes, with 'slice' occupying 0x01..0xAF
##------------------------------------------------------------------------
START_CODE = {
    0x00 : 'picture_start_code',
    0xB0 : 'reserved',
    0xB1 : 'reserved',
    0xB2 : 'user_data_start_code',
    0xB3 : 'sequence_header_code',
    0xB4 : 'sequence_error_code',
    0xB5 : 'extension_start_code',
    0xB6 : 'reserved',
    0xB7 : 'sequence end',
    0xB8 : 'group of pictures',
}
for i in range(0x01,0xAF): 
    START_CODE[i] = 'slice_start_code'

##------------------------------------------------------------------------
## START CODES
##------------------------------------------------------------------------
PICTURE   = 0x00
USERDATA  = 0xB2
SEQ_HEAD  = 0xB3
SEQ_ERR   = 0xB4
EXT_START = 0xB5
SEQ_END   = 0xB7
GOP       = 0xB8

SEQ_START_CODE = 0xB3
PACK_PKT       = 0xBA
SYS_PKT        = 0xBB
PADDING_PKT    = 0xBE
AUDIO_PKT      = 0xC0
VIDEO_PKT      = 0xE0

##------------------------------------------------------------------------
## FRAME_RATE
##
## A lookup table of all the standard frame rates.  Some rates adhere to
## a particular profile that ensures compatibility with VLSI capabilities
## of the early to mid 1990s.
##
## CPB
##   Constrained Parameters Bitstreams, an MPEG-1 set of sampling and 
##   bitstream parameters designed to normalize decoder computational 
##   complexity, buffer size, and memory bandwidth while still addressing 
##   the widest possible range of applications.
##
## Main Level
##   MPEG-2 Video Main Profile and Main Level is analogous to MPEG-1's 
##   CPB, with sampling limits at CCIR 601 parameters (720x480x30 Hz or 
##   720x576x24 Hz). 
##
##------------------------------------------------------------------------ 
FRAME_RATE = [ 
      0, 
      round(24000.0/1001*100)/100, ## 3-2 pulldown NTSC (CPB/Main Level)
      24,           ## Film (CPB/Main Level)
      25,           ## PAL/SECAM or 625/60 video
      round(30000.0/1001*100)/100, ## NTSC (CPB/Main Level)
      30,           ## drop-frame NTSC or component 525/60  (CPB/Main Level)
      50,           ## double-rate PAL
      round(60000.0/1001*100)/100, ## double-rate NTSC
      60,           ## double-rate, drop-frame NTSC/component 525/60 video
      ]

##------------------------------------------------------------------------
## ASPECT_RATIO -- INCOMPLETE?
##
## This lookup table maps the header aspect ratio index to a common name.
## These are just the defined ratios for CPB I believe.  As I understand 
## it, a stream that doesn't adhere to one of these aspect ratios is
## technically considered non-compliant.
##------------------------------------------------------------------------ 
ASPECT_RATIO = [ 'Forbidden',
		      '1/1 (VGA)',
		      '4/3 (TV)',
		      '16/9 (Large TV)',
		      '2.21/1 (Cinema)',
	       ]
 

class MpegInfo(mediainfo.AVInfo):
    def __init__(self,file):
        mediainfo.AVInfo.__init__(self)
        self.context = 'video'
        self.offset = 0

        # try to find some basic info
        self.valid = self.isTS(file) 
        if not self.valid:
            self.valid = self.isSystem(file) 
        if not self.valid:
            self.valid = self.isVideo(file) 

        if self.valid:       
            self.mime = 'video/mpeg'
            if not self.video:
                self.video.append(mediainfo.VideoInfo())

            for vi in self.video:
                vi.width, vi.height = self.dxy(file)
                vi.fps, vi.aspect = self.framerate_aspect(file)
                vi.bitrate = self.bitrate(file)
                if self.length:
                    vi.length = self.length
                else:
                    # wild (bad) guess
                    vi.length = self.mpgsize(file) * 8 / (vi.bitrate)

            if not self.type:
                if self.video[0].width == 480:
                    self.type = 'MPEG2 video' # SVCD spec
                elif self.video[0].width == 352:
                    self.type = 'MPEG1 video' # VCD spec
                else:
                    self.type = 'MPEG video'

                
    def dxy(self,file):  
        file.seek(self.offset+4,0)
        v = file.read(4)
        x = struct.unpack('>H',v[:2])[0] >> 4
        y = struct.unpack('>H',v[1:3])[0] & 0x0FFF
        return (x,y)
        
    def framerate_aspect(self,file):
        file.seek(self.offset+7,0)
        v = struct.unpack( '>B', file.read(1) )[0] 
        try:
            fps = FRAME_RATE[v&0xf]
        except IndexError:
            fps = None
        try:
            aspect = ASPECT_RATIO[v>>4]
        except IndexError:
            if mediainfo.DEBUG:
                print 'Index error: %s' % (v>>4)
            aspect = None
        return (fps, aspect)
        
    ##------------------------------------------------------------------------
    ## bitrate()
    ##
    ## From the MPEG-2.2 spec:
    ##
    ##   bit_rate -- This is a 30-bit integer.  The lower 18 bits of the 
    ##   integer are in bit_rate_value and the upper 12 bits are in 
    ##   bit_rate_extension.  The 30-bit integer specifies the bitrate of the 
    ##   bitstream measured in units of 400 bits/second, rounded upwards. 
    ##   The value zero is forbidden.
    ##
    ## So ignoring all the variable bitrate stuff for now, this 30 bit integer
    ## multiplied times 400 bits/sec should give the rate in bits/sec.
    ##  
    ## TODO: Variable bitrates?  I need one that implements this.
    ## 
    ## Continued from the MPEG-2.2 spec:
    ##
    ##   If the bitstream is a constant bitrate stream, the bitrate specified 
    ##   is the actual rate of operation of the VBV specified in annex C.  If 
    ##   the bitstream is a variable bitrate stream, the STD specifications in 
    ##   ISO/IEC 13818-1 supersede the VBV, and the bitrate specified here is 
    ##   used to dimension the transport stream STD (2.4.2 in ITU-T Rec. xxx | 
    ##   ISO/IEC 13818-1), or the program stream STD (2.4.5 in ITU-T Rec. xxx | 
    ##   ISO/IEC 13818-1).
    ## 
    ##   If the bitstream is not a constant rate bitstream the vbv_delay 
    ##   field shall have the value FFFF in hexadecimal.
    ##
    ##   Given the value encoded in the bitrate field, the bitstream shall be 
    ##   generated so that the video encoding and the worst case multiplex 
    ##   jitter do not cause STD buffer overflow or underflow.
    ##
    ##
    ##------------------------------------------------------------------------ 


    ## Some parts in the code are based on mpgtx (mpgtx.sf.net)
    
    def bitrate(self,file):
        file.seek(self.offset+8,0)
        t,b = struct.unpack( '>HB', file.read(3) )
        vrate = t << 2 | b >> 6
        return vrate * 400
        
    def mpgsize(self,file):
        file.seek(0,2)
        return file.tell()


    def ParseSystemPacket(self, buffer):
        size = (ord(buffer[4]) * 256 + ord(buffer[5])) - 6
        if size % 3:
            return 0
        if mediainfo.DEBUG:
            print '%s Streams in MPEG' % (size / 3)
        num_v = 0
        num_a = 0
        for i in range(size/3):
            code = ord(buffer[12+i*3])
            if (code&0xF0)==0xC0:
                num_a += 1
            elif (code&0xF0)==0xE0 or (code & 0xF0)==0xD0:
                num_v += 1
        if num_v:
            self.has_video = 1
        if num_a:
            self.has_audio = 1
            for i in range(num_a):
                ai = mediainfo.AudioInfo()
                ai.id = i
                # FIXME: more infos please
                self.audio.append(ai)
        return 1


    def ReadTSMpeg2(self, buffer):
	highbit = (ord(buffer[0])&0x20)>>5

	low4Bytes= ((ord(buffer[0]) & 0x18) >> 3) << 30
	low4Bytes |= (ord(buffer[0]) & 0x03) << 28
	low4Bytes |= ord(buffer[1]) << 20
	low4Bytes |= (ord(buffer[2]) & 0xF8) << 12
	low4Bytes |= (ord(buffer[2]) & 0x03) << 13
	low4Bytes |= ord(buffer[3]) << 5
	low4Bytes |= (ord(buffer[4])) >> 3

	sys_clock_ref=(ord(buffer[4]) & 0x3) << 7
	sys_clock_ref|=(ord(buffer[5]) >> 1)

 	return (long(highbit * (1<<16) * (1<<16)) + low4Bytes) / 90000


    def ReadTSMpeg1(self, buffer):
	highbit = (ord(buffer[0]) >> 3) & 0x01

	low4Bytes = ((ord(buffer[0]) >> 1) & 0x03) << 30
	low4Bytes |= ord(buffer[1]) << 22;
	low4Bytes |= (ord(buffer[2]) >> 1) << 15;
	low4Bytes |= ord(buffer[3]) << 7;
	low4Bytes |= ord(buffer[4]) >> 1;

	return (long(highbit) * (1<<16) * (1<<16) + low4Bytes) / 90000;


    def isSystem(self, file):
        file.seek(0,0)
        buffer = file.read(10000)
        offset = 0
        while buffer[offset] == '\0':
            offset += 1
        offset -= 2

        if buffer[offset:offset+4] == '\x00\x00\x01%s' % chr(PACK_PKT):
            offset += 4

            if ord(buffer[4]) & 0xF0 == 0x20:
                self.type = 'MPEG1 video'
                PACKlength = 12
                self.ReadTS = self.ReadTSMpeg1
            elif (ord(buffer[4]) & 0xC0) == 0x40:
                self.type = 'MPEG2 video'
                PACKlength = 14 + (ord(buffer[13]) & 0x07)
                self.ReadTS = self.ReadTSMpeg2
            else:
                return 0

            if not self.ParseSystemPacket(buffer[PACKlength:]):
                return 0

            type = ord(buffer[0])
            if ord(buffer[15+PACKlength]) in (VIDEO_PKT, AUDIO_PKT):
                type = VIDEO_PKT
            if type != VIDEO_PKT:
                if mediainfo.DEBUG:
                    print 'unknown packet type %s, this may cause problems' % type

            if not self.isVideo(file):
                return 0

            self.ts_start = self.ReadTS(buffer[4:])
            self.filename = file.name
            self.length   = self.get_length()
            if mediainfo.DEBUG:
                print 'detected ts format'
            return 1
        return 0


    def get_length(self):
        if not hasattr(self, 'filename') or not hasattr(self, 'ts_start'):
            return -1
        file = open(self.filename)
        file.seek(os.stat(self.filename)[stat.ST_SIZE]-10000)
        buffer = file.read(10000)
        pos    = buffer.rfind('\x00\x00\x01%s' % chr(PACK_PKT))
        length = self.ReadTS(buffer[pos+4:]) - self.ts_start
        file.close()
        return length
    

    def seek(self, pos):
        if not hasattr(self, 'filename') or not hasattr(self, 'ts_start'):
            return 0
        file    = open(self.filename)
        seek_to = 0
        while 1:
            file.seek(1000000, 1)
            buffer = file.read(10000)
            if len(buffer) < 10000:
                break
            pack_pos = buffer.find('\x00\x00\x01%s' % chr(PACK_PKT))
            if pack_pos == -1:
                continue
            if self.ReadTS(buffer[pack_pos+4:]) - self.ts_start >= pos:
                break
            buffer  = buffer[pack_pos+50:]
            seek_to = file.tell()

        file.close()
        return seek_to

    
    def isVideo(self,file):
        file.seek(0,0)
        buffer = file.read(10000)
        self.offset = buffer.find( '\x00\x00\x01\xB3' )
        if self.offset >= 0:
            return 1
        return 0


    def TSinfo(self, file):
        PACKET_LENGTH = 188
        SYNC          = 0x47

        buffer = file.read(PACKET_LENGTH * 2)
        c = 0

        while c + PACKET_LENGTH < len(buffer):
            if ord(buffer[c]) == ord(buffer[c+PACKET_LENGTH]) == SYNC:
                break
            c += 1
        else:
            return 0

        buffer += file.read(1000000)
        self.type = 'MPEG-TS'
        while c + PACKET_LENGTH < len(buffer):
            start = ord(buffer[c+1]) & 0x40
            if not start:
                c += PACKET_LENGTH
                continue

            tsid = ((ord(buffer[c+1]) & 0x3F) << 8) + ord(buffer[c+2])
            adapt = (ord(buffer[c+3]) & 0x30) >> 4

            offset = 4
            if adapt & 0x02:
                # meta info present, skip it for now
                offset += ord(buffer[c+offset]) + 1

            if adapt & 0x01 and ord(buffer[c+offset]) == ord(buffer[c+offset+1]) == 0 \
                   and ord(buffer[c+offset+2]) == 1:
                align         = ord(buffer[c+offset+6]) & 4
                header_length = ord(buffer[c+offset+8])
                dts           = ord(buffer[c+offset+7]) >> 6

                # PES Payload (starting with 001)
                if ord(buffer[c+offset+3]) & 0xE0 == 0xC0:
                    id = ord(buffer[c+offset+3]) & 0x1F
                    type = 'audio'
                    for a in self.audio:
                        if a.id == tsid:
                            break
                    else:
                        self.audio.append(mediainfo.AudioInfo())
                        self.audio[-1].id = tsid
                        self.audio[-1].keys.append('id')

                elif ord(buffer[c+offset+3]) & 0xE0 == 0xE0:
                    id = ord(buffer[c+offset+3]) & 0xF
                    type = 'video'
                    for v in self.video:
                        if v.id == tsid:
                            break
                    else:
                        self.video.append(mediainfo.VideoInfo())
                        self.video[-1].id = tsid
                        self.video[-1].keys.append('id')

                    # new mpeg starting
                    if buffer[c+offset+header_length+9:c+offset+header_length+13] == \
                           '\x00\x00\x01\xB3' and not self.offset:
                        # yes, remember offset for later use
                        self.offset = c+offset+header_length+9
                else:
                    # unknown content
                    continue

            elif adapt & 0x01:
                # no PES, scan for something else here
                pass
            
            c += PACKET_LENGTH

        if self.offset:
            return 1
        return 0

            
    def isTS(self, file):
        if mediainfo.DEBUG:
            print 'trying mpeg-ts scan'
        file.seek(0,0)
        return self.TSinfo(file)

    
mmpython.registertype( 'video/mpeg', ('mpeg','mpg','mp4', 'ts'), mediainfo.TYPE_AV, MpegInfo )
