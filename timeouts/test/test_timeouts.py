import unittest

from timeouts import time, socket, Timeout


class OuterTimeout(Timeout):
    pass


class InnerTimeout(Timeout):
    pass


class TimeoutsTest(unittest.TestCase):
    def test_nested_timeouts(self):
        def nest_timeouts(inner, outer):
            with OuterTimeout(outer):
                with InnerTimeout(inner):
                    time.sleep(30)
        self.assertRaises(InnerTimeout, lambda: nest_timeouts(0.1, 3))
        self.assertRaises(OuterTimeout, lambda: nest_timeouts(3, 0.1))

    def test_socket_timeout(self):
        def timeout_socket():
            sock = socket.create_connection(('www.google.com', 80))
            with Timeout(0.1):
                sock.recv(8192)
        self.assertRaises(Timeout, timeout_socket)

if __name__ == '__main__':
    unittest.main()
