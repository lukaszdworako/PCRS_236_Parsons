from unittest import TestCase

from problems_rdb.db_wrapper import StudentWrapper, PostgresWrapper


class TestProcessNoOrder(TestCase):
    
    def test_empty_list(self):
        l1, l2 = [], []
        self.assertTrue(StudentWrapper.process(l1, l2, order_matters=False))
        self.assertEqual(l1, [])
        self.assertEqual(l2, [])

    def test_same_dicts(self):
        l1 = [{'a': 1}]
        l2 = [{'a': 1}]
        self.assertTrue(StudentWrapper.process(l1, l2, order_matters=False))
        self.assertEqual(l1, [{'a': 1, 'missing': False}])
        self.assertEqual(l2, [{'a': 1, 'extra': False}])

    def test_one_extra(self):
        exp = []
        act = [{'a': 1}]
        self.assertFalse(StudentWrapper.process(exp, act, order_matters=False))
        self.assertEqual(exp, [])
        self.assertEqual(act, [{'a': 1, 'extra': True}])

    def test_same_extra(self):
        exp = [{'a': 1}]
        act = [{'a': 1}, {'a': 1}, {'a': 1}]
        self.assertFalse(StudentWrapper.process(exp, act, order_matters=False))
        self.assertEqual(exp, [{'a': 1, 'missing': False}])
        self.assertEqual(act, [{'a': 1, 'extra': False},
                               {'a': 1, 'extra': True},
                               {'a': 1, 'extra': True}])

    def test_one_missing(self):
        exp = [{'a': 1}]
        act = []
        self.assertFalse(StudentWrapper.process(exp, act, order_matters=False))
        self.assertEqual(exp, [{'a': 1, 'missing': True}])
        self.assertEqual(act, [])

    def test_same_missing(self):
        exp = [{'a': 1}, {'a': 1}, {'a': 1}]
        act = [{'a': 1}]
        self.assertFalse(StudentWrapper.process(exp, act, order_matters=False))
        self.assertEqual(exp, [{'a': 1, 'missing': False},
                               {'a': 1, 'missing': True},
                               {'a': 1, 'missing': True}])
        self.assertEqual(act, [{'a': 1, 'extra': False}])

    def test_multiple_missing(self):
        exp = [{'a': 1}, {'b': 2}]
        act = []
        self.assertFalse(StudentWrapper.process(exp, act, False))
        self.assertEqual(exp, [{'a': 1, 'missing': True},
                               {'b': 2, 'missing': True}])
        self.assertEqual(act, [])

    def test_multiple_extra(self):
        exp = []
        act = [{'a': 1}, {'b': 2}]
        self.assertFalse(StudentWrapper.process(exp, act, False))
        self.assertEqual(exp, [])
        self.assertEqual(act, [{'a': 1, 'extra': True},
                               {'b': 2, 'extra': True}])

    def test_all_different(self):
        exp = [{'a': 1}, {'b': 2}]
        act = [{'c': 1}, {'d': 2}]
        self.assertFalse(StudentWrapper.process(exp, act, order_matters=False))
        self.assertEqual(exp, [{'a': 1, 'missing': True},
                               {'b': 2, 'missing': True}])
        self.assertEqual(act, [{'c': 1, 'extra': True},
                               {'d': 2, 'extra': True}])

    def test_all_same(self):
        exp = [{'a': 1}, {'b': 2}, {'c': 3}]
        act = [{'a': 1}, {'b': 2}, {'c': 3}]
        self.assertTrue(StudentWrapper.process(exp, act, order_matters=False))
        self.assertEqual(exp, [{'a': 1, 'missing': False},
                               {'b': 2, 'missing': False},
                               {'c': 3, 'missing': False}])
        self.assertEqual(act, [{'a': 1, 'extra': False},
                               {'b': 2, 'extra': False},
                               {'c': 3, 'extra': False}])

    def test_all_same_different_order(self):
        exp = [{'c': 3}, {'a': 1}, {'b': 2}, ]
        act = [{'b': 2}, {'a': 1}, {'c': 3}]
        self.assertTrue(StudentWrapper.process(exp, act, order_matters=False))
        self.assertEqual(exp, [{'c': 3, 'missing': False},
                               {'a': 1, 'missing': False},
                               {'b': 2, 'missing': False}])
        self.assertEqual(act, [{'b': 2, 'extra': False},
                               {'a': 1, 'extra': False},
                               {'c': 3, 'extra': False}])

    def test_multiple_same_multiple_different_ordered(self):
        exp = [{'a': 1}, {'b': 2}, {'c': 3}, {'d': 4}, {'e': 5}]
        act = [{'a': 1}, {'b': 2}, {'c': 3}, {'f': 6}, {'g': 7}]
        self.assertFalse(StudentWrapper.process(exp, act, order_matters=False))
        self.assertEqual(exp, [{'a': 1, 'missing': False},
                               {'b': 2, 'missing': False},
                               {'c': 3, 'missing': False},
                               {'d': 4, 'missing': True},
                               {'e': 5, 'missing': True}])
        self.assertEqual(act, [{'a': 1, 'extra': False},
                               {'b': 2, 'extra': False},
                               {'c': 3, 'extra': False},
                               {'f': 6, 'extra': True},
                               {'g': 7, 'extra': True}])

    def test_multiple_same_multiple_different_mixed(self):
        exp = [{'a': 1}, {'b': 2}, {'d': 4}, {'e': 5}, {'c': 3}]
        act = [{'a': 1}, {'f': 6}, {'b': 2}, {'c': 3}, {'g': 7}]
        self.assertFalse(StudentWrapper.process(exp, act, order_matters=False))
        self.assertEqual(exp, [{'a': 1, 'missing': False},
                               {'b': 2, 'missing': False},
                               {'d': 4, 'missing': True},
                               {'e': 5, 'missing': True},
                               {'c': 3, 'missing': False}])
        self.assertEqual(act, [{'a': 1, 'extra': False},
                               {'f': 6, 'extra': True},
                               {'b': 2, 'extra': False},
                               {'c': 3, 'extra': False},
                               {'g': 7, 'extra': True}])


        

