# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# async.py - Async callback handling (InProgress)
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# kaa.notifier - Mainloop and callbacks
# Copyright (C) 2006-2008 Dirk Meyer, Jason Tackaberry, et al.
#
# First Version: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
# Please see the file AUTHORS for a complete list of authors.
#
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version
# 2.1 as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301 USA
#
# -----------------------------------------------------------------------------

__all__ = [ 'TimeoutException', 'InProgress', 'InProgressCallback',
            'InProgressSignals', 'InProgressList', 'AsyncException',
            'AsyncExceptionBase', 'make_exception_class' ]

# python imports
import sys
import logging
import traceback
import time
import _weakref
import threading
import types

# kaa.notifier imports
from callback import Callback
from signals import Signal
from kaa.utils import property

# get logging object
log = logging.getLogger('notifier.async')


def make_exception_class(name, bases, dict):
    """
    Class generator for AsyncException.  Creates AsyncException class
    which derives the class of a particular Exception instance.
    """
    def create(exc, stack, *args):
        from new import classobj
        e = classobj(name, bases + (exc.__class__,), {})(exc, stack, *args)
        return e

    return create


class AsyncExceptionBase(Exception):
    """
    Base class for asynchronous exceptions.  This class can be used to raise
    exceptions where the traceback object is not available.  The stack is
    stored (which is safe to reference and can be pickled) instead, and when
    AsyncExceptionBase instances are printed, the original traceback will
    be printed.

    This class will proxy the given exception object.
    """
    def __init__(self, exc, stack, *args):
        self._kaa_exc = exc
        self._kaa_exc_stack = stack
        self._kaa_exc_args = args

    def __getattribute__(self, attr):
        # Used by python 2.5, where exceptions are new-style classes.
        if attr.startswith('_kaa'):
            return super(AsyncExceptionBase, self).__getattribute__(attr)
        return getattr(self._kaa_exc, attr)

    def __getattr__(self, attr):
        # Used by python 2.4, where exceptions are old-style classes.
        exc = self._kaa_exc
        if attr == '__members__':
            return [ x for x in dir(exc) if not callable(getattr(exc, x)) ]
        elif attr == '__methods__':
            return [ x for x in dir(exc) if callable(getattr(exc, x)) ]
        return self.__getattribute__(attr)

    def _kaa_get_header(self):
        return 'Exception raised asynchronously; traceback follows:'

    def __str__(self):
        dump = ''.join(traceback.format_list(self._kaa_exc_stack))
        info = '%s: %s' % (self._kaa_exc.__class__.__name__, str(self._kaa_exc))
        return self._kaa_get_header() + '\n' + dump + info


class AsyncException(AsyncExceptionBase):
    __metaclass__ = make_exception_class


class TimeoutException(Exception):
    pass


