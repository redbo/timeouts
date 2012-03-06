import threading
import sys

import timeouts.patched_socket
import timeouts.patched_time


__version__ = '0.2'

_timeout_stack = threading.local()

_to_patch = {'socket': timeouts.patched_socket,
            'time': timeouts.patched_time}

def patched(module_name):
    orig_modules = {}
    try:
        for name, module in _to_patch.iteritems():
            orig_modules[name] = sys.modules.get(name, None)
            sys.modules[name] = module
        return __import__(module_name, {}, {}, module_name.split('.')[:-1], 0)
    finally:
        for name, module in orig_modules.iteritems():
            if module:
                sys.modules[name] = module
            else:
                del sys.modules[name]


socket = timeouts.patched_socket
time = timeouts.patched_time
httplib = patched('httplib')


def monkey_patch():
    """
    Monkey patch blocking methods to time out and raise the timeout
    exception.
    """
    for name, lib in _to_patch.iteritems():
        stdlib_v = __import__(name)
        if hasattr(stdlib_v, '_timeout_patched'):
            continue
        for key in lib.__patch__:
            setattr(stdlib_v, key, getattr(lib, key))
        stdlib_v._timeout_patched = True


def next_timeout():
    """
    Returns (timeout, exception) for the next timeout in the stack.
    Or (None, None) if there are no timeouts in the stack.
    """
    if not getattr(_timeout_stack, 'values', None):
        return None, None
    timeout, exception = min(_timeout_stack.values)
    return timeout - time.time(), exception


class Timeout(BaseException):
    """
    A timeout.
    """
    def __init__(self, timeout):
        self.timeout = timeout
        if not hasattr(_timeout_stack, 'values'):
            _timeout_stack.values = []

    def __enter__(self):
        this_timeout = time.time() + self.timeout
        _timeout_stack.values.append((this_timeout, self))

    def __exit__(self, cls, value, traceback):
        _timeout_stack.values.pop()
