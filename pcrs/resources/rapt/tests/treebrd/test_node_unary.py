from rapt.treebrd.errors import (AttributeReferenceError, InputError,
                                 InputReferenceError)
from rapt.treebrd.node import (ProjectNode, RenameNode, SelectNode, UnaryNode,
                               Operator, AssignNode, Node)
from rapt.treebrd.attributes import AttributeList
from tests.treebrd.test_node import NodeTestCase


class UnaryTestCase(NodeTestCase):
    pass


class TestUnaryNode(UnaryTestCase):
    def test_operator_from_init(self):
        actual = UnaryNode(Operator.select, self.alpha).operator
        self.assertEqual(Operator.select, actual)

    def test_name_when_init_has_none_is_child_name(self):
        node = UnaryNode(Operator.relation, self.alpha)
        expected = 'alpha'
        self.assertEqual(expected, node.name)

    def test_name_when_init_has_name(self):
        node = UnaryNode(Operator.relation, self.alpha, 'a_name')
        self.assertEqual('a_name', node.name)

    def test_child_after_init(self):
        node = UnaryNode(Operator.relation, self.alpha)
        self.assertEqual(self.alpha, node.child)

    def test_attributes_are_copied_from_child_when_init(self):
        expected = AttributeList(self.schema.get_attributes('beta'),
                                 'beta').to_list()
        node = UnaryNode(Operator.relation, self.beta, self.schema)
        self.assertEqual(expected, node.attributes.to_list())


class TestUnaryNodeEquality(UnaryTestCase):
    def test_equality_when_identical(self):
        node = UnaryNode(Operator.relation, Node(Operator.relation))
        same = node
        self.assertTrue(node == same)

    def test_equality_when_same_operator_and_name_and_child(self):
        node = UnaryNode(Operator.relation, self.alpha, 'borg')
        twin = UnaryNode(Operator.relation, self.alpha, 'borg')
        self.assertTrue(node == twin)

    def test_non_equality_when_different_operator(self):
        node = UnaryNode(Operator.relation, self.alpha, 'borg')
        other = UnaryNode(Operator.project, self.alpha, 'borg')
        self.assertTrue(node != other)

    def test_non_equality_when_different_name(self):
        node = UnaryNode(Operator.relation, self.alpha, 'borg')
        other = UnaryNode(Operator.relation, self.alpha, 'other')
        self.assertTrue(node != other)

    def test_non_equality_when_different_child(self):
        node = UnaryNode(Operator.relation, self.alpha, 'borg')
        other = UnaryNode(Operator.relation, self.beta, 'other')
        self.assertTrue(node != other)

    def test_non_equality_when_different_operator_and_name(self):
        node = UnaryNode(Operator.relation, self.alpha, 'borg')
        other = UnaryNode(Operator.project, self.alpha, 'other')
        self.assertTrue(node != other)

    def test_non_equality_when_different_operator_and_child(self):
        node = UnaryNode(Operator.relation, self.alpha, 'borg')
        other = UnaryNode(Operator.project, self.beta, 'borg')
        self.assertTrue(node != other)

    def test_non_equality_when_different_name_and_child(self):
        node = UnaryNode(Operator.relation, self.alpha, 'borg')
        other = UnaryNode(Operator.relation, self.beta, 'other')
        self.assertTrue(node != other)

    def test_non_equality_when_different_operator_and_name_and_child(self):
        node = UnaryNode(Operator.relation, self.alpha, 'borg')
        other = UnaryNode(Operator.project, self.beta, 'other')
        self.assertTrue(node != other)