class InProgress(Signal):
    """
    An InProgress class used to return from function calls that need more time
    to continue. It is possible to connect to an object of this class like
    Signals. The member 'exception' is a second signal to get
    notification of an exception raised later.
    """
    class Progress(Signal):
        """
        Generic progress status object for InProgress. This object can be
        used as 'progress' member of an InProgress object and the caller
        can monitor the progress.
        """
        def __init__(self, max=0):
            super(InProgress.Progress, self).__init__()
            self.start_time = time.time()
            self.pos = 0
            self.max = max


        def set(self, pos=None, max=None):
            """
            Set new status. The new status is pos of max.
            """
            if max is not None:
                self.max = max
            if pos is not None:
                self.pos = pos
            if pos > self.max:
                self.max = pos
            self.emit(self)


        def update(self, diff=1):
            """
            Update position by the given difference.
            """
            self.set(self.pos + diff)


        def get_progressbar(self, width=70):
            """
            Return a small ASCII art progressbar.
            """
            n = 0
            if self.max:
                n = int((self.pos / float(self.max)) * (width-3))
            s = '|%%%ss|' % (width-2)
            return s % ("="*n + ">").ljust(width-2)

        @property
        def elapsed(self):
            """
            Return time elapsed since the operation started.
            """
            return time.time() - self.start_time

        @property
        def eta(self):
            """
            Estimated time left to complete the operation. Depends on the
            operation itself if this is correct or not.
            """
            if not self.pos:
                return 0
            sec = (time.time() - self.start_time) / self.pos
            # we assume every step takes the same amount of time
            return sec * (self.max - self.pos)

        @property
        def percentage(self):
            """
            Return percentage of steps done.
            """
            if self.max:
                return (self.pos * 100) / self.max
            return 0


    def __init__(self):
        """
        Create an InProgress object.
        """
        Signal.__init__(self)
        self.exception = Signal()
        self._finished = False
        self._finished_event = threading.Event()
        self._unhandled_exception = None
        self.progress = None


    def finish(self, result):
        """
        This function should be called when the creating function is
        done and no longer in progress.

        This method returns self, which makes it convenient to prime InProgress
        objects with a finished value.
        """
        if self._finished:
            raise RuntimeError('%s already finished' % self)
        if isinstance(result, InProgress):
            # we are still not finished, link to this new InProgress
            self.link(result)
            return self

        # store result
        self._finished = True
        self._result = result
        self._exception = None
        # Wake any threads waiting on us
        self._finished_event.set()
        # emit signal
        self.emit_when_handled(result)
        # cleanup
        self.disconnect_all()
        self.exception.disconnect_all()
        return self


    def throw(self, type, value, tb):
        """
        This function should be called when the creating function is
        done because it raised an exception.
        """
        # This function must deal with a tricky problem.  See:
        # http://mail.python.org/pipermail/python-dev/2005-September/056091.html
        #
        # Ideally, we want to store the traceback object so we can defer the
        # exception handling until some later time.  The problem is that by
        # storing the traceback, we create some ridiculously deep circular
        # references.
        #
        # The way we deal with this is to pass along the traceback object to
        # any handler that can handle the exception immediately, and then
        # discard the traceback.  A stringified formatted traceback is attached
        # to the exception in the formatted_traceback attribute.
        #
        # The above URL suggests a possible non-trivial workaround: create a
        # custom traceback object in C code that preserves the parts of the
        # stack frames needed for printing tracebacks, but discarding objects
        # that would create circular references.  This might be a TODO.

        self._finished = True
        self._exception = type, value, tb
        self._unhandled_exception = True
        stack = traceback.extract_tb(tb)

        # Attach a stringified traceback to the exception object.  Right now,
        # this is the best we can do for asynchronous handlers.
        trace = ''.join(traceback.format_exception(*self._exception)).strip()
        value.formatted_traceback = trace

        # Wake any threads waiting on us.  We've initialized _exception with
        # the traceback object, so any threads that call get_result() between
        # now and the end of this function will have an opportunity to get
        # the live traceback.
        self._finished_event.set()

        if self.exception.count() == 0:
            # There are no exception handlers, so we know we will end up
            # queuing the traceback in the exception signal.  Set it to None
            # to prevent that.
            tb = None

        if self.exception.emit_when_handled(type, value, tb) == False:
            # A handler has acknowledged handling this exception by returning
            # False.  So we won't log it.
            self._unhandled_exception = None

        if self._unhandled_exception:
            # This exception was not handled synchronously, so we set up a
            # weakref object with a finalize callback to a function that
            # logs the exception.  We could do this in __del__, except that
            # the gc refuses to collect objects with a destructor.  The weakref
            # kludge lets us accomplish the same thing without actually using
            # __del__.
            #
            # If the exception is passed back via get_result(), then it is
            # considered handled, and it will not be logged.
            cb = Callback(InProgress._log_exception, trace, value)
            self._unhandled_exception = _weakref.ref(self, cb)

        # Remove traceback from stored exception.  If any waiting threads
        # haven't gotten it by now, it's too late.
        if not isinstance(value, AsyncExceptionBase):
            value = AsyncException(value, stack)
        self._exception = value.__class__, value, None

        # cleanup
        self.disconnect_all()
        self.exception.disconnect_all()


    @classmethod
    def _log_exception(cls, weakref, trace, exc):
        """
        Callback to log unhandled exceptions.
        """
        if isinstance(exc, (SystemExit, KeyboardInterrupt)):
            # We have an unhandled asynchronous SystemExit or KeyboardInterrupt
            # exception.  Rather than logging it, we reraise it in the main
            # loop so that the main loop exception handler can act
            # appropriately.
            import main
            def reraise():
                raise exc
            return main.signals['step'].connect_once(reraise)

        log.error('Unhandled %s exception:\n%s', cls.__name__, trace)


    def is_finished(self):
        """
        Return if the InProgress is finished.
        """
        return self._finished


    def get_result(self):
        """
        Get the results when finished.
        The function will either return the result or raise the exception
        provided to the exception function.
        """
        if not self._finished:
            raise RuntimeError('operation not finished')
        if self._exception:
            self._unhandled_exception = None
            if self._exception[2]:
                # We have the traceback, so we can raise using it.
                exc_type, exc_value, exc_tb_or_stack = self._exception
                raise exc_type, exc_value, exc_tb_or_stack
            else:
                # No traceback, so construct an AsyncException based on the
                # stack.
                raise self._exception[1]

        return self._result


    def timeout(self, timeout, callback=None):
        """
        Return an InProgress object linked to this one that will throw
        a TimeoutException if this object is not finished in time. This
        will not affect this InProgress object. If callback is given, the
        callback will be called just before TimeoutException is raised.
        """
        # Import modules here rather than globally to avoid circular importing.
        from timer import OneShotTimer
        async = InProgress()
        def trigger():
            self.disconnect(async.finish)
            self.exception.disconnect(async.throw)
            if not async._finished:
                if callback:
                    callback()
                async.throw(TimeoutException, TimeoutException('timeout'), None)
        async.link(self)
        OneShotTimer(trigger).start(timeout)
        return async


    def execute(self, func, *args, **kwargs):
        """
        Execute the given function and return the result or exception in the
        InProgress object. Returns self as result of the execution.
        """
        try:
            result = func(*args, **kwargs)
        except:
            self.throw(*sys.exc_info())
        else:
            self.finish(result)
        return self

    
    def wait(self, timeout = None):
        """
        Waits for the result (or exception) of the InProgress object.  The
        main loop is kept alive if waiting in the main thread, otherwise
        the thread is blocked until another thread finishes the InProgress.

        If timeout is specified, wait() blocks for at most timeout seconds
        (which may be fractional).  If wait times out, a TimeoutException is
        raised.
        """
        # Import modules here rather than globally to avoid circular importing.
        import main
        from thread import is_mainthread
        if is_mainthread() or not main.is_running():
            # We're waiting in the main thread, so we must keep the mainloop
            # alive by calling main.loop() until we're finished.
            main.loop(lambda: not self.is_finished(), timeout)
        else:
            # We're waiting in some other thread, so wait for some other
            # thread to wake us up.
            self._finished_event.wait(timeout)

        if not self.is_finished():
            raise TimeoutException

        return self.get_result()


    def link(self, in_progress):
        """
        Links with another InProgress object.  When the supplied in_progress
        object finishes (or throws), we do too.
        """
        in_progress.connect_both(self.finish, self.throw)


    def _connect(self, callback, args = (), kwargs = {}, once = False,
                 weak = False, pos = -1):
        """
        Internal connect function. Always set once to True because InProgress
        will be emited only once.
        """
        return Signal._connect(self, callback, args, kwargs, True, weak, pos)


    def connect_both(self, finished, exception):
        """
        Connect a finished and an exception callback without extra arguments.
        """
        self.connect(finished)
        self.exception.connect_once(exception)



