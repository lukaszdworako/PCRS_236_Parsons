import unittest

from pyparsing import ParseException

from rapt.treebrd.grammars.core_grammar import CoreGrammar


class TestSelect(unittest.TestCase):
    def setUp(self):
        self.parser = CoreGrammar()

    def test_single_condition(self):
        expression = '\\select_{age < 42} astronauts;'
        expected = [['\\select', ['age', '<', '42'], ['astronauts']]]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)

    def test_single_condition_reversed(self):
        expression = '\\select_{42 < age} astronauts;'
        expected = [['\\select', ['42', '<', 'age'], ['astronauts']]]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)

    def test_single_condition_spacing(self):
        expression = '\\select_{age<42} astronauts;'
        expected = [['\\select', ['age', '<', '42'], ['astronauts']]]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)

    def test_single_condition_literal(self):
        expression = "\\select_{name = 'Douglas'} astronauts;"
        expected = [['\\select', ['name', '=', "'Douglas'"], ['astronauts']]]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)

    def test_condition_not(self):
        expression = '\\select_{not(age < 42)} astronauts;'
        expected = [['\\select', [['not', '(', 'age', '<', '42', ')']],
                     ['astronauts']]]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)

    def test_two_conditions_and(self):
        expression = '\\select_{age < 42 and flights > 1} astronauts;'
        expected = [
            ['\\select', [['age', '<', '42', 'and', 'flights', '>', '1']],
             ['astronauts']]]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)

    def test_two_conditions_or(self):
        expression = '\\select_{age < 42 or name = 5} astronauts;'
        expected = [['\\select', [['age', '<', '42', 'or', 'name', '=', '5']],
                     ['astronauts']]]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)

    # Exceptions

    def test_exp_basic(self):
        expression = '\\select;'
        self.assertRaises(ParseException, self.parser.statements.parseString,
                          expression, CoreGrammar)

    def test_exp_no_relation(self):
        expression = '\\select_{age < 42};'
        self.assertRaises(ParseException, self.parser.statements.parseString,
                          expression, CoreGrammar)

    def test_exp_no_attributes(self):
        expression = '\\select astronauts;'
        self.assertRaises(ParseException, self.parser.statements.parseString,
                          expression, CoreGrammar)

    def test_exp_empty_attribute_list(self):
        expression = '\\select_{} astronauts;'
        self.assertRaises(ParseException, self.parser.statements.parseString,
                          expression, CoreGrammar)

    def test_exp_space_before_attributes(self):
        expression = '\\select _{age < 42} astronauts;'
        self.assertRaises(ParseException, self.parser.statements.parseString,
                          expression, CoreGrammar)