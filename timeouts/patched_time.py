stdlib_time = __import__('time', level=0)

import timeouts


__patch__ = ['sleep']


for key in dir(stdlib_time):
    if key not in __patch__ and key not in \
            ('__builtins__', '__package__', '__file__'):
        globals()[key] = getattr(stdlib_time, key)


_orig_sleep = stdlib_time.sleep


def sleep(sleep_time):
    timeout, exception = timeouts.next_timeout()
    if timeout >= 0 and timeout < sleep_time:
        _orig_sleep(timeout)
        raise exception
    else:
        stdlib_time.sleep(sleep_time)