class InProgressCallback(InProgress):
    """
    InProgress object that can be used as a callback for an async
    function. The InProgress object will be finished when it is
    called. Special support for Signals that will finish the InProgress
    object when the signal is emited.
    """
    def __init__(self, func=None):
        InProgress.__init__(self)
        if func is not None:
            if isinstance(func, Signal):
                func = func.connect_once
            # connect self as callback
            func(self)


    def __call__(self, *args, **kwargs):
        """
        Call the InProgressCallback by the external function. This will
        finish the InProgress object.
        """
        # try to get the results as the caller excepts them
        if args and kwargs:
            # no idea how to merge them
            return self.finish((args, kwargs))
        if kwargs and len(kwargs) == 1:
            # return the value
            return self.finish(kwargs.values()[0])
        if kwargs:
            # return as dict
            return self.finish(kwargs)
        if len(args) == 1:
            # return value
            return self.finish(args[0])
        if len(args) > 1:
            # return as list
            return self.finish(args)
        return self.finish(None)


class InProgressSignals(InProgress):
    """
    InProgress object that will be finished if one of the provided
    signals is emited. The return value is the number of the signal
    starting with 0. A second interface is to provide a dict of signals
    as first parameter and the dict keys after that. E.g.
    InProgressSignals(object.signals['completed'], object.signals['failed'])
    InProgressSignals(object.signals, 'completed', 'failed')
    """
    def __init__(self, *signals):
        assert(signals)
        if isinstance(signals[0], dict):
            signals = [ signals[0][key] for key in signals[1:] ]
        for num, signal in enumerate(signals):
            signal.connect_once(self.finish, num).set_user_args_first()
        self._signals = signals
        super(InProgressSignals, self).__init__()


    def finish(self, result, *args):
        """
        Callback when one signal is emited.
        """
        self.signal_args = args
        for num, signal in enumerate(self._signals):
            signal.disconnect(self.finish, num)
        self._signals = []
        return super(InProgressSignals, self).finish(result)


class InProgressList(InProgress):
    """
    InProgress object that will finish when all InProgress objects given to
    the constructor are finished. This object will never raise an exception
    nor will it provide the results of the given InProgress objects. Use
    get_result() on each InProgress object to get the required result.
    """
    def __init__(self, objects):
        super(InProgressList, self).__init__()
        self._counter = len(objects) or 1
        for obj in objects:
            obj.connect(self.finish)
            obj.exception.connect(self.finish)
        if not objects:
            self.finish(None)

    def finish(self, result):
        self._counter -= 1
        if not self._counter:
            super(InProgressList, self).finish(None)
