#!/usr/bin/python

import mediainfo
import audio.ogginfo
import audio.pcminfo
import audio.mp3info
import video.riffinfo
#import video.mpeginfo
import video.asfinfo
import video.movinfo
import video.dvdinfo
import image.jpginfo
import image.pnginfo
import image.tiffinfo
import video.dvdinfo

import sys

m = mediainfo.get_singleton()
medium = m.create_from_filename(sys.argv[1])
#medium.expand_keywords()
if medium:
    print "medium is: %s" % medium.type
    for k in medium.keys:
        val = medium.__dict__[k]
        if val: print "  %s: %s" % (k,val)
else:
    print "No Match found"