class TestSelect(UnaryTestCase):
    def test_operator_is_correct(self):
        actual = SelectNode(self.alpha, 'a1=42').operator
        self.assertEqual(Operator.select, actual)

    def test_condition_when_init_has_condition(self):
        condition = 'a1=42'
        actual = SelectNode(self.alpha, condition).conditions
        self.assertEqual(condition, actual)

    def test_condition_when_multiple_conditions(self):
        condition = 'a1>41 and a1<43'
        node = SelectNode(self.alpha, condition)
        self.assertEqual(condition, node.conditions)

    def test_condition_when_with_prefix(self):
        condition = 'alpha.a1>41'
        node = SelectNode(self.alpha, condition)
        self.assertEqual(condition, node.conditions)

    def test_condition_when_multiple_conditions_with_prefix(self):
        condition = 'alpha.a1>41 and alpha.a1<43'
        node = SelectNode(self.alpha, condition)
        self.assertEqual(condition, node.conditions)

    def test_exception_when_first_attribute_in_condition_is_wrong(self):
        self.assertRaises(AttributeReferenceError, SelectNode, self.alpha,
                          'a2=42')

    def test_exception_when_second_attribute_in_condition_is_wrong(self):
        self.assertRaises(AttributeReferenceError, SelectNode, self.alpha,
                          'a1=a2')

    def test_exception_when_both_attributes_in_condition_are_wrong(self):
        self.assertRaises(AttributeReferenceError, SelectNode, self.alpha,
                          'a2=a3')

    def test_exception_when_prefix_in_condition_is_wrong(self):
        self.assertRaises(AttributeReferenceError, SelectNode, self.alpha,
                          'beta.a1=42')

    def test_exception_when_ambiguous_attributes(self):
        self.assertRaises(AttributeReferenceError, SelectNode, self.ambiguous,
                          'd1<5')


class TestProject(UnaryTestCase):
    def test_operator_is_correct(self):
        actual = ProjectNode(self.alpha, []).operator
        self.assertEqual(Operator.project, actual)

    def test_attributes_when_init_with_empty_list(self):
        node = ProjectNode(self.beta, [])
        self.assertEqual([], node.attributes.to_list())

    def test_attributes_when_init_with_all_attributes(self):
        expected = AttributeList(self.schema.get_attributes('beta'),
                                 'beta').to_list()
        node = ProjectNode(self.beta, ['b1', 'b2'])
        self.assertEqual(expected, node.attributes.to_list())

    def test_attributes_when_init_with_some_attributes(self):
        expected = ['gamma.c2', 'gamma.c3']
        node = ProjectNode(self.gamma, ['c2', 'c3'])
        self.assertEqual(expected, node.attributes.to_list())

    def test_attributes_when_init_with_some_attributes_different_order(self):
        expected = ['gamma.c3', 'gamma.c2']
        node = ProjectNode(self.gamma, ['c3', 'c2'])
        self.assertEqual(expected, node.attributes.to_list())

    def test_attributes_when_init_with_single_attribute(self):
        expected = ['gamma.c2']
        node = ProjectNode(self.gamma, ['c2'])
        self.assertEqual(expected, node.attributes.to_list())

    def test_attributes_when_init_with_project_child(self):
        expected = ['gamma.c1']
        child = ProjectNode(self.gamma, ['c1', 'c2'])
        node = ProjectNode(child, ['c1'])
        self.assertEqual(expected, node.attributes.to_list())

    def test_attributes_when_prefixed(self):
        expected = ['gamma.c1', 'gamma.c2']
        node = ProjectNode(self.gamma, ['gamma.c1', 'gamma.c2'])
        self.assertEqual(expected, node.attributes.to_list())

    def test_attributes_when_mixed(self):
        expected = ['gamma.c1', 'gamma.c2']
        node = ProjectNode(self.gamma, ['gamma.c1', 'c2'])
        self.assertEqual(expected, node.attributes.to_list())

    def test_exception_when_attribute_does_not_exist(self):
        self.assertRaises(AttributeReferenceError, ProjectNode, self.alpha,
                          ['void'])

    def test_exception_when_attribute_no_longer_exists(self):
        child = ProjectNode(self.gamma, ['c1', 'c2'])
        self.assertRaises(AttributeReferenceError, ProjectNode, child,
                          ['c3'])

    def test_exception_when_prefix_is_wrong(self):
        self.assertRaises(InputReferenceError, ProjectNode, self.beta,
                          ['alpha.c2'])

    def test_exception_when_ambiguous_attributes(self):
        self.assertRaises(AttributeReferenceError, ProjectNode, self.ambiguous,
                          'd1')


