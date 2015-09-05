from unittest import TestCase
from rapt.treebrd.attributes import Attribute, AttributeList

__author__ = 'Noel'


class TestAttribute(TestCase):
    def test_name_after_init(self):
        attribute = Attribute('Name', 'Prefix')
        self.assertEqual('Name', attribute.name)

    def test_prefix_after_init(self):
        attribute = Attribute('Name', 'Prefix')
        self.assertEqual('Prefix', attribute.prefix)

    def test_prefixed_after_init(self):
        attribute = Attribute('Name', 'Prefix')
        self.assertEqual('Prefix.Name', attribute.prefixed)

    def test_equality_when_name_and_attribute_are_equal(self):
        attribute_a = Attribute('Name', 'Prefix')
        attribute_b = Attribute('Name', 'Prefix')
        self.assertEqual(attribute_a, attribute_b)

    def test_equality_when_name_and_attribute_are_different(self):
        attribute_a = Attribute('Name', 'Prefix')
        attribute_b = Attribute('Other', 'Other')
        self.assertNotEquals(attribute_a, attribute_b)

    def test_equality_when_name_is_different(self):
        attribute_a = Attribute('Name', 'Prefix')
        attribute_b = Attribute('Other', 'Prefix')
        self.assertNotEqual(attribute_a, attribute_b)

    def test_equality_when_attribute_is_different(self):
        attribute_a = Attribute('Name', 'Prefix')
        attribute_b = Attribute('Name', 'Other')
        self.assertNotEqual(attribute_a, attribute_b)

    def test_hash_when_name_and_attribute_are_equal(self):
        attribute_a = Attribute('Name', 'Prefix')
        attribute_b = Attribute('Name', 'Prefix')
        self.assertEqual(hash(attribute_a), hash(attribute_b))


class TestAttributeList(TestCase):
    def test_trim_when_restriction_is_empty(self):
        a_list = AttributeList(['A', 'B', 'C'], 'prefix')
        a_list.trim([])
        self.assertEqual([], a_list.to_list())

    def test_trim_when_restriction_contains_all_with_no_prefix(self):
        expected = ['prefix.A', 'prefix.B', 'prefix.C']
        a_list = AttributeList(['A', 'B', 'C'], 'prefix')
        a_list.trim(['A', 'B', 'C'])
        self.assertEqual(expected, a_list.to_list())

    def test_trim_when_restriction_contains_all_with_prefix(self):
        expected = ['prefix.A', 'prefix.B', 'prefix.C']
        a_list = AttributeList(['A', 'B', 'C'], 'prefix')
        a_list.trim(['prefix.A', 'prefix.B', 'prefix.C'])
        self.assertEqual(expected, a_list.to_list())

    def test_trim_when_restriction_excludes_first(self):
        expected = ['prefix.B', 'prefix.C']
        a_list = AttributeList(['A', 'B', 'C'], 'prefix')
        a_list.trim(['B', 'C'])
        self.assertEqual(expected, a_list.to_list())

    def test_trim_when_restriction_excludes_last(self):
        expected = ['prefix.A', 'prefix.B']
        a_list = AttributeList(['A', 'B', 'C'], 'prefix')
        a_list.trim(['A', 'B'])
        self.assertEqual(expected, a_list.to_list())

    def test_trim_when_restriction_excludes_middle(self):
        expected = ['prefix.A', 'prefix.C']
        a_list = AttributeList(['A', 'B', 'C'], 'prefix')
        a_list.trim(['A', 'C'])
        self.assertEqual(expected, a_list.to_list())

    def test_trim_when_restriction_leaves_first(self):
        expected = ['prefix.A']
        a_list = AttributeList(['A', 'B', 'C'], 'prefix')
        a_list.trim(['A'])
        self.assertEqual(expected, a_list.to_list())

    def test_trim_when_restriction_leaves_last(self):
        expected = ['prefix.C']
        a_list = AttributeList(['A', 'B', 'C'], 'prefix')
        a_list.trim(['C'])
        self.assertEqual(expected, a_list.to_list())

    def test_trim_when_restriction_leaves_middle(self):
        expected = ['prefix.B']
        a_list = AttributeList(['A', 'B', 'C'], 'prefix')
        a_list.trim(['B'])
        self.assertEqual(expected, a_list.to_list())

    def test_trim_when_reorder(self):
        expected = ['prefix.B', 'prefix.C', 'prefix.A']
        a_list = AttributeList(['B', 'C', 'A'], 'prefix')
        a_list.trim(['B', 'C', 'A'])
        self.assertEqual(expected, a_list.to_list())

    def test_trim_when_reorder_and_restrict(self):
        expected = ['prefix.C', 'prefix.A']
        a_list = AttributeList(['B', 'C', 'A'], 'prefix')
        a_list.trim(['C', 'A'])
        self.assertEqual(expected, a_list.to_list())

    def test_rename_prefix(self):
        expected = ['prefix.A', 'prefix.B', 'prefix.C']
        a_list = AttributeList(['A', 'B', 'C'], 'old')
        a_list.rename([], 'prefix')
        self.assertEqual(expected, a_list.to_list())

    def test_rename_attribute_names(self):
        expected = ['prefix.A', 'prefix.B', 'prefix.C']
        a_list = AttributeList(['a', 'b', 'c'], 'prefix')
        a_list.rename(['A', 'B', 'C'], None)
        self.assertEqual(expected, a_list.to_list())

    def test_rename_attribute_name_and_prefix(self):
        expected = ['prefix.A', 'prefix.B', 'prefix.C']
        a_list = AttributeList(['a', 'b', 'c'], 'old')
        a_list.rename(['A', 'B', 'C'], 'prefix')
        self.assertEqual(expected, a_list.to_list())