class TestProcessWithOrder(TestCase):
    
    def test_empty_list(self):
        l1, l2 = [], []
        self.assertTrue(StudentWrapper.process(l1, l2, order_matters=True))
        self.assertEqual(l1, [])
        self.assertEqual(l2, [])

    def test_same_dicts(self):
        l1 = [{'a': 1}]
        l2 = [{'a': 1}]
        self.assertTrue(StudentWrapper.process(l1, l2, order_matters=True))
        self.assertEqual(l1, [{'a': 1, 'missing': False}])
        self.assertEqual(l2, [{'a': 1, 'extra': False, 'out_of_order': False}])

    def test_one_extra(self):
        exp = []
        act = [{'a': 1}]
        self.assertFalse(StudentWrapper.process(exp, act, order_matters=True))
        self.assertEqual(exp, [])
        self.assertEqual(act, [{'a': 1, 'extra': True}])

    def test_same_extra(self):
        exp = [{'a': 1}]
        act = [{'a': 1}, {'a': 1}, {'a': 1}]
        self.assertFalse(StudentWrapper.process(exp, act, order_matters=True))
        self.assertEqual(exp, [{'a': 1, 'missing': False}])
        self.assertEqual(act, [{'a': 1, 'extra': False},
                               {'a': 1, 'extra': True},
                               {'a': 1, 'extra': True}])

    def test_one_missing(self):
        exp = [{'a': 1}]
        act = []
        self.assertFalse(StudentWrapper.process(exp, act, order_matters=True))
        self.assertEqual(exp, [{'a': 1, 'missing': True}])
        self.assertEqual(act, [])

    def test_same_missing(self):
        exp = [{'a': 1}, {'a': 1}, {'a': 1}]
        act = [{'a': 1}]
        self.assertFalse(StudentWrapper.process(exp, act, order_matters=True))
        self.assertEqual(exp, [{'a': 1, 'missing': False},
                               {'a': 1, 'missing': True},
                               {'a': 1, 'missing': True}])
        self.assertEqual(act, [{'a': 1, 'extra': False}])

    def test_multiple_missing(self):
        exp = [{'a': 1}, {'b': 2}]
        act = []
        self.assertFalse(StudentWrapper.process(exp, act, False))
        self.assertEqual(exp, [{'a': 1, 'missing': True},
                               {'b': 2, 'missing': True}])
        self.assertEqual(act, [])

    def test_multiple_extra(self):
        exp = []
        act = [{'a': 1}, {'b': 2}]
        self.assertFalse(StudentWrapper.process(exp, act, False))
        self.assertEqual(exp, [])
        self.assertEqual(act, [{'a': 1, 'extra': True},
                               {'b': 2, 'extra': True}])

    def test_all_different(self):
        exp = [{'a': 1}, {'b': 2}]
        act = [{'c': 1}, {'d': 2}]
        self.assertFalse(StudentWrapper.process(exp, act, order_matters=True))
        self.assertEqual(exp, [{'a': 1, 'missing': True},
                               {'b': 2, 'missing': True}])
        self.assertEqual(act, [{'c': 1, 'extra': True},
                               {'d': 2, 'extra': True}])

    def test_all_same(self):
        exp = [{'a': 1}, {'b': 2}, {'c': 3}]
        act = [{'a': 1}, {'b': 2}, {'c': 3}]
        self.assertTrue(StudentWrapper.process(exp, act, order_matters=True))
        self.assertEqual(exp, [{'a': 1, 'missing': False},
                               {'b': 2, 'missing': False},
                               {'c': 3, 'missing': False}])
        self.assertEqual(act, [{'a': 1, 'extra': False, 'out_of_order': False},
                               {'b': 2, 'extra': False, 'out_of_order': False},
                               {'c': 3, 'extra': False, 'out_of_order': False}])

    def test_all_same_different_order(self):
        exp = [{'c': 3}, {'a': 1}, {'b': 2}, ]
        act = [{'b': 2}, {'a': 1}, {'c': 3}]
        self.assertFalse(StudentWrapper.process(exp, act, order_matters=True))
        self.assertEqual(exp, [{'c': 3, 'missing': False},
                               {'a': 1, 'missing': False},
                               {'b': 2, 'missing': False}])
        self.assertEqual(act, [{'b': 2, 'extra': False, 'out_of_order': True},
                               {'a': 1, 'extra': False, 'out_of_order': False},
                               {'c': 3, 'extra': False, 'out_of_order': True}])

    def test_multiple_same_multiple_different_mixed(self):
        # self.fail('order?')
        exp = [{'a': 1}, {'b': 2}, {'d': 4}, {'e': 5}, {'c': 3}]
        act = [{'a': 1}, {'f': 6}, {'b': 2}, {'c': 3}, {'g': 7}]
        self.assertFalse(StudentWrapper.process(exp, act, order_matters=True))
        self.assertEqual(exp, [{'a': 1, 'missing': False},
                               {'b': 2, 'missing': False},
                               {'d': 4, 'missing': True},
                               {'e': 5, 'missing': True},
                               {'c': 3, 'missing': False}])
        self.assertEqual(act, [{'a': 1, 'extra': False, 'out_of_order': False},
                               {'f': 6, 'extra': True},
                               {'b': 2, 'extra': False, 'out_of_order': True},
                               {'c': 3, 'extra': False, 'out_of_order': True},
                               {'g': 7, 'extra': True}])


