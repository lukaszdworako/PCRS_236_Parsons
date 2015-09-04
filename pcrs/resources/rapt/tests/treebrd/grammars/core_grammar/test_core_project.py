import unittest

from pyparsing import ParseException

from rapt.treebrd.grammars.core_grammar import CoreGrammar


class TestProject(unittest.TestCase):
    def setUp(self):
        self.parser = CoreGrammar()

    def test_single_attribute(self):
        expression = '\project_{species} astronauts;'
        expected = [['\\project', ['species'], ['astronauts']]]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)

    def test_two_attributes(self):
        expression = '\project_{name, age} astronauts;'
        expected = [['\\project', ['name', 'age'], ['astronauts']]]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)

    def test_multiple_attributes(self):
        expression = '\project_{name, age, colour, sex, alive} astronauts;'
        expected = [['\\project', ['name', 'age', 'colour', 'sex', 'alive'],
                     ['astronauts']]]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)

    def test_recursive(self):
        expression = '\project_{species} \project_{age, species} astronauts;'
        expected = [['\\project', ['species'],
                     ['\\project', ['age', 'species'], ['astronauts']]]]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)

    def test_recursive_double(self):
        expression = '\project_{species} \project_{age} \project_{name} ' \
                     'astronauts;'
        expected = [['\\project', ['species'],
                     ['\\project', ['age'],
                      ['\\project', ['name'], ['astronauts']]]]]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)

    # Exceptions

    def test_exp_basic(self):
        expression = '\project;'
        self.assertRaises(ParseException, self.parser.statements.parseString,
                          expression, CoreGrammar)

    def test_exp_no_relation(self):
        expression = '\project_{species};'
        self.assertRaises(ParseException, self.parser.statements.parseString,
                          expression, CoreGrammar)

    def test_exp_no_attributes(self):
        expression = '\project astronauts;'
        self.assertRaises(ParseException, self.parser.statements.parseString,
                          expression, CoreGrammar)

    def test_exp_empty_attribute_list(self):
        expression = '\project_{} astronauts;'
        self.assertRaises(ParseException, self.parser.statements.parseString,
                          expression, CoreGrammar)

    def test_exp_space_before_attributes(self):
        expression = '\project _{species} astronauts;'
        self.assertRaises(ParseException, self.parser.statements.parseString,
                          expression, CoreGrammar)

    def test_exp_attribute_not_delim(self):
        expression = '\project _{species age} astronauts;'
        self.assertRaises(ParseException, self.parser.statements.parseString,
                          expression, CoreGrammar)
