from unittest import TestCase
from rapt.node_attributes import AttributeList
from rapt.constants import SET_SEMANTICS, BAG_SEMANTICS

from rapt.node import (RelationNode)
from rapt.translation_error import RelationReferenceError


class TestRelationNode(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = {
            'Questions': ['id', 'question'],
            'Answers': ['id', 'question', 'answer'],
            'AnswersTwin': ['id', 'question', 'answer']
        }

    def test_name(self):
        node = RelationNode('Answers', self.schema)
        expected = 'Answers'
        self.assertEqual(expected, node.name)

    def test_attributes(self):
        node = RelationNode('Answers', self.schema)
        expected = AttributeList(self.schema['Answers'], 'Answers').to_list()
        self.assertEqual(expected, node.attributes.to_list())

    def test_conditions(self):
        node = RelationNode('Answers', self.schema)
        self.assertEqual('', node.conditions)

    def test_to_sql_set(self):
        node = RelationNode('Questions', self.schema)
        expected = 'SELECT DISTINCT Questions.id, Questions.question ' \
                   'FROM {name}'.format(name='Questions')
        self.assertEqual(expected, node.to_sql(SET_SEMANTICS))

    def test_to_sql_bag(self):
        node = RelationNode('Questions', self.schema)
        expected = 'SELECT Questions.id, Questions.question ' \
                   'FROM {name}'.format(name='Questions')
        self.assertEqual(expected, node.to_sql(BAG_SEMANTICS))

    def test_exp(self):
        self.assertRaises(RelationReferenceError, RelationNode, 'srewsnA',
                          self.schema)