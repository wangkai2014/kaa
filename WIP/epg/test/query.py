import time
import kaa.epg

def local():
    kaa.epg.load('test.db')
    print kaa.epg.get_channels()
    t1 = time.time()
    # UTC/GMT conversion because kaa.epg uses UTC
    print int(time.mktime(time.gmtime()))
    print int(time.time() + time.timezone)
    result = kaa.epg.search(time=time.mktime(time.gmtime()))
    t2 = time.time()
    for r in result:
        print r.title, r.channel
    print t2 - t1

@kaa.coroutine()
def rpc():
    kaa.epg.connect()
    yield kaa.epg.guide.signals.subset('connected').any()
    print kaa.epg.get_channels()
    t1 = time.time()
    result = yield kaa.epg.search(time=time.mktime(time.gmtime()))
    t2 = time.time()
    print result
    print t2 - t1

if 0:
    rpc()
    kaa.main.run()
if 1:
    local()

