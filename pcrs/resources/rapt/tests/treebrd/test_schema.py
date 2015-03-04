from unittest import TestCase
from rapt.treebrd.errors import RelationReferenceError
from rapt.treebrd.schema import Schema


class TestSchema(TestCase):
    def test_contains_when_empty(self):
        self.assertFalse(Schema({}).contains('relation'))

    def test_contains_when_false(self):
        self.assertFalse(Schema({'another_relation': []}).contains('relation'))

    def test_contains_when_true(self):
        self.assertTrue(Schema({'relation': []}).contains('relation'))

    def test_to_dict(self):
        expected = {'alpha': ['a1'], 'beta': ['b1']}
        actual = Schema(expected).to_dict()
        self.assertNotEquals(id(expected), id(actual))
        self.assertEqual(expected, actual)

    def test_get_attributes(self):
        raw = {'alpha': ['a1'], 'beta': ['b1']}
        expected = ['a1']
        actual = Schema(raw).get_attributes('alpha')
        self.assertNotEquals(id(expected), id(raw['alpha']))
        self.assertEqual(expected, actual)

    def test_add(self):
        schema = Schema({'alpha': ['a1']})
        schema.add('beta', ['b1'])
        self.assertTrue(schema.contains('beta'))
        self.assertEqual(['b1'], schema.get_attributes('beta'))

    def test_exception_when_name_conflicts(self):
        schema = Schema({'alpha': ['a1']})
        self.assertRaises(RelationReferenceError, schema.add, 'alpha', [])