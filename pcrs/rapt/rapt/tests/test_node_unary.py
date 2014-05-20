from unittest import TestCase
from rapt.node_attributes import AttributeList

from rapt.node import (AssignmentNode, RelationNode, ProjectNode, RenameNode,
                       SelectNode)
from rapt.translation_error import InputError, InputReferenceError, \
    AttributeReferenceError


class TestUnaryNode(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cls_schema = {
            'Questions': ['id', 'question'],
            'Answers': ['id', 'question', 'answer'],
            'AnswersTwin': ['id', 'question', 'answer'],
            'Ambiguous': ['twin', 'odd', 'twin']
        }


class TestSelect(TestUnaryNode):
    def setUp(self):
        self.child = RelationNode('Questions', self.cls_schema)
        self.node = SelectNode(self.child, 'id = 1', ['id'])

    def test_name(self):
        expected = 'Questions'
        self.assertEqual(expected, self.node.name)

    def test_attributes(self):
        expected = AttributeList(self.cls_schema['Questions'],
                                 'Questions').to_list()
        self.assertEqual(expected, self.node.attributes.to_list())

    def test_conditions(self):
        expected = '(id = 1)'
        self.assertEqual(expected, self.node.conditions)

    def test_multiple_conditions(self):
        node = SelectNode(self.child,
                          'id=id and question=\'Life?\'',
                          ['id', 'question'])
        expected = '(id=id and question=\'Life?\')'
        self.assertEqual(expected, node.conditions)

    def test_conditions_with_prefix(self):
        node = SelectNode(self.child,
                          'Question.id=id and question=\'Life?\'',
                          ['id', 'question'])
        expected = '(Question.id=id and question=\'Life?\')'
        self.assertEqual(expected, node.conditions)

    def test_child_has_conditions(self):
        node = SelectNode(self.node,
                          'Question.id=id and question=\'Life?\'',
                          ['id', 'question'])
        expected = '(id = 1) AND (Question.id=id and question=\'Life?\')'
        self.assertEqual(expected, node.conditions)

    def test_attribute_reference_error(self):
        self.assertRaises(AttributeReferenceError, SelectNode, self.child,
                          'ultimate=42', ['ultimate'])


class TestProject(TestUnaryNode):
    def setUp(self):
        self.child = RelationNode('Answers', self.cls_schema)

    def test_name(self):
        node = ProjectNode(self.child, ['id', 'question'])
        expected = 'Answers'
        self.assertEqual(expected, node.name)

    def test_conditions(self):
        node = ProjectNode(self.child, ['id', 'question'])
        expected = ''
        self.assertEqual(expected, node.conditions)

    def test_child_has_conditions(self):
        child = SelectNode(self.child, 'question=\'Life?\'', ['question'])
        node = ProjectNode(child, ['id'])
        expected = '(question=\'Life?\')'
        self.assertEqual(expected, node.conditions)

    def test_attributes(self):
        node = ProjectNode(self.child, ['id', 'question'])
        expected = ['Answers.id', 'Answers.question']
        self.assertEqual(expected, node.attributes.to_list())

    def test_attributes_prefixed(self):
        node = ProjectNode(self.child, ['Answers.id', 'Answers.question'])
        expected = ['Answers.id', 'Answers.question']
        self.assertEqual(expected, node.attributes.to_list())

    def test_attributes_mixed(self):
        node = ProjectNode(self.child, ['Answers.id', 'question'])
        expected = ['Answers.id', 'Answers.question']
        self.assertEqual(expected, node.attributes.to_list())

    def test_attributes_rearranged(self):
        node = ProjectNode(self.child, ['question', 'id'])
        expected = ['Answers.question', 'Answers.id']
        self.assertEqual(expected, node.attributes.to_list())

    def test_attributes_from_child(self):
        node = ProjectNode(self.child, ['id', 'question', 'answer'])
        expected = ['Answers.id', 'Answers.question', 'Answers.answer']
        self.assertEqual(expected, node.attributes.to_list())

    def test_attributes_from_project_child(self):
        child = ProjectNode(self.child, ['id', 'question'])
        node = ProjectNode(child, ['id'])
        expected = ['Answers.id']
        self.assertEqual(expected, node.attributes.to_list())

    def test_attribute_reference_error(self):
        self.assertRaises(InputReferenceError, ProjectNode, self.child,
                          ['Silence'])

    def test_attribute_reference_error_prefix(self):
        self.assertRaises(InputReferenceError, ProjectNode, self.child,
                          ['Answering.id'])

    def test_attribute_reference_error_too_many(self):
        node = ProjectNode(self.child, ['id', 'question'])
        self.assertRaises(InputReferenceError, ProjectNode, node,
                          ['id', 'question', 'answer'])


class TestRename(TestUnaryNode):
    def setUp(self):
        self.cls_schema = {
            'Questions': ['id', 'question'],
            'Answers': ['id', 'question', 'answer'],
            'AnswersTwin': ['id', 'question', 'answer'],
            'Ambiguous': ['twin', 'odd', 'twin']
        }
        self.child = RelationNode('Questions', self.cls_schema)

    def test_name(self):
        node = RenameNode('Apex', self.child, ['first', 'second'],
                          self.cls_schema)
        expected = 'Apex'
        self.assertEqual(expected, node.name)

    def test_conditions(self):
        node = RenameNode('Apex', self.child, ['first', 'second'],
                          self.cls_schema)
        expected = ''
        self.assertEqual(expected, node.conditions)

    def test_child_has_conditions(self):
        child = SelectNode(self.child, 'question=\'Life?\'', ['question'])
        node = RenameNode('Apex', child, ['first', 'second'], self.cls_schema)
        expected = ''
        self.assertEqual(expected, node.conditions)

    def test_attributes(self):
        node = RenameNode('Apex', self.child, ['first', 'second'],
                          self.cls_schema)
        expected = ['Apex.first', 'Apex.second']
        self.assertEqual(expected, node.attributes.to_list())

    def test_attributes_no_name(self):
        node = RenameNode(None, self.child, ['first', 'second'],
                          self.cls_schema)
        expected = ['first', 'second']
        self.assertEqual(expected, node.attributes.to_list())

    def test_attributes_no_renamed_attributes(self):
        node = RenameNode('Apex', self.child, None, self.cls_schema)
        expected = ['Apex.id', 'Apex.question']
        self.assertEqual(expected, node.attributes.to_list())

    def test_duplicate_relation_name(self):
        self.assertRaises(InputReferenceError, RenameNode, 'Answers',
                          self.child, ['first', 'second'], self.cls_schema)

    def test_ambiguous_attributes(self):
        self.assertRaises(InputError, RenameNode, 'Argon',
                          self.child, ['Alpha', 'Alpha'], self.cls_schema)

    def test_too_few_attributes(self):
        self.assertRaises(InputError, RenameNode, 'Argon',
                          self.child, ['Alpha'], self.cls_schema)

    def test_too_many_attributes(self):
        self.assertRaises(InputError, RenameNode, 'Argon',
                          self.child, ['x', 'y', 'z'], self.cls_schema)


class TestAssignment(TestUnaryNode):
    def setUp(self):
        self.schema = {
            'Questions': ['id', 'question'],
            'Answers': ['id', 'question', 'answer'],
            'AnswersTwin': ['id', 'question', 'answer'],
            'Ambiguous': ['twin', 'odd', 'twin']
        }
        self.child = RelationNode('Questions', self.schema)

    def test_name(self):
        node = AssignmentNode('Apex', self.child, ['a', 'b'], self.schema)
        expected = 'Apex'
        self.assertEqual(expected, node.name)

    def test_conditions(self):
        node = AssignmentNode('Apex', self.child, ['a', 'b'], self.schema)
        expected = ''
        self.assertEqual(expected, node.conditions)

    def test_child_has_conditions(self):
        child = SelectNode(self.child, 'question=\'Life?\'', ['question'])
        node = AssignmentNode('Apex', child, ['a', 'b'], self.schema)
        expected = '(question=\'Life?\')'
        self.assertEqual(expected, node.conditions)

    def test_attributes(self):
        node = AssignmentNode('Apex', self.child, ['a', 'b'], self.schema)
        expected = ['Apex.a', 'Apex.b']
        self.assertEqual(expected, node.attributes.to_list())

    def test_schema(self):
        AssignmentNode('Apex', self.child, ['a', 'b'], self.schema)
        expected = ['a', 'b']
        self.assertEqual(expected, self.schema['Apex'])

    def test_ambiguous_attributes_in_child(self):
        child = RelationNode('Ambiguous', self.schema)
        node = AssignmentNode('Apex', child, ['a', 'b', 'c'], self.schema)
        expected = ['Apex.a', 'Apex.b', 'Apex.c']
        self.assertEqual(expected, node.attributes.to_list())

    def test_duplicate_relation_name(self):
        self.assertRaises(InputReferenceError, AssignmentNode, 'Answers',
                          self.child, ['first', 'second'], self.schema)

    def test_ambiguous_attributes(self):
        self.assertRaises(InputError, AssignmentNode, 'Argon',
                          self.child, ['Alpha', 'Alpha'], self.schema)

    def test_too_few_attributes(self):
        self.assertRaises(InputError, AssignmentNode, 'Argon',
                          self.child, ['Alpha'], self.schema)

    def test_too_many_attributes(self):
        self.assertRaises(InputError, AssignmentNode, 'Argon',
                          self.child, ['x', 'y', 'z'], self.schema)
