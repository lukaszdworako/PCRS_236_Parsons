import logging
from unittest import TestCase

from rapt.treebrd.errors import RelationReferenceError
from rapt.treebrd.node import Node, Operator, RelationNode
from rapt.treebrd.attributes import AttributeList
from rapt.treebrd.schema import Schema


class NodeTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        # logging.basicConfig(level=logging.NOTSET)
        pass

    def setUp(self):
        self.schema = Schema({
            'alpha': ['a1'],
            'beta': ['b1', 'b2'],
            'gamma': ['c1', 'c2', 'c3'],
            'twin': ['t1', 't2', 't3'],
            'twin_prime': ['t1', 't2', 't3'],
            'ambiguous': ['d1', 'd1']
        })
        self.alpha = RelationNode('alpha', self.schema)
        self.beta = RelationNode('beta', self.schema)
        self.gamma = RelationNode('gamma', self.schema)
        self.twin = RelationNode('twin', self.schema)
        self.twin_prime = RelationNode('twin_prime', self.schema)
        self.ambiguous = RelationNode('ambiguous', self.schema)


class TestNode(TestCase):
    def test_operator_from_init(self):
        expected = Operator.relation
        actual = Node(Operator.relation, None).operator
        self.assertEqual(expected, actual)

    def test_name_when_init_has_none(self):
        node = Node(Operator.relation, None)
        self.assertIsNone(node.name)

    def test_name_when_init_has_name(self):
        expected = 'alpha'
        actual = Node(Operator.relation, 'alpha').name
        self.assertEqual(expected, actual)

    def test_attributes_from_init_when_none(self):
        actual = Node(Operator.relation, None).attributes
        self.assertIsNone(actual)


class TestNodeEquality(TestCase):
    def test_equality_when_identical(self):
        node = Node(Operator.relation, 'borg')
        same = node
        self.assertTrue(node == same)

    def test_equality_when_same_operator_and_name(self):
        node = Node(Operator.relation, 'borg')
        twin = Node(Operator.relation, 'borg')
        self.assertTrue(node == twin)

    def test_non_equality_when_different_operator_and_name(self):
        node = Node(Operator.relation, 'borg')
        other = Node(Operator.project, 'other')
        self.assertTrue(node != other)

    def test_non_equality_when_different_operator(self):
        node = Node(Operator.relation, 'borg')
        other = Node(Operator.project, 'borg')
        self.assertTrue(node != other)

    def test_non_equality_when_different_name(self):
        node = Node(Operator.relation, 'borg')
        other = Node(Operator.relation, 'other')
        self.assertTrue(node != other)


class TestRelationNode(NodeTestCase):
    def test_operator_from_init(self):
        expected = Operator.relation
        actual = RelationNode('alpha', self.schema).operator
        self.assertEqual(expected, actual)

    def test_exception_raised_when_name_not_in_schema(self):
        self.assertRaises(RelationReferenceError, RelationNode, 'unknown',
                          self.schema)

    def test_attributes_when_name_is_in_schema(self):
        expected = AttributeList(self.schema.get_attributes('alpha'),
                                 'alpha').to_list()
        node = RelationNode('alpha', self.schema)
        self.assertEqual(expected, node.attributes.to_list())