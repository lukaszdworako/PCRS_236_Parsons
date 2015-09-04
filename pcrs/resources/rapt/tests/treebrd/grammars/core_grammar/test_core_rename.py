import unittest

from pyparsing import ParseException

from rapt.treebrd.grammars.core_grammar import CoreGrammar


class TestProject(unittest.TestCase):
    def setUp(self):
        self.parser = CoreGrammar()

    def test_rename_relation(self):
        expression = '\\rename_{species} astronauts;'
        expected = [['\\rename', ['species'], ['astronauts']]]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)

    def test_rename_attribute(self):
        expression = '\\rename_{ (name)} astronauts;'
        expected = [['\\rename', [['name']], ['astronauts']]]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)

    def test_rename_multiple_attributes(self):
        expression = '\\rename_{(name, age, alive)} astronauts;'
        expected = [['\\rename', [['name', 'age', 'alive']],
                     ['astronauts']]]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)

    def test_rename_relation_and_multiple_attributes(self):
        expression = '\\rename_{nautical (name, age, alive)} astronauts;'
        expected = [['\\rename', ['nautical', ['name', 'age', 'alive']],
                     ['astronauts']]]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)

    # Exceptions

    def test_exp_basic(self):
        expression = '\\rename;'
        self.assertRaises(ParseException, self.parser.statements.parseString,
                          expression)

    def test_exp_no_relation(self):
        expression = '\\rename_{species};'
        self.assertRaises(ParseException, self.parser.statements.parseString,
                          expression)

    def test_exp_no_attributes(self):
        expression = '\\rename astronauts;'
        self.assertRaises(ParseException, self.parser.statements.parseString,
                          expression)

    def test_exp_empty_attribute_list(self):
        expression = '\\rename_{} astronauts;'
        self.assertRaises(ParseException, self.parser.statements.parseString,
                          expression)

    def test_exp_space_before_attributes(self):
        expression = '\\rename _{species} astronauts;'
        self.assertRaises(ParseException, self.parser.statements.parseString,
                          expression)

    def test_exp_attribute_not_delim(self):
        expression = '\\rename _{species age} astronauts;'
        self.assertRaises(ParseException, self.parser.statements.parseString,
                          expression)
