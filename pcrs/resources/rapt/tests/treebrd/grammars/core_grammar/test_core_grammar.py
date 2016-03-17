from pyparsing import ParseException

from rapt.treebrd.grammars.core_grammar import CoreGrammar
from tests.treebrd.grammars.grammar_test_case import GrammarTestCase


class TestCoreGrammar(GrammarTestCase):
    def setUp(self):
        self.parser = CoreGrammar()

    def test_attribute_id(self):
        parse = self.parse_function(self.parser.attribute_reference)

        self.assertEqual(parse('attribute'), ['attribute'])
        self.assertEqual(parse('relation.attribute'), ['relation.attribute'])

    def test_attribute_id_exp(self):
        parse = self.parse_function(self.parser.attribute_reference)

        self.assertRaises(ParseException, parse, "relation.")
        self.assertRaises(ParseException, parse, ".attribute")
        self.assertRaises(ParseException, parse, "relation.attribute.attribute")
        self.assertRaises(ParseException, parse, ".")