class TestHTMLRepr(TestCase):
    def test_table(self):
        info = {
            'tables': {'A': ['a1'], 'B': ['b1', 'b2']},
        }
        expected = {'', '<b>A</b>(a1)', '<b>B</b>(b1, b2)'}
        actual = set(PostgresWrapper.html_representation(info).split('<br>'))
        self.assertEqual(expected, actual)

    def test_table_with_one_key(self):
        info = {
            'tables': {'A': ['a1'], 'B': ['b1', 'b2']},
            'pkeys': {'A': ['a1']}
        }
        expected = {'<b>A</b>(<u>a1</u>)', '<b>B</b>(b1, b2)'}
        actual = set(PostgresWrapper.html_representation(info).split('<br>'))
        self.assertEqual(expected, actual - {''})

    def test_table_with_many_keys(self):
        info = {
            'tables': {'A': ['a1'], 'B': ['b1', 'b2', 'b3']},
            'pkeys': {'B': ['b1', 'b3']}
        }
        expected = {'<b>A</b>(a1)', '<b>B</b>(<u>b1</u>, b2, <u>b3</u>)'}
        actual = set(PostgresWrapper.html_representation(info).split('<br>'))
        self.assertEqual(expected, actual - {''})

    def test_table_with_foreign_key(self):
        info = {
            'tables': {'A': ['a1'], 'B': ['b1', 'b2', 'b3']},
            'pkeys': {'B': ['b1', 'b3']},
            'fkeys': [(('A', 'a1'), ('B', 'b1'))]
        }
        expected = {'<b>A</b>(a1)', '<b>B</b>(<u>b1</u>, b2, <u>b3</u>)',
                    'A[a1] &sub; B[b1]'}
        actual = set(PostgresWrapper.html_representation(info).split('<br>'))
        self.assertEqual(expected, actual - {''})

    def test_table_with_foreign_keys(self):
        info = {
            'tables': {'A': ['a1'], 'B': ['b1', 'b2', 'b3']},
            'pkeys': {'B': ['b1', 'b3']},
            'fkeys': [(('A', 'a1'), ('B', 'b1')), (('B', 'b3'), ('A', 'a1'))]
        }
        expected = {'<b>A</b>(a1)', '<b>B</b>(<u>b1</u>, b2, <u>b3</u>)',
                    'A[a1] &sub; B[b1]', 'B[b3] &sub; A[a1]'}


        actual = set(PostgresWrapper.html_representation(info).split('<br>'))
        self.assertEqual(expected, actual - {''})