import unittest

from pyparsing import ParseException

from rapt.treebrd.grammars.core_grammar import CoreGrammar


class TestUnion(unittest.TestCase):
    def setUp(self):
        self.parser = CoreGrammar()

    def test_binary_precedence_low_high(self):
        expression = 'astronauts \\union sputnik1_crew ' \
                     '\\join sputnik2_crew;'
        expected = [
            [['astronauts'], '\\union', [['sputnik1_crew'], '\\join',
                                         ['sputnik2_crew']]]
        ]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)

    def test_binary_precedence_high_low(self):
        expression = 'astronauts \\join sputnik1_crew ' \
                     '\\union sputnik2_crew;'
        expected = [
            [[['astronauts'], '\\join', ['sputnik1_crew']], '\\union',
             ['sputnik2_crew']]
        ]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)

    def test_binary_precedence_high_low_bracketed(self):
        expression = 'astronauts \\join (sputnik1_crew ' \
                     '\\union sputnik2_crew);'
        expected = [
            [['astronauts'], '\\join', [['sputnik1_crew'], '\\union',
                                        ['sputnik2_crew']]]
        ]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)

    def test_binary_same_precedence(self):
        expression = 'astronauts \\union s1_crew \\difference s2_crew;'
        expected = [
            [['astronauts'], '\\union', ['s1_crew'], '\\difference',
             ['s2_crew']]
        ]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)

    # Exceptions

    def test_exp_basic(self):
        expression = '\\union;'
        self.assertRaises(ParseException, self.parser.statements.parseString,
                          expression, CoreGrammar)

    def test_exp_no_relation(self):
        expression = '\\union_{species};'
        self.assertRaises(ParseException, self.parser.statements.parseString,
                          expression, CoreGrammar)

    def test_exp_no_attributes(self):
        expression = '\\union astronauts;'
        self.assertRaises(ParseException, self.parser.statements.parseString,
                          expression, CoreGrammar)

    def test_exp_empty_attribute_list(self):
        expression = 'astronauts \\union;'
        self.assertRaises(ParseException, self.parser.statements.parseString,
                          expression, CoreGrammar)
