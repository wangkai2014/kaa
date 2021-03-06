import sys
import logging

import kaa
import kaa.display
import kaa.popcorn

logging.getLogger('popcorn').setLevel(logging.INFO)

def print_msg(msg):
    print '>', msg

def next(id):
    print 'play with', id
    player.open(sys.argv[1], player=id)
    player.play()
    
window = kaa.display.X11Window(size = (800,600), title = "kaa.popcorn")

player = kaa.popcorn.Player(window)
player.signals["start"].connect_once(window.show)
player.signals["start"].connect(print_msg, 'playback started')
player.signals["end"].connect(print_msg, 'playback end')
player.signals["failed"].connect(print_msg, 'playback failed')

kaa.OneShotTimer(next, 'xine').start(0)
kaa.OneShotTimer(next, 'gstreamer').start(5)
kaa.OneShotTimer(next, 'mplayer').start(10)
kaa.OneShotTimer(next, 'xine').start(15)
kaa.OneShotTimer(next, 'xine').start(20)
kaa.OneShotTimer(next, 'gstreamer').start(25)
kaa.OneShotTimer(next, 'gstreamer').start(30)
kaa.OneShotTimer(next, 'mplayer').start(35)
kaa.OneShotTimer(next, 'mplayer').start(40)

kaa.main.run()
