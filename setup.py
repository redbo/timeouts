"""
Eventlet/gevent style timeouts for regular python.
"""

from setuptools import setup
from timeouts import __version__

setup(name='timeouts',
      version=__version__,
      description='Python Timeouts',
      author='Michael Barton',
      author_email='mike@weirdlooking.com',
      url='https://github.com/redbo/timeouts/',
      license='BSD',
      platforms = ["any"],
      long_description = __doc__,
      packages=['timeouts'],
     )
