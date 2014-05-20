from pyparsing import *

from rapt.grammars import CoreGrammar
import rapt.constants as const
from rapt.grammars.core_grammar import parametrize


class ExtendedGrammar(CoreGrammar):
    """
    A parser that recognizes an extended relational algebra grammar.

    The rules are annotated with their BNF equivalents. For a complete
    specification refer to the associated grammar file.
    """

    # Grammar Rules

    # natural_join_expr ::= expression natural_join expression

    # theta_join_expr ::= expression join
    #                     param_start conditions param_stop expression

    #
    @property
    def natural_join(self):
        """
        natural_join_expr ::= expression natural_join expression
        """
        return CaselessKeyword(const.NATURAL_JOIN_OP)

    @property
    def theta_join(self):
        """
        select_expr ::= select param_start conditions param_stop expression
        """
        return parametrize(const.JOIN_OP, self.conditions).setParseAction(
            self.theta_parse_action)

    def theta_parse_action(self, s, l, t):
        t[0] = const.THETA_JOIN_OP
        return t

    @property
    def binary_op_p1(self):
        return super().binary_op_p1 ^ self.natural_join ^ self.theta_join

    @property
    def intersect(self):
        """
        intersect_op ::= intersect_name
        """
        return CaselessKeyword(const.INTERSECT_OP)

    @property
    def binary_op_p2(self):
        return super().binary_op_p2 | self.intersect
