import unittest

from pyparsing import ParseException

from rapt.treebrd.grammars.core_grammar import CoreGrammar


class TestAssignment(unittest.TestCase):
    def setUp(self):
        self.parser = CoreGrammar()

    def test_assign_relation(self):
        expression = 'asts := astronauts;'
        expected = [[['asts'], ':=', ['astronauts']]]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)

    def test_assign_expression(self):
        expression = 'ast := \\project_{name} astronauts;'
        expected = [[['ast'], ':=', ['\\project', ['name'], ['astronauts']]]]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)

    def test_multiple_assign_expressions(self):
        expression = 'names := \\project_{name} astronauts;' \
                     'species := \\project_{species} astronauts;'
        expected = [
            [['names'], ':=', ['\\project', ['name'], ['astronauts']]],
            [['species'], ':=', ['\\project', ['species'], ['astronauts']]]
        ]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)

    def test_assign_attributes(self):
        expression = 'ast(age, happiness) := astronauts;'
        expected = [[['ast', ['age', 'happiness']], ':=', ['astronauts']]]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)

    def test_assign_attributes_spacing(self):
        expression = 'ast ( age , happiness ) := astronauts;'
        expected = [[['ast', ['age', 'happiness']], ':=', ['astronauts']]]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)

    # Exceptions

    def test_no_expressions(self):
        expression = ':=;'
        self.assertRaises(ParseException, self.parser.statements.parseString,
                          expression, CoreGrammar)

    def test_exp_no_right(self):
        expression = 'A := ;'
        self.assertRaises(ParseException, self.parser.statements.parseString,
                          expression, CoreGrammar)

    def test_no_left(self):
        expression = ':= A;'
        self.assertRaises(ParseException, self.parser.statements.parseString,
                          expression, CoreGrammar)

    def test_no_attributes(self):
        expression = 'ast() := A;'
        self.assertRaises(ParseException, self.parser.statements.parseString,
                          expression, CoreGrammar)
