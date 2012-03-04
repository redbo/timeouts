import threading
import socket
import time
import sys


_timeout_stack = threading.local()

def monkey_patch():
    if not hasattr(socket, '_timeout_patched'):
        class new_socket(socket.socket):
            def __init__(self, *args, **kwargs):
                super(new_socket, self).__init__(*args, **kwargs)

                def patch(method_name):
                    old_method = getattr(super(new_socket, self), method_name)
                    def _patched_method(*args, **kwargs):
                        if not getattr(_timeout_stack, 'values', None):
                            return old_method(*args, **kwargs)
                        timeout, exception = min(_timeout_stack.values)
                        self.settimeout(timeout - time.time())
                        try:
                            return old_method(*args, **kwargs)
                        except socket.timeout:
                            cls, value, traceback = sys.exc_info()
                            raise type(exception), exception, traceback
                    return _patched_method

                for method_name in ('recv', 'sendall', 'sendto', 'connect',
                            'recvfrom', 'recvfrom_into', 'accept', 'send'):
                    setattr(self, method_name, patch(method_name))

        socket.socket = new_socket
        socket._timeout_patched = True

        if not hasattr(time, '_timeout_patched'):
            def patched_sleep():
                old_method = time.sleep
                def new_sleep(sleep_time):
                    if not getattr(_timeout_stack, 'values', None):
                        return old_method(sleep_time)
                    timeout, exception = min(_timeout_stack.values)
                    old_method(timeout - time.time())
                    cls, value, traceback = sys.exc_info()
                    raise type(exception), exception, traceback
                return new_sleep
            time.sleep = patched_sleep()
            time._timeout_patched = True


class Timeout(BaseException):
    def __init__(self, timeout):
        self.timeout = timeout
        if not hasattr(_timeout_stack, 'values'):
            _timeout_stack.values = []

    def __enter__(self):
        this_timeout = time.time() + self.timeout
        _timeout_stack.values.append((this_timeout, self))

    def __exit__(self, cls, value, traceback):
        _timeout_stack.values.pop()


if __name__ == '__main__':
    monkey_patch()
    start = time.time()

    class OuterTimeout(Timeout):
        pass

    class InnerTimeout(Timeout):
        pass

    try:
        with OuterTimeout(2):
            try:
                with InnerTimeout(10):
                    time.sleep(20)
            except InnerTimeout:
                print "INNER TIMEOUT CAUGHT", time.time() - start
    except OuterTimeout:
        print "OUTER TIMEOUT CAUGHT", time.time() - start
