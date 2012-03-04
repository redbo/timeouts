import threading
import sys


_timeout_stack = threading.local()


def next_timeout():
    """
    Returns (timeout, exception) for the next timeout in the stack.
    Or (-1, None) if there are no timeouts in the stack.
    """
    if not getattr(_timeout_stack, 'values', None):
        return -1, None
    timeout, exception = min(_timeout_stack.values)
    return timeout - time.time(), exception


def patch(globals, lib, patchlist):
    for key in dir(lib):
        if key not in patchlist and key not in \
                ('__builtins__', '__package__', '__file__'):
            globals[key] = getattr(lib, key)


def monkey_patch():
    """
    Monkey patch blocking methods to time out and raise the timeout
    exception.
    """
    for lib in ('socket', 'time'):
        stdlib_v = __import__(lib)
        timeouts_v = __import__('timeouts.' + lib, fromlist=['timeouts'])
        if hasattr(stdlib_v, '_timeout_patched'):
            continue
        for key in timeouts_v.__patch__:
            setattr(stdlib_v, key, getattr(timeouts_v, key))
        stdlib_v._timeout_patched = True


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
