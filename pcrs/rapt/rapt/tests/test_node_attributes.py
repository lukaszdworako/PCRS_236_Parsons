from unittest import TestCase
from rapt.node_attributes import AttributeList, Attribute


class TestAttribute(TestCase):
    def test_construction(self):
        attribute = Attribute('Potato_Head', 'Mr')
        self.assertEqual('Potato_Head', attribute.name)
        self.assertEqual('Mr', attribute.prefix)

    def test_prefixed_with(self):
        attribute = Attribute('Potato_Head', 'Mr')
        self.assertEqual('Mr.Potato_Head', attribute.prefixed)

    def test_prefixed_without(self):
        attribute = Attribute('Potato_Head', None)
        self.assertEqual('Potato_Head', attribute.prefixed)


class TestAttributeList(TestCase):
    def test_construction(self):
        names = ['Woody', 'Lightyear', 'Dog']
        attr_list = AttributeList(names, 'Mr')
        expected = [Attribute(name, 'Mr') for name in names]
        self.assertEqual(expected, attr_list.contents)
        self.assertEqual(names, attr_list.names)


class TestAttributeListOld(TestCase):
    def test_to_list_no_prefix(self):
        attr_list = ['a', 'b', 'c']
        node_attr = AttributeList(attr_list, None)
        expected = attr_list
        self.assertEqual(expected, node_attr.to_list())

    def test_to_list_with_prefixes(self):
        attr_list = ['a', 'b', 'c']
        node_attr = AttributeList(attr_list, 'prefix')
        expected = ['prefix.{}'.format(attr) for attr in attr_list]
        self.assertEqual(expected, node_attr.to_list())

    def test_to_str_no_prefix(self):
        attr_list = ['a', 'b', 'c']
        node_attr = AttributeList(attr_list, None)
        expected = ', '.join(attr_list)
        self.assertEqual(expected, str(node_attr))

    def test_to_str_with_prefixes(self):
        attr_list = ['a', 'b', 'c']
        node_attr = AttributeList(attr_list, 'prefix')
        expected = ', '.join(['prefix.{}'.format(attr) for attr in attr_list])
        self.assertEqual(expected, str(node_attr))

    def test_extend_no_prefix(self):
        init_list = ['a', 'b', 'c']
        ext_list = ['d', 'e', 'f']
        node_attr = AttributeList(init_list, 'first')
        node_attr.extend(ext_list, None)
        expected = ['first.{}'.format(attr) for attr in init_list]
        expected += ['{}'.format(attr) for attr in ext_list]
        self.assertEqual(expected, node_attr.to_list())

    def test_extend_prefix(self):
        init_list = ['a', 'b', 'c']
        ext_list = ['d', 'e', 'f']
        node_attr = AttributeList(init_list, 'first')
        node_attr.extend(ext_list, 'second')
        expected = ['first.{}'.format(attr) for attr in init_list]
        expected += ['second.{}'.format(attr) for attr in ext_list]
        actual = node_attr.to_list()
        self.assertEqual(expected, actual)

    def test_contains_no_prefix(self):
        node_attr = AttributeList(['a', 'b', 'c'], None)
        sub_list = ['a', 'b']
        self.assertTrue(node_attr.contains(sub_list))

    def test_properly_contains_no_prefix(self):
        node_attr = AttributeList(['a', 'b', 'c'], None)
        sub_list = ['a', 'b', 'c']
        self.assertTrue(node_attr.contains(sub_list))

    def test_not_contains_no_prefix(self):
        node_attr = AttributeList(['a', 'b', 'c'], None)
        sub_list = ['a', 'b', 'd']
        self.assertFalse(node_attr.contains(sub_list))

    def test_contains_prefix_on_node_attributes(self):
        node_attr = AttributeList(['a', 'b', 'c'], 'prefix')
        sub_list = ['a', 'b']
        self.assertTrue(node_attr.contains(sub_list))

    def test_contains_prefix_both(self):
        node_attr = AttributeList(['a', 'b', 'c'], 'prefix')
        sub_list = ['prefix.a', 'b']
        self.assertTrue(node_attr.contains(sub_list))

    def test_contains_prefix_on_some_node_attributes(self):
        node_attr = AttributeList(['a', 'b', 'c'], 'first')
        node_attr.extend(['d', 'e'], None)
        sub_list = ['first.a', 'b', 'e']
        self.assertTrue(node_attr.contains(sub_list))

    def test_get_item(self):
        node_attr = AttributeList(['a', 'b', 'c'], 'first')
        expected = Attribute('b', 'first')
        actual = node_attr['b']
        self.assertEqual(expected, actual)

    def test_get_item_prefixed(self):
        node_attr = AttributeList(['a', 'b', 'c'], 'first')
        expected = Attribute('b', 'first')
        actual = node_attr['first.b']
        self.assertEqual(expected, actual)

    def test_merge(self):
        first = AttributeList(['a', 'b', 'c'], 'first')
        second = AttributeList(['a', 'b', 'c'], 'second')
        merged = AttributeList.merge(first, second)
        expected = ['first.a', 'first.b', 'first.c', 'second.a', 'second.b',
                    'second.c', ]
        self.assertEqual(expected, merged.to_list())

    def test_get_item_exception(self):
        node_attr = AttributeList(['a', 'b', 'c'], 'first')
        self.assertRaises(KeyError, node_attr.__getitem__, 'd')

    def test_get_item_correct_prefix_exception(self):
        node_attr = AttributeList(['a', 'b', 'c'], 'first')
        self.assertRaises(KeyError, node_attr.__getitem__, 'first.d')

    def test_get_item_incorrect_prefix_exception(self):
        node_attr = AttributeList(['a', 'b', 'c'], 'first')
        self.assertRaises(KeyError, node_attr.__getitem__, 'second.a')