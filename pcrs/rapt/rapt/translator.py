import rapt.constants as const
from rapt.grammars.condition_rules import get_attrs
from rapt.node import RelationNode, ProjectNode, SelectNode, RenameNode, \
    AssignmentNode, JoinNode, UnionNode, DifferenceNode, IntersectNode, \
    NaturalJoinNode, ThetaJoinNode
from rapt.utility import flatten


class Translator:
    """
    A relational algebra to SQL translator.

    The translator uses the grammar rules of the provided pyparsing parser to
    translate an instring into a Translation.
    """

    def __init__(self, grammar):
        self.grammar = grammar()

    def translate(self, schema, semantics, instring):
        """
        Return a SQL translation of instring.

        :param semantics:
        :param schema:
        :param instring: A relational algebra string that follows the grammar.
        :return: A Translation object.
        """
        ra = self.grammar.parse(instring).asList()
        parse_tree = self.ra_to_parse_tree(schema, ra)
        sql = self.parse_tree_to_sql(semantics, parse_tree)
        return Translation(instring, ra, sql, parse_tree)

    @staticmethod
    def parse_tree_to_sql(semantics, parse_tree):
        """
        Return a list of SQL statements with the result that when each is run
        in order, it will return the tuples queried by the parse tree.

        A relational algebra query might include an assignment statement which
        would add a table to the namespace.

        :param parse_tree: A parse tree that represents relational algebra
        queries.
        :return: A list of terminated SQL statements.
        """
        sql_list = ['{statement};'.format(statement=node.to_sql(semantics))
                    for node in parse_tree]
        return sql_list

    def ra_to_parse_tree(self, schema, ra):
        """
        Return a list of Nodes, each of which represents the specified
        relational algebra queries.

        :param schema:
        :return: A list of Nodes.
        """
        return [self.ra_to_node(schema, statement) for statement in ra[:]]

    def ra_to_node(self, schema, exp):
        """
        Return a Node that represents the parse structure of the specified
        expression.

        :param schema:
        :param exp: A list that represents a relational algebra expression.
        :return: A Node.
        """
        # A relation node.
        if len(exp) == 1 and isinstance(exp[0], str):
            node = RelationNode(name=exp[0], schema=schema)

        # An expression.
        elif len(exp) == 1 and isinstance(exp[0], list):
            node = self.ra_to_node(schema, exp[0])

        # Unary operators.
        elif isinstance(exp[0], str) and exp[0] in const.UNARY_OP:
            child = self.ra_to_node(schema, exp[2:])
            node = create_unary(operator=exp[0], child=child, param=exp[1],
                                schema=schema)

        # Assignment.
        elif exp[1] is const.ASSIGN_OP:
            child = self.ra_to_node(schema, exp[2:])
            node = create_unary(operator=exp[1], child=child, param=exp[0],
                                schema=schema)

        # Binary operators.
        elif exp[1] in const.BINARY_OP:
            left = self.ra_to_node(schema, exp[:-2])
            right = self.ra_to_node(schema, exp[-1])
            node = create_binary(operator=exp[-2], left=left, right=right)

        elif exp[1] in const.BINARY_OP_PARAMS:
            left = self.ra_to_node(schema, exp[0])
            right = self.ra_to_node(schema, exp[3:])
            node = create_param_binary(operator=exp[1], left=left, right=right,
                                       param=exp[2])

        else:
            print(exp)
            raise Exception

        return node


class Translation:
    """
    A relational algebra to SQL translation.

    The translation stores the original instring, the parsed relational algebra
    structure, the parse tree that was used to make the translation and the SQL
    translation.

    The parse tree is a list of translation nodes, each representing a separate
    statement in the instring.

    The SQL translation is a list of SQL statements. The last statement is a
    select statement that selects every tuple in a SQL view. The remaining
    statements create SQL views for each component expression of the input
    relation algebra string.
    """

    def __init__(self, instring, ra, sql, parse_tree):
        self.instring = instring
        self.ra = ra
        self.sql = sql
        self.parse_tree = parse_tree


def create_unary(operator, child=None, param=None, schema=None):
    """
    Return a Unary Node whose type depends on the specified operator.

    :param operator: A relational algebra operator (see constants.py)
    :param param: A list of parameters for the operator.
    :return: A Unary Node.
    """

    if operator == const.PROJECT_OP:
        attributes = param
        return ProjectNode(child, attributes)

    if operator == const.SELECT_OP:
        conditions = ' '.join(flatten(param))
        attributes = get_attrs(conditions)
        return SelectNode(child, conditions, attributes)

    if operator == const.RENAME_OP:
        name = None
        attributes = []
        if isinstance(param[0], str):
            name = param.pop(0)
        if param:
            attributes = param[0]
        return RenameNode(name, child, attributes, schema)

    if operator == const.ASSIGN_OP:
        name = param[0]
        attributes = [] if len(param) < 2 else param[1]
        return AssignmentNode(name, child, attributes, schema)


def create_binary(operator, left=None, right=None):
    """
    Return a Node whose type depends on the specified operator.

    :param operator: A relational algebra operator (see constants.py)
    :return: A Node.
    """

    # Join
    if operator == const.JOIN_OP:
        return JoinNode(left, right)

    # Natural Join
    if operator == const.NATURAL_JOIN_OP:
        return NaturalJoinNode(left, right)

    # Set operators
    if operator == const.UNION_OP:
        return UnionNode(left, right)

    if operator == const.DIFFERENCE_OP:
        return DifferenceNode(left, right)

    if operator == const.INTERSECT_OP:
        return IntersectNode(left, right)


def create_param_binary(operator, left, right, param):
    if operator == const.THETA_JOIN_OP:
        conditions = ' '.join(flatten(param))
        return ThetaJoinNode(left, right, conditions)