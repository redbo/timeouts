stdlib_time = __import__('time', level=0)

import timeouts


__patch__ = ['sleep']


timeouts.patch(globals(), stdlib_time, __patch__)

_orig_sleep = stdlib_time.sleep

def sleep(sleep_time):
    timeout, exception = timeouts.next_timeout()
    if timeout >= 0 and timeout < sleep_time:
        _orig_sleep(timeout)
        raise exception
    else:
        stdlib_time.sleep(sleep_time)
