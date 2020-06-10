from pyparsing import ParseException

from rapt.treebrd.grammars.extended_grammar import ExtendedGrammar
from tests.treebrd.grammars.grammar_test_case import GrammarTestCase


class TestIntersect(GrammarTestCase):
    def setUp(self):
        self.parser = ExtendedGrammar()
        self.parse = self.parse_function(self.parser.statements)

    def test_simple(self):
        expression = 'zeppelin \\intersect floyd;'
        expected = [
            [['zeppelin'], '\\intersect', ['floyd']]
        ]
        actual = self.parse(expression)
        self.assertEqual(expected, actual)

    def test_multiple(self):
        expression = 'zeppelin \\intersect floyd \\intersect doors;'
        expected = [
            [['zeppelin'], '\\intersect', ['floyd'], '\\intersect', ['doors']]
        ]
        actual = self.parse(expression)
        self.assertEqual(expected, actual)

    def test_intersect_precedence_when_before_set_operator(self):
        expression = 'zeppelin \\intersect floyd \\union doors;'
        expected = [
            [[['zeppelin'], '\\intersect', ['floyd']], '\\union', ['doors']]
        ]
        actual = self.parse(expression)
        self.assertEqual(expected, actual)

    def test_intersect_precedence_when_after_set_operator(self):
        expression = 'zeppelin \\union floyd \\intersect doors;'
        expected = [
            [['zeppelin'], '\\union', [['floyd'], '\\intersect', ['doors']]]
        ]
        actual = self.parse(expression)
        self.assertEqual(expected, actual)

    def test_other_join(self):
        expression = 'zeppelin \\intersect floyd \\join doors;'
        expected = [
            [['zeppelin'], '\\intersect', [['floyd'], '\\join', ['doors']]]
        ]
        actual = self.parse(expression)
        self.assertEqual(expected, actual)

    def test_other_unary(self):
        expression = '\\project_{albums} zeppelin \\intersect ' \
                     '\\project_{albums} floyd;'
        expected = [
            [['\\project', ['albums'], ['zeppelin']], '\\intersect',
             ['\\project', ['albums'], ['floyd']]]
        ]
        actual = self.parse(expression)
        self.assertEqual(expected, actual)

    # Exceptions

    def test_exp_no_relations(self):
        expression = '\\intersect;'
        self.assertRaises(ParseException, self.parse, expression)

    def test_exp_left_relation(self):
        expression = 'roger \\intersect;'
        self.assertRaises(ParseException, self.parse, expression)

    def test_exp_right_relation(self):
        expression = '\\intersect waters;'
        self.assertRaises(ParseException, self.parse, expression)


class TestNaturalJoin(GrammarTestCase):
    def setUp(self):
        self.parser = ExtendedGrammar()
        self.parse = self.parse_function(self.parser.statements)

    def test_simple(self):
        expression = 'zeppelin \\natural_join floyd;'
        expected = [
            [['zeppelin'], '\\natural_join', ['floyd']]
        ]
        actual = self.parse(expression)
        self.assertEqual(expected, actual)

    def test_multiple(self):
        expression = 'zeppelin \\natural_join floyd \\natural_join doors;'
        expected = [
            [['zeppelin'], '\\natural_join', ['floyd'], '\\natural_join',
             ['doors']]
        ]
        actual = self.parse(expression)
        self.assertEqual(expected, actual)

    def test_same_precedence(self):
        expression = 'zeppelin \\natural_join floyd \\join doors;'
        expected = [
            [['zeppelin'], '\\natural_join', ['floyd'], '\\join', ['doors']]
        ]
        actual = self.parse(expression)
        self.assertEqual(expected, actual)

    def test_other_precedence(self):
        expression = 'zeppelin \\union floyd \\natural_join doors;'
        expected = [
            [['zeppelin'], '\\union', [['floyd'], '\\natural_join', ['doors']]]
        ]
        actual = self.parse(expression)
        self.assertEqual(expected, actual)

    def test_other_unary(self):
        expression = '\\project_{albums} zeppelin \\natural_join ' \
                     '\\project_{albums} floyd;'
        expected = [
            [['\\project', ['albums'], ['zeppelin']], '\\natural_join',
             ['\\project', ['albums'], ['floyd']]]
        ]
        actual = self.parse(expression)
        self.assertEqual(expected, actual)

    # Exceptions

    def test_exp_no_relations(self):
        expression = '\\natural_join;'
        self.assertRaises(ParseException, self.parse, expression)

    def test_exp_left_relation(self):
        expression = 'roger \\natural_join;'
        self.assertRaises(ParseException, self.parse, expression)

    def test_exp_right_relation(self):
        expression = '\\natural_join waters;'
        self.assertRaises(ParseException, self.parse, expression)


class TestThetaJoin(GrammarTestCase):
    def setUp(self):
        self.parser = ExtendedGrammar()
        self.parse = self.parse_function(self.parser.statements)

    def test_simple(self):
        expression = 'zeppelin \\join_{year < 1975} floyd;'
        expected = [
            [['zeppelin'], '\\theta_join', ['year', '<', '1975'], ['floyd']]]
        actual = self.parse(expression)
        self.assertEqual(expected, actual)

    def test_multiple(self):
        expression = 'zeppelin \\join_{year < 1975} floyd ' \
                     '\\join_{year < 1960} doors;'
        expected = [
            [['zeppelin'], '\\theta_join', ['year', '<', '1975'], ['floyd'],
             '\\theta_join', ['year', '<', '1960'], ['doors']]
        ]
        actual = self.parse(expression)
        self.assertEqual(expected, actual)

    def test_same_precedence(self):
        expression = 'zeppelin \\join_{year < 1975} floyd ' \
                     '\\join doors;'
        expected = [
            [['zeppelin'], '\\theta_join', ['year', '<', '1975'], ['floyd'],
             '\\join', ['doors']]
        ]
        actual = self.parse(expression)
        self.assertEqual(expected, actual)

    def test_other_precedence(self):
        expression = 'zeppelin \\union floyd \\join_{year < 1975} doors;'
        expected = [
            [['zeppelin'], '\\union', [['floyd'], '\\theta_join',
                                       ['year', '<', '1975'], ['doors']]]
        ]
        actual = self.parse(expression)
        self.assertEqual(expected, actual)

    def test_other_unary(self):
        expression = '\\project_{albums} zeppelin \\join_{year < 1975} ' \
                     '\\project_{albums} floyd;'
        expected = [
            [['\\project', ['albums'], ['zeppelin']], '\\theta_join',
             ['year', '<', '1975'], ['\\project', ['albums'], ['floyd']]]
        ]
        actual = self.parse(expression)
        self.assertEqual(expected, actual)

    # Exceptions

    def test_exp_basic(self):
        expression = '\\join_;'
        self.assertRaises(ParseException, self.parse, expression)

    def test_exp_no_relation_right(self):
        expression = 'zeppelin \\join_{age < 42};'
        self.assertRaises(ParseException, self.parse, expression)

    def test_exp_no_relation_left(self):
        expression = '\\join_{age < 42} floyd;'
        self.assertRaises(ParseException, self.parse, expression)

    def test_exp_empty_attribute_list(self):
        expression = 'zeppelin \\join_{} floyd;'
        self.assertRaises(ParseException, self.parse, expression)

    def test_exp_space_before_attributes(self):
        expression = 'zeppelin \\join _{age < 42} floyd;'
        self.assertRaises(ParseException, self.parse, expression)