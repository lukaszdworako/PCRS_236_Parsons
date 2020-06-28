import unittest
from pyparsing import ParseException
from rapt.treebrd.grammars.condition_grammar import ConditionGrammar, get_attrs
from tests.treebrd.grammars.grammar_test_case import GrammarTestCase


class TestConditionRules(GrammarTestCase):
    def setUp(self):
        self.parser = ConditionGrammar()

    def test_comparator(self):
        parse = self.parse_function(self.parser.comparator_op)

        self.assertEqual(parse('='), ['='])
        self.assertEqual(parse('!='), ['!='])
        self.assertEqual(parse('<>'), ['<>'])
        self.assertEqual(parse('<'), ['<'])
        self.assertEqual(parse('<='), ['<='])
        self.assertEqual(parse('>'), ['>'])
        self.assertEqual(parse('>='), ['>='])

    def test_comparator_exp(self):
        parse = self.parse_function(self.parser.comparator_op)

        self.assertRaises(ParseException, parse, "==")
        self.assertRaises(ParseException, parse, "><")
        self.assertRaises(ParseException, parse, "=<")
        self.assertRaises(ParseException, parse, "=>")

    def test_logical_unary(self):
        parse = self.parse_function(self.parser.not_op)

        self.assertEqual(parse('not'), ['not'])
        self.assertEqual(parse('NOT'), ['not'])

    def test_logical_binary(self):
        parse = self.parse_function(self.parser.logical_binary_op)

        self.assertEqual(parse('and'), ['and'])
        self.assertEqual(parse('AND'), ['and'])
        self.assertEqual(parse('or'), ['or'])
        self.assertEqual(parse('OR'), ['or'])

    def test_operand(self):
        parse = self.parse_function(self.parser.operand)

        self.assertEqual(parse('"Secret to life"'), ["'Secret to life'"])
        self.assertEqual(parse('is__'), ['is__'])
        self.assertEqual(parse('1.3337'), ['1.3337'])

    def test_operand_exp(self):
        parse = self.parse_function(self.parser.operand)

        self.assertRaises(ParseException, parse, "=")
        self.assertRaises(ParseException, parse, "Need space!")

    def test_condition(self):
        parse = self.parse_function(self.parser.condition)

        self.assertEqual(parse('2 > 7'), ['2', '>', '7'])
        self.assertEqual(parse('secret = 3'), ['secret', '=', '3'])
        self.assertEqual(parse('"name" != "mane"'), ["'name'", '!=', "'mane'"])

    def test_condition_exp_fragments(self):
        parse = self.parse_function(self.parser.condition)

        self.assertRaises(ParseException, parse, "'Happiness' =")
        self.assertRaises(ParseException, parse, "< you")
        self.assertRaises(ParseException, parse, "<>")

    # Testing a single condition

    def test_conditions_single(self):
        parse = self.parse_function(self.parser.conditions)
        expected = ['2', '>', '7']
        actual = parse('2 > 7')
        self.assertEqual(actual, expected)

    def test_conditions_par(self):
        parse = self.parse_function(self.parser.conditions)
        expected = ['(', '2', '>', '7', ')']
        actual = parse('(2 > 7)')
        self.assertEqual(actual, expected)

    def test_conditions_not(self):
        parse = self.parse_function(self.parser.conditions)
        expected = [['not', '(', '2', '>', '7', ')']]
        actual = parse('not (2 > 7)')
        self.assertEqual(actual, expected)

    def test_conditions_and(self):
        parse = self.parse_function(self.parser.conditions)
        expected = [['2', '>', '7', 'and', '3', '<>', '3']]
        actual = parse('2 > 7 and 3 <> 3')
        self.assertEqual(actual, expected)

    def test_conditions_and_par(self):
        parse = self.parse_function(self.parser.conditions)
        expected = [['(', '2', '>', '7', ')', 'and', '(', '3', '<>', '3', ')']]
        actual = parse('(2 > 7) and (3 <> 3)')
        self.assertEqual(actual, expected)

    def test_conditions_or(self):
        parse = self.parse_function(self.parser.conditions)
        expected = [['(', '2', '>', '7', ')', 'or', '(', '3', '<>', '3', ')']]
        actual = parse('(2 > 7) or (3 <> 3)')
        self.assertEqual(actual, expected)

    def test_conditions_unary_binary_simple(self):
        parse = self.parse_function(self.parser.conditions)
        expected = [[['not', '2', '>', '7'], 'and', '3', '<>', '3']]
        actual = parse('not 2 > 7 and 3 <> 3')
        self.assertEqual(actual, expected)

    def test_conditions_unary_binary_simple_forced(self):
        parse = self.parse_function(self.parser.conditions)
        expected = [['not', '(', ['2', '>', '7', 'and', '3', '<>', '3'], ')']]
        actual = parse('not (2 > 7 and 3 <> 3)')
        self.assertEqual(actual, expected)

    def test_conditions_binary_unary_simple(self):
        parse = self.parse_function(self.parser.conditions)
        expected = [['3', '<>', '3', 'or', ['not', '2', '>', '7']]]
        actual = parse('3 <> 3 or not 2 > 7')
        self.assertEqual(expected, actual)


class TestConditionAttrs(unittest.TestCase):

    def test_conditions_binary_unary(self):
        expected = ['answer']
        self.assertEqual(expected, get_attrs('answer=42'))

    def test_conditions_binary_unary_with_prefix(self):
        expected = ['a.answer']
        self.assertEqual(expected, get_attrs('a.answer=42'))

    def test_conditions_binary_unary_reversed(self):
        expected = ['answer']
        self.assertEqual(expected, get_attrs('42=answer'))

    def test_conditions_binary_unary_no_attr(self):
        self.assertEqual([], get_attrs('42=42'))

    def test_conditions_binary_unary_two_attrs(self):
        expected = ['answer', 'known']
        self.assertEqual(expected, get_attrs('answer=known'))

    def test_conditions_binary_two_attrs(self):
        expected = ['answer', 'known']
        self.assertEqual(expected, get_attrs('answer=known and 42=42'))

    def test_conditions_binary_man_attrs(self):
        expected = ['answer', 'known', 'answer', 'unknown']
        self.assertEqual(expected, get_attrs('answer=known and answer=unknown'))