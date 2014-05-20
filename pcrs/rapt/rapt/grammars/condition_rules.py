from pyparsing import oneOf, CaselessKeyword, operatorPrecedence, opAssoc

from rapt import constants as const
from rapt.grammars.proto_grammar import ProtoGrammar


def get_attrs(instring):
    parsed = ConditionRules().conditions.parseString(instring)
    result = parsed if isinstance(parsed[0], str) else parsed[0]
    return result.attrs.asList() if result.attrs else []


class ConditionRules(ProtoGrammar):
    """
    A mixin that provides grammar rules for condition expressions.

    The rules are annotated with their BNF equivalents. For a complete
    specification refer to the associated grammar file.
    """

    @property
    def comparator_op(self):
        """
        comparator_op ::= "<" | "<=" | "=" | ">" | ">=" | "!=" | "<>"
        """
        return oneOf([const.EQUAL_OP,
                      const.NOT_EQUAL_OP, const.NOT_EQUAL_ALT_OP,
                      const.LESS_THAN_OP, const.LESS_THAN_EQUAL_OP,
                      const.GREATER_THAN_OP, const.GREATER_THAN_EQUAL_OP])

    @property
    def not_op(self):
        """
        not_op ::= "not" | "NOT"
        """
        return CaselessKeyword(const.NOT_OP)

    @property
    def logical_binary_op(self):
        """
        logical_binary_op ::=  "and" | "or" | "AND" | "OR"
        """
        return CaselessKeyword(const.AND_OP) | CaselessKeyword(const.OR_OP)

    @property
    def operand(self):
        """
        operand ::= identifier | string_literal | number
        """
        return (self.attribute_reference('attrs*') |
                self.string_literal |
                self.number)

    @property
    def condition(self):
        """
        condition ::= operand comparator_op operand | not_op condition |
                  paren_left condition paren_right
        not_op and grouping rules are defined using operatorPrecedence in
        conditions.
        """
        return self.operand + self.comparator_op + self.operand

    @property
    def conditions(self):
        """
        conditions ::= condition | condition logical_binary_op conditions
        Note: By default lpar and rpar arguments are suppressed.
        """
        return operatorPrecedence(
            baseExpr=self.condition,
            opList=[(self.not_op, 1, opAssoc.RIGHT),
                    (self.logical_binary_op, 2, opAssoc.LEFT)],
            lpar=const.PAREN_LEFT,
            rpar=const.PAREN_RIGHT)