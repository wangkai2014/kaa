import logging
import sys

class _Wrapper(object):
    def __init__(self, name):
        self.name = name

    def __call__(self, *args, **kwargs):
        init()
        return globals()[self.name](*args, **kwargs)

dispatcher_add = _Wrapper('dispatcher_add')
dispatcher_remove = _Wrapper('dispatcher_remove')
loop = _Wrapper('loop')
step = _Wrapper('step')
timer_remove = _Wrapper('timer_remove')
timer_add = _Wrapper('timer_add')
socket_remove = _Wrapper('socket_remove')
socket_add = _Wrapper('socket_add')


# socket wrapper

nf_conditions = []
def _socket_add(id, method, condition = 0):
    return nf_socket_add(id, method, nf_conditions[condition])


def _socket_remove(id, condition = 0):
    return nf_socket_remove(id, nf_conditions[condition])


def init( module = None ):
    global timer_add
    global socket_add
    global dispatcher_add
    global timer_remove
    global socket_remove
    global dispatcher_remove
    global loop, step
    global nf_socket_remove
    global nf_socket_add
    global nf_conditions

    if not isinstance(loop, _Wrapper):
        raise RuntimeError('notifier loop already running')
    
    try:
        import notifier
    except ImportError:
        # use our own copy of pynotifier
        import pynotifier as notifier
        
    if notifier.loop:
        # pyNotifier should be used and already active
        log = logging.getLogger('notifier')
        log.info('pynotifier already running, I hope you know what you are doing')
    else:
        # find a good main loop
        if not module and sys.modules.has_key('gtk'):
            # The gtk module is loaded, this means that we will hook
            # ourself into the gtk main loop
            module = 'gtk'
        elif not module:
            # use generic
            module = 'generic'

        if getattr(notifier, module.upper()) is not None:
            # use the selected module
            notifier.init(getattr(notifier, module.upper()))
            if module.upper() == 'GTK':
                # add gtk thread support
                import gobject
                gobject.threads_init()
        elif module:
            raise AttributeError('no notifier module %s' % module)

        # delete basic notifier handler
        log = logging.getLogger('notifier')
        for l in log.handlers:
            log.removeHandler(l)

    timer_remove = notifier.timer_remove
    timer_add = notifier.timer_add

    nf_socket_remove = notifier.socket_remove
    nf_socket_add = notifier.socket_add
    nf_conditions = [ notifier.IO_READ, notifier.IO_WRITE ]
    socket_remove = _socket_remove
    socket_add = _socket_add
    
    dispatcher_add = notifier.dispatcher_add
    dispatcher_remove = notifier.dispatcher_remove

    loop = notifier.loop
    step = notifier.step
