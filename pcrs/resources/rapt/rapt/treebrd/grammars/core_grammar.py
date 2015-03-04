from pyparsing import *

from .condition_grammar import ConditionGrammar


class CoreGrammar(ConditionGrammar):
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
        return delimitedList(self.attribute_name, delim=self.syntax.delim)

    @property
    def attribute_reference_list(self):
        """
        attribute_reference_list ::= attribute_reference |
                                 attribute_list delim attribute_reference
        """
        return delimitedList(self.attribute_reference,
                             delim=self.syntax.delim)

    @property
    def relation(self):
        """
        relation_expr ::= relation_name
        """
        return Group(self.relation_name)

    # ## Unary Expressions ###

    @property
    def project(self):
        """
        project_expr ::= project param_start attribute_list param_stop
            expression
        """
        return self.parametrize(self.syntax.project_op,
                                self.attribute_reference_list)

    @property
    def select(self):
        """
        select_expr ::= select param_start conditions param_stop expression
        """
        return self.parametrize(self.syntax.select_op, self.conditions)

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
                                       self.parenthesize(self.attribute_list))
        return self.parametrize(self.syntax.rename_op, params)

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
        return CaselessKeyword(self.syntax.join_op)

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
        return CaselessKeyword(self.syntax.union_op)

    @property
    def difference(self):
        """
        difference_expr ::= expression difference expression
        """
        return CaselessKeyword(self.syntax.difference_op)

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
                    Optional(self.parenthesize(self.attribute_list)))
        return Group(lhs + Keyword(self.syntax.assign_op) + self.expression)

    @property
    def statement(self):
        """
        A terminated relational algebra statement.
        """
        return (self.assignment ^ self.expression) + Suppress(
            self.syntax.terminator)

    @property
    def statements(self):
        """
        An ordered collection of relational algebra statements.
        """
        return OneOrMore(self.statement)

    def parenthesize(self, parser):
        return (Suppress(self.syntax.paren_left) + Group(parser) +
                Suppress(self.syntax.paren_right))

    def parameter(self, parser):
        """
        Return a parser the parses parameters.
        """
        return (Suppress(self.syntax.params_start).leaveWhitespace() +
                Group(parser) + Suppress(self.syntax.params_stop))

    def parametrize(self, operator, params):
        """
        Return a parser that parses an operator with parameters.
        """
        return (CaselessKeyword(operator, identChars=alphanums) +
                self.parameter(params))

    def is_unary(self, operator):
        return operator in {self.syntax.select_op,
                            self.syntax.project_op,
                            self.syntax.rename_op}

    def is_binary(self, operator):
        return operator in {self.syntax.difference_op,
                            self.syntax.union_op,
                            self.syntax.join_op}