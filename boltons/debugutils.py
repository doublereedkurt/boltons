# -*- coding: utf-8 -*-
"""
A small set of utilities useful for debugging misbehaving
applications. Currently this focuses on ways to use :mod:`pdb`, the
built-in Python debugger.
"""

__all__ = ['pdb_on_signal', 'pdb_on_exception', 'trace_module']


def pdb_on_signal(signalnum=None):
    """Installs a signal handler for *signalnum*, which defaults to
    ``SIGINT``, or keyboard interrupt/ctrl-c. This signal handler
    launches a :mod:`pdb` breakpoint. Results vary in concurrent
    systems, but this technique can be useful for debugging infinite
    loops, or easily getting into deep call stacks.

    Args:
        signalnum (int): The signal number of the signal to handle
            with pdb. Defaults to :mod:`signal.SIGINT`, see
            :mod:`signal` for more information.
    """
    import pdb
    import signal
    if not signalnum:
        signalnum = signal.SIGINT

    old_handler = signal.getsignal(signalnum)

    def pdb_int_handler(sig, frame):
        signal.signal(signalnum, old_handler)
        pdb.set_trace()
        pdb_on_signal(signalnum)  # use 'u' to find your code and 'h' for help

    signal.signal(signalnum, pdb_int_handler)
    return


def pdb_on_exception(limit=100):
    """Installs a handler which, instead of exiting, attaches a
    post-mortem pdb console whenever an unhandled exception is
    encountered.

    Args:
        limit (int): the max number of stack frames to display when
            printing the traceback

    A similar effect can be achieved from the command-line using the
    following command::

      python -m pdb your_code.py

    But ``pdb_on_exception`` allows you to do this conditionally and within
    your application. To restore default behavior, just do::

      sys.excepthook = sys.__excepthook__
    """
    import pdb
    import sys
    import traceback

    def pdb_excepthook(exc_type, exc_val, exc_tb):
        traceback.print_tb(exc_tb, limit=limit)
        pdb.post_mortem(exc_tb)

    sys.excepthook = pdb_excepthook


def trace_module(modules):
    '''Prints lines of code as they are executed only within the
    given modules, in the current thread.

    Compare to '-t' option of trace from the standard library, made usable
    by having the condition inverted.  Only specifc modules are invluded
    in the output, instead of having to itemize modules to exclude.

    (Uses sys.settrace() so will interfere with other modules that want to own
    the trace function such as coverage, profile, and trace.)
    '''
    import sys

    if type(modules) is not list:
        modules = [modules]

    globalses = set()
    for module in modules:
        globalses.add(id(module.__dict__))

    def trace(frame, event, arg):
        if event == 'line':
            print frame.f_code.co_filename, frame.f_code.co_name, frame.f_lineno
        if event == 'call':
            if id(frame.f_globals) in globalses:
                return trace

    sys.settrace(trace)
