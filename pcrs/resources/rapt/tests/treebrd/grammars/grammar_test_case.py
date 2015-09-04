import unittest

__author__ = 'Noel'


class GrammarTestCase(unittest.TestCase):
    @staticmethod
    def parse_function(parser):
        """
        Return a function that parses a value with the specified parser and
        returns the results as a list.
        """

        def function(value):
            return parser.parseString(value, parseAll=True).asList()

        return function