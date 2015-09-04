import functools
from unittest import TestCase


class TestTransformer(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.schema = {
            'alpha': ['a1', 'a2', 'a3'],
            'alphatwin': ['a1', 'a2', 'a3'],
            'alphaprime': ['a1', 'a4', 'a5'],
            'beta': ['b1', 'b2', 'b3'],
            'gamma': ['g1', 'g2'],
            'gammaprime': ['g1', 'g2'],
            'gammatwin': ['g1', 'g2'],
            'delta': ['d1', 'd2'],
            'ambiguous': ['a', 'a', 'b']
        }

    def translate_func(self, func, schema=None):
        schema = schema or self.schema
        return functools.partial(func, schema=schema)
