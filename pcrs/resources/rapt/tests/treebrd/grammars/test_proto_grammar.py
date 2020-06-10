from pyparsing import ParseException, alphas, nums

from rapt.treebrd.grammars.proto_grammar import ProtoGrammar
from tests.treebrd.grammars.grammar_test_case import GrammarTestCase


class TestProtoGrammar(GrammarTestCase):
    def setUp(self):
        self.parser = ProtoGrammar()

    def test_character(self):
        expected = set(alphas + nums + '_')
        actual = set(self.parser.character)

        self.assertEqual(expected, actual)

    def test_number_integers(self):
        parse = self.parse_function(self.parser.number)

        self.assertEqual(parse('792'), ['792'])
        self.assertEqual(parse('0'), ['0'])
        self.assertEqual(parse('-42'), ['-42'])

    def test_number_floats(self):
        parse = self.parse_function(self.parser.number)

        self.assertEqual(parse('7.42'), ['7.42'])
        self.assertEqual(parse('0.0'), ['0.0'])
        self.assertEqual(parse('.576'), ['.576'])
        self.assertEqual(parse('-42.7'), ['-42.7'])
        self.assertEqual(parse('-1042.789'), ['-1042.789'])

    def test_number_exp(self):
        parse = self.parse_function(self.parser.number)

        self.assertRaises(ParseException, parse, "_")
        self.assertRaises(ParseException, parse, "a")
        self.assertRaises(ParseException, parse, "--7")
        self.assertRaises(ParseException, parse, "++7")

    def test_number_floats_exp(self):
        parse = self.parse_function(self.parser.number)

        self.assertRaises(ParseException, parse, "7.a")
        self.assertRaises(ParseException, parse, "7,1")
        self.assertRaises(ParseException, parse, "3.7.4")
        self.assertRaises(ParseException, parse, ".")

    def test_identifier(self):
        parse = self.parse_function(self.parser.identifier)

        self.assertEqual(parse('y'), ['y'])
        self.assertEqual(parse('Q'), ['q'])
        self.assertEqual(parse('why'), ['why'])
        self.assertEqual(parse('why_not'), ['why_not'])
        self.assertEqual(parse('Life_Is_42'), ['life_is_42'])

    def test_identifier_exp(self):
        parse = self.parse_function(self.parser.identifier)

        self.assertRaises(ParseException, parse, "7_is_perfect")
        self.assertRaises(ParseException, parse, "_is_perfect")
        self.assertRaises(ParseException, parse, "1")
        self.assertRaises(ParseException, parse, "0")

    def test_literal(self):
        parse = self.parse_function(self.parser.string_literal)
        self.assertEqual(parse("'Single!'"), ["'Single!'"])
        self.assertEqual(parse('"Two is one."'), ['\'Two is one.\''])
        self.assertEqual(parse("''"), ["''"])

    def test_literal_exp(self):
        parse = self.parse_function(self.parser.string_literal)

        self.assertRaises(ParseException, parse, "Do not quote me!")
        self.assertRaises(ParseException, parse, "Don't quote me!")
        self.assertRaises(ParseException, parse, "\"Mismatch'")