import logging

from .rapt import Rapt

__version__ = '0.0.2'

# To add logging to a python file insert `log = logging.getLogger(__name__)`
# near the top at the module level.
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Turn logging on.
logging.basicConfig(level=logging.DEBUG)


def main():
    # """Entry point for the application script"""
    pass