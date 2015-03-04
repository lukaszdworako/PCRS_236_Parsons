import unittest

from rapt.treebrd.grammars.core_grammar import CoreGrammar


class TestJoin(unittest.TestCase):
    def setUp(self):
        self.parser = CoreGrammar()

    def test_single(self):
        expression = 'astronauts \\join sputnik1_crew;'
        expected = [
            [['astronauts'], '\\join', ['sputnik1_crew']]
        ]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)

    def test_double(self):
        expression = 'astronauts \\join sputnik1_crew \\join sputnik2_crew;'
        expected = [
            [['astronauts'], '\\join', ['sputnik1_crew'], '\\join',
             ['sputnik2_crew']]
        ]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)

    def test_triple(self):
        expression = 'astronauts \\join sputnik1_crew ' \
                     '\\join sputnik2_crew \\join sputnik3_crew;'
        expected = [
            [['astronauts'], '\\join', ['sputnik1_crew'],
             '\\join', ['sputnik2_crew'], '\\join', ['sputnik3_crew']]
        ]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)

    def test_precedence_left(self):
        expression = 'astronauts \\join sputnik1_crew ' \
                     '\\union sputnik2_crew \\union sputnik3_crew;'
        expected = [
            [[['astronauts'], '\\join', ['sputnik1_crew']], '\\union',
             ['sputnik2_crew'], '\\union', ['sputnik3_crew']]
        ]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)

    def test_precedence_right(self):
        expression = 'astronauts \\union sputnik1_crew ' '\\union ' \
                     'sputnik2_crew \\join sputnik3_crew;'
        expected = [
            [['astronauts'], '\\union', ['sputnik1_crew'], '\\union',
             [['sputnik2_crew'], '\\join', ['sputnik3_crew']]]
        ]
        actual = self.parser.statements.parseString(expression).asList()
        self.assertEqual(expected, actual)


