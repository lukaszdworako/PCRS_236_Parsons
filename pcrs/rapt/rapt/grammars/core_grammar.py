from pyparsing import *

from rapt.grammars.condition_rules import ConditionRules
import rapt.constants as const


def parameter(parser):
    """
    Return a parser the parses parameters.
    """
    return (Suppress(const.PARAMS_START).leaveWhitespace() +
            Group(parser) + Suppress(const.PARAMS_STOP))


def parametrize(operator, params):
    """
    Return a parser that parses an operator with parameters.
    """
    return CaselessKeyword(operator, identChars=alphanums) + parameter(params)


def parenthesize(parser):
    return (Suppress(const.PAREN_LEFT) + Group(parser) +
            Suppress(const.PAREN_RIGHT))


class CoreGrammar(ConditionRules):
    """
    A parser that recognizes a core relational algebra grammar.

    The rules are annotated with their BNF equivalents. For a complete
    specification refer to the associated grammar file.
    """

    def parse(self, instring):
        return self.statements.parseString(instring, parseAll=True)

    @property
    def attribute_list(self):
        """
        attribute_list ::= attribute_name | attribute_list delim attribute_name
        """
        return delimitedList(self.attribute_name, delim=const.DELIM)

    @property
    def attribute_reference_list(self):
        """
        attribute_reference_list ::= attribute_reference |
                                 attribute_list delim attribute_reference
        """
        return delimitedList(self.attribute_reference,
                             delim=const.DELIM)

    @property
    def relation(self):
        """
        relation_expr ::= relation_name
        """
        return Group(self.relation_name)

    ### Unary Expressions ###

    @property
    def project(self):
        """
        project_expr ::= project param_start attribute_list param_stop
            expression
        """
        return parametrize(const.PROJECT_OP, self.attribute_reference_list)

    @property
    def select(self):
        """
        select_expr ::= select param_start conditions param_stop expression
        """
        return parametrize(const.SELECT_OP, self.conditions)

    @property
    def rename(self):
        """
        rename_expr ::= rename param_start rename_parameters param_stop
            expression

        rename_parameters ::= relation_name |
            paren_left attribute_list paren_right |
            relation_name paren_left attribute_list paren_right
        """
        params = self.relation_name ^ (Optional(self.relation_name) +
                                       parenthesize(self.attribute_list))
        return parametrize(const.RENAME_OP, params)

    @property
    def unary_op(self):
        """
        rename_expr ::= rename param_start rename_parameters param_stop
            expression
        """
        return self.project | self.select | self.rename

    # Binary Operators (Precedence 1)
    #

    @property
    def join(self):
        """
        join_expr ::= expression join expression
        """
        return CaselessKeyword(const.JOIN_OP)

    @property
    def binary_op_p1(self):
        """
        Binary operators with precedence of one.
        """
        return self.join

    # Binary Operators (Precedence 2)

    @property
    def union(self):
        """
        union_expr ::= expression union expression
        """
        return CaselessKeyword(const.UNION_OP)

    @property
    def difference(self):
        """
        difference_expr ::= expression difference expression
        """
        return CaselessKeyword(const.DIFFERENCE_OP)

    @property
    def binary_op_p2(self):
        """
        Binary operators with precedence of two.
        """
        return self.union | self.difference

    @property
    def expression(self):
        """
        A relation algebra expression. An expression is either a relation or a
        combination of relations that uses the previously defined operators
        and follows precedence rules.
        """
        return operatorPrecedence(self.relation, [
            (self.unary_op, 1, opAssoc.RIGHT),
            (self.binary_op_p1, 2, opAssoc.LEFT),
            (self.binary_op_p2, 2, opAssoc.LEFT)])

    @property
    def assignment(self):
        """
        assignment ::= relation_name assign expression |
            relation_name param_start attribute_list param_stop
            assign expression
        """
        lhs = Group(self.relation_name +
                    Optional(parenthesize(self.attribute_list)))
        return Group(lhs + Keyword(const.ASSIGN_OP) + self.expression)

    @property
    def statement(self):
        """
        A terminated relational algebra statement.
        """
        return (self.assignment ^ self.expression) + Suppress(const.TERMINATOR)

    @property
    def statements(self):
        """
        An ordered collection of relational algebra statements.
        """
        return OneOrMore(self.statement)