from rapt.treebrd.grammars import CoreGrammar, GRAMMARS
from rapt.treebrd.grammars.syntax import Syntax
from .treebrd.treebrd import TreeBRD
from .transformers.sql import sql_translator
from .transformers.qtree import qtree_translator


class Rapt:
    @staticmethod
    def configure_grammar(**config):
        syntax = Syntax(**config.get('syntax', {}))
        grammar_class_name = config.get('grammar', 'Core Grammar')
        # grammar_class = GRAMMARS.get(grammar_class_name, CoreGrammar)
        grammar_class = grammar_class_name
        if type(grammar_class) == str:
            grammar_class = GRAMMARS.get(grammar_class_name, ExtendedGrammar)
        return grammar_class(syntax)

    def __init__(self, **config):
        grammar = self.configure_grammar(**config)
        self.builder = TreeBRD(grammar)

    def to_syntax_tree(self, instring, schema):
        """
        Return a list of syntax trees that represent the instring.

        :param instring: a relational algebra string
        :param schema: a schema for the string
        :return: a list of syntax trees
        """
        return self.builder.build(instring, schema)

    def to_sql(self, instring, schema, use_bag_semantics=False):
        """
        Translate a relational algebra string into a SQL string.

        :param instring: a relational algebra string to translate
        :param schema: a mapping of relation names to their attributes
        :param use_bag_semantics: flag for using relational algebra bag semantics
        :return: a SQL translation string
        """
        root_list = self.to_syntax_tree(instring, schema)
        return sql_translator.translate(root_list, use_bag_semantics)

    def to_sql_sequence(self, instring, schema, use_bag_semantics=False):
        # TODO: docstring
        root_list = self.to_syntax_tree(instring, schema)
        return [
            sql_translator.translate(root.post_order(), use_bag_semantics)
            for root in root_list
        ]

    def to_qtree(self, instring, schema):
        """
        Translate a relational algebra string into a string representing a
        latex tree, using the grammar.
        """
        root_list = self.to_syntax_tree(instring, schema)
        return qtree_translator.translate(root_list)