class TestRename(TestUnaryNode):
    def test_operator_is_correct(self):
        actual = RenameNode(self.alpha, 'other', [], self.schema).operator
        self.assertEqual(Operator.rename, actual)

    def test_name_when_renamed(self):
        actual = RenameNode(self.alpha, 'mask', [], self.schema).name
        self.assertEqual('mask', actual)

    def test_attributes_when_renamed(self):
        expected = ['beta.a', 'beta.b']
        node = RenameNode(self.beta, None, ['a', 'b'], self.schema)
        self.assertEqual(expected, node.attributes.to_list())

    def test_name_when_name_is_not_renamed(self):
        node = RenameNode(self.beta, None, ['a', 'b'], self.schema)
        self.assertEqual('beta', node.name)

    def test_name_when_name_and_attributes_renamed(self):
        node = RenameNode(self.beta, 'mask', ['a', 'b'], self.schema)
        self.assertEqual('mask', node.name)

    def test_attributes_when_name_and_attributes_renamed(self):
        expected = ['mask.a', 'mask.b']
        node = RenameNode(self.beta, 'mask', ['a', 'b'], self.schema)
        self.assertEqual(expected, node.attributes.to_list())

    def test_no_exception_when_renaming_ambiguous_relation(self):
        expected = ['mask.a', 'mask.b']
        node = RenameNode(self.ambiguous, 'mask', ['a', 'b'], self.schema)
        self.assertEqual(expected, node.attributes.to_list())

    def test_exception_when_too_few_attributes(self):
        self.assertRaises(InputError, RenameNode, self.beta,
                          None, ['a'], self.schema)

    def test_exception_when_too_many_attributes(self):
        self.assertRaises(InputError, RenameNode, self.beta,
                          None, ['a', 'b', 'c'], self.schema)

    def test_exception_when_name_conflicts(self):
        self.assertRaises(InputError, RenameNode, self.beta,
                          'alpha', ['a', 'b'], self.schema)

    def test_when_ambiguous_attributes(self):
        self.assertRaises(InputError, RenameNode, self.beta, 'beta',
                          ['b1', 'b1'], self.schema)


class TestAssignment(TestUnaryNode):
    def test_operator_is_correct(self):
        actual = AssignNode(self.alpha, 'omega', [], self.schema).operator
        self.assertEqual(Operator.assign, actual)

    def test_name_when_given(self):
        actual = AssignNode(self.alpha, 'omega', [], self.schema).name
        self.assertEqual('omega', actual)

    def test_attributes_when_renamed(self):
        node = AssignNode(self.beta, 'omega', ['a', 'b'], self.schema)
        expected = ['omega.a', 'omega.b']
        self.assertEqual(expected, node.attributes.to_list())

    def test_ambiguous_attributes_in_child(self):
        node = AssignNode(self.ambiguous, 'omega', ['a', 'b'], self.schema)
        expected = ['omega.a', 'omega.b']
        self.assertEqual(expected, node.attributes.to_list())

    def test_schema_is_updated_after_assign_with_no_explicit_attributes(self):
        AssignNode(self.beta, 'omega', [], self.schema)
        self.assertTrue(self.schema.contains('omega'))
        self.assertEqual(self.schema.get_attributes('beta'),
                         self.schema.get_attributes('omega'))

    def test_schema_is_updated_after_assign_with_attributes(self):
        AssignNode(self.gamma, 'omega', ['a', 'b', 'c'], self.schema)
        self.assertTrue(self.schema.contains('omega'))
        self.assertEqual(['a', 'b', 'c'], self.schema.get_attributes('omega'))

    def test_exception_when_missing_name(self):
        self.assertRaises(InputError, AssignNode, self.alpha,
                          None, ['a'], self.schema)

    def test_exception_when_too_few_attributes(self):
        self.assertRaises(InputError, AssignNode, self.beta,
                          'omega', ['a'], self.schema)

    def test_exception_when_too_many_attributes(self):
        self.assertRaises(InputError, AssignNode, self.beta,
                          'omega', ['a', 'b', 'c'], self.schema)

    def test_when_ambiguous_attributes(self):
        self.assertRaises(InputError, AssignNode, self.beta, 'omega',
                          ['o1', 'o1'], self.schema)

    def test_exception_when_name_conflicts(self):
        self.assertRaises(InputError, RenameNode, self.beta,
                          'alpha', ['a', 'b'], self.schema)
