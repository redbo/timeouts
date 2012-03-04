stdlib_socket = __import__('socket', level=0)

import timeouts


__patch__ = ['socket', 'SocketType', '_socketobject', 'create_connection']

timeouts.patch(globals(), stdlib_socket, __patch__)

_orig_socket = stdlib_socket.socket
class socket(_orig_socket):
    def __init__(self, *args, **kwargs):
        super(socket, self).__init__(*args, **kwargs)

        def patch(func_name):
            orig_func = getattr(self, func_name)
            def new_func(*args, **kwargs):
                timeout, exception = timeouts.next_timeout()
                if timeout < 0:
                    return orig_func(*args, **kwargs)
                self.settimeout(timeout)
                try:
                    return orig_func(*args, **kwargs)
                except stdlib_socket.timeout:
                    cls, value, traceback = sys.exc_info()
                    raise type(exception), exception, traceback
            return new_func

        for func in ('recv', 'sendall', 'sendto', 'connect',
                     'recvfrom', 'accept', 'send'):
            setattr(self, func, patch(func))

SocketType = _socketobject = socket


def create_connection(address,
                      timeout=_GLOBAL_DEFAULT_TIMEOUT,
                      source_address=None):
    """Connect to *address* and return the socket object.

    Convenience function.  Connect to *address* (a 2-tuple ``(host,
    port)``) and return the socket object.  Passing the optional
    *timeout* parameter will set the timeout on the socket instance
    before attempting to connect.  If no *timeout* is supplied, the
    global default timeout setting returned by :func:`getdefaulttimeout`
    is used.
    """

    msg = "getaddrinfo returns an empty list"
    host, port = address
    for res in getaddrinfo(host, port, 0, SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        sock = None
        try:
            sock = socket(af, socktype, proto)
            if timeout is not _GLOBAL_DEFAULT_TIMEOUT:
                sock.settimeout(timeout)
            if source_address:
                sock.bind(source_address)
            sock.connect(sa)
            return sock

        except error, msg:
            if sock is not None:
                sock.close()
