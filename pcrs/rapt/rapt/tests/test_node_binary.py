from unittest import TestCase

from rapt.node import RelationNode, UnionNode, JoinNode, \
    DifferenceNode, BinaryNode, SelectNode, IntersectNode
from rapt.translation_error import InputError


class TestBinaryNode(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = {
            'Questions': ['id', 'question'],
            'Answers': ['id', 'question', 'answer'],
            'AnswersTwin': ['id', 'question', 'answer']
        }

    def test_binary_children(self):
        left = RelationNode('Questions', self.schema)
        right = RelationNode('Answers', self.schema)
        node = BinaryNode(left, right)
        self.assertEqual(left, node.left)
        self.assertEqual(right, node.right)


class TestUnionNode(TestCase):
    def setUp(self):
        self.schema = {
            'Questions': ['id', 'question'],
            'Answers': ['id', 'question', 'answer'],
            'AnswersTwin': ['id', 'question', 'answer']
        }
        self.left = RelationNode('Questions', self.schema)
        self.right = RelationNode('Answers', self.schema)

    def test_name(self):
        node = UnionNode(self.left, self.left)
        expected = '_{}'.format(id(node))
        self.assertEqual(expected, node.name)

    def test_children(self):
        node = UnionNode(self.left, self.left)
        self.assertEqual(self.left, node.left)
        self.assertEqual(self.left, node.right)

    def test_conditions(self):
        node = UnionNode(self.left, self.left)
        expected = ''
        self.assertEqual(expected, node.conditions)

    def test_child_has_conditions(self):
        left = SelectNode(self.left, 'question=\'Life?\'', ['question'])
        right = SelectNode(self.left, 'question=\'Life?\'', ['question'])
        node = UnionNode(left, right)
        expected = ''
        self.assertEqual(expected, node.conditions)

    def test_attributes(self):
        node = UnionNode(self.left, self.left)
        expected = ['id', 'question']
        self.assertEqual(expected, node.attributes.to_list())

    def test_mismatch(self):
        self.assertRaises(InputError, UnionNode, self.left, self.right)


class TestDifferenceNode(TestCase):
    def setUp(self):
        self.schema = {
            'Questions': ['id', 'question'],
            'Answers': ['id', 'question', 'answer'],
            'AnswersTwin': ['id', 'question', 'answer']
        }
        self.left = RelationNode('Questions', self.schema)
        self.right = RelationNode('Answers', self.schema)

    def test_name(self):
        node = DifferenceNode(self.left, self.left)
        expected = '_{}'.format(id(node))
        self.assertEqual(expected, node.name)

    def test_children(self):
        node = DifferenceNode(self.left, self.left)
        self.assertEqual(self.left, node.left)
        self.assertEqual(self.left, node.right)

    def test_conditions(self):
        node = DifferenceNode(self.left, self.left)
        expected = ''
        self.assertEqual(expected, node.conditions)

    def test_child_has_conditions(self):
        left = SelectNode(self.left, 'question=\'Life?\'', ['question'])
        right = SelectNode(self.left, 'question=\'Life?\'', ['question'])
        node = DifferenceNode(left, right)
        expected = ''
        self.assertEqual(expected, node.conditions)

    def test_attributes(self):
        node = DifferenceNode(self.left, self.left)
        expected = ['id', 'question']
        self.assertEqual(expected, node.attributes.to_list())

    def test_mismatch(self):
        self.assertRaises(InputError, DifferenceNode, self.left, self.right)


class TestIntersectionNode(TestCase):
    def setUp(self):
        self.schema = {
            'Questions': ['id', 'question'],
            'Answers': ['id', 'question', 'answer'],
            'AnswersTwin': ['id', 'question', 'answer']
        }
        self.left = RelationNode('Questions', self.schema)
        self.right = RelationNode('Answers', self.schema)

    def test_name(self):
        node = IntersectNode(self.left, self.left)
        expected = '_{}'.format(id(node))
        self.assertEqual(expected, node.name)

    def test_children(self):
        node = IntersectNode(self.left, self.left)
        self.assertEqual(self.left, node.left)
        self.assertEqual(self.left, node.right)

    def test_conditions(self):
        node = IntersectNode(self.left, self.left)
        expected = ''
        self.assertEqual(expected, node.conditions)

    def test_child_has_conditions(self):
        left = SelectNode(self.left, 'question=\'Life?\'', ['question'])
        right = SelectNode(self.left, 'question=\'Life?\'', ['question'])
        node = IntersectNode(left, right)
        expected = ''
        self.assertEqual(expected, node.conditions)

    def test_attributes(self):
        node = IntersectNode(self.left, self.left)
        expected = ['id', 'question']
        self.assertEqual(expected, node.attributes.to_list())

    def test_mismatch(self):
        self.assertRaises(InputError, IntersectNode, self.left, self.right)


class TestJoinNode(TestCase):
    def setUp(self):
        self.schema = {
            'Questions': ['id', 'question'],
            'Answers': ['id', 'question', 'answer'],
            'AnswersTwin': ['id', 'question', 'answer']
        }
        self.left = RelationNode('Questions', self.schema)
        self.right = RelationNode('Answers', self.schema)

    def test_name(self):
        node = JoinNode(self.left, self.right)
        expected = '_{}'.format(id(node))
        self.assertEqual(expected, node.name)

    def test_conditions(self):
        node = JoinNode(self.left, self.right)
        expected = ''
        self.assertEqual(expected, node.conditions)

    def test_child_has_conditions(self):
        left = SelectNode(self.left, 'question=\'Life?\'', ['question'])
        right = SelectNode(self.right, 'question=\'Life?\'', ['question'])
        node = JoinNode(left, right)
        expected = ''
        self.assertEqual(expected, node.conditions)

    def test_children(self):
        node = JoinNode(self.left, self.right)
        self.assertEqual(self.left, node.left)
        self.assertEqual(self.right, node.right)

    def test_attributes(self):
        node = JoinNode(self.left, self.right)
        expected = ['Questions.id', 'Questions.question', 'Answers.id',
                    'Answers.question', 'Answers.answer']
        self.assertEqual(expected, node.attributes.to_list())

    def test_attributes_left_join(self):
        left = JoinNode(self.left, self.right)
        node = JoinNode(left, self.left)
        expected = ['Questions.id', 'Questions.question', 'Answers.id',
                    'Answers.question', 'Answers.answer', 'Questions.id',
                    'Questions.question']
        self.assertEqual(expected, node.attributes.to_list())