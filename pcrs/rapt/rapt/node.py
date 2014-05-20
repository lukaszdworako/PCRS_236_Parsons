import copy

import rapt.constants as const
from rapt.node_attributes import AttributeList
from rapt.translation_error import RelationReferenceError, InputError, \
    AttributeReferenceError


class Node:
    """
    A Node is a representation of a relational algebra relation. It has a name
    and attributes.

    A Node is an abstract base class that is not intended to be used directly.
    """

    def __init__(self, name):
        self.name = name
        self.attributes = None
        self._conditions = ''

    @property
    def conditions(self):
        return self._conditions

    @conditions.setter
    def conditions(self, value):
        if self.conditions:
            self._conditions += ' AND '

        if value:
            self._conditions += '({})'.format(value)
        else:
            self._conditions = ''

    def to_sql(self, semantics):
        """
        Return a SQL statement that translates the relational algebra relation
        represented by this node.

        Relational algebra has two semantics: Set and Bag.
        """
        attributes = (str(self.attributes) if semantics == const.BAG_SEMANTICS
                      else 'DISTINCT {}'.format(str(self.attributes)))

        query = 'SELECT {attributes} FROM {prior_relation}'.format(
            attributes=attributes,
            prior_relation=self.from_clause(semantics))
        if self.conditions:
            query = '{query} WHERE {conditions}'.format(
                query=query, conditions=self.conditions)
        return query

    def from_clause(self, semantics):
        """
        The FROM clause in a SQL query.
        """
        raise NotImplementedError


class RelationNode(Node):
    """
    A representation of a relational algebra relation.
    """

    def __init__(self, name, schema):
        attributes = schema.get(name, None)
        if not attributes:
            raise RelationReferenceError(
                'Relation \'{name}\' does not exist.'.format(name=name))

        super().__init__(name)
        self.attributes = AttributeList(attributes, name)

    def from_clause(self, semantics=None):
        return '{name}'.format(name=self.name)


class UnaryNode(Node):
    """
    A Unary Node extends Node and has one child, that is of type Node.
    Before querying this node, the child expressions need to be evaluated.
    """

    def __init__(self, name, child):
        super().__init__(name)

        self.child = child
        if not name:
            self.name = self.child.name

        self.attributes = copy.copy(child.attributes)
        self._conditions = child.conditions

    def from_clause(self, semantics):
        return self.child.from_clause(semantics)


class SelectNode(UnaryNode):
    """
    A relation that results from the relation algebra select operator.
    """

    def __init__(self, child, conditions, condition_attributes):
        if not child.attributes.contains(condition_attributes):
            raise AttributeReferenceError(
                'At least one attribute in select is not in the relation.')

        super().__init__(None, child)
        self.conditions = conditions


class ProjectNode(UnaryNode):
    """
    A relation that results from the relation algebra project operator.
    """

    def __init__(self, child, attributes):
        super().__init__(None, child)
        self.attributes.restrict(attributes)


class RenameNode(UnaryNode):
    """
    A relation that results from the relation algebra rename operator.
    """

    def __init__(self, name, child, attributes, schema):
        if name and name in schema:
            raise RelationReferenceError(
                'Relation \'{name}\' already exists.'.format(name=name))

        super().__init__(name, child)
        self.attributes.rename(attributes, name)
        self.conditions = ''

    def from_clause(self, semantics):
        return '({child}) AS {name}({attributes})'.format(
            child=self.child.to_sql(semantics),
            name=self.name,
            attributes=', '.join(self.attributes.names))


class AssignmentNode(UnaryNode):
    """
    A relation that results from the relation algebra assign operator.
    """

    def __init__(self, name, child, attributes, schema):
        if name in schema:
            raise RelationReferenceError(
                'Relation \'{name}\' already exists.'.format(name=name))

        if attributes and len(attributes) != len(child.attributes):
            raise InputError('Assignment requires naming all attributes.')

        super().__init__(name, child)
        self.attributes.rename(attributes, name)
        schema[name] = self.attributes.names

    def to_sql(self, semantics):
        return 'CREATE TEMPORARY TABLE {name}({attributes}) AS ' \
               '{query}'.format(name=self.name,
                                attributes=', '.join(self.attributes.names),
                                query=self.child.to_sql(semantics))


class BinaryNode(Node):
    """
    A Binary Node is a Node with two child Nodes, a left and a right.

    Binary Nodes are uniquely named on instantiation and the name is prefixed
    with an underscore.
    """

    def __init__(self, left, right):
        super().__init__(None)
        self.left = left
        self.right = right
        self.name = self._unique_name()
        self.attributes = None

    def _unique_name(self):
        """
        Return a unique name for this Node, prefixed by an underscore.
        """
        return '_{id}'.format(id=id(self))


class JoinNode(BinaryNode):
    """
    A relation that results from the relation algebra join operator.
    """

    def __init__(self, left, right):
        super().__init__(left, right)
        self.attributes = AttributeList.merge(left.attributes, right.attributes)

    @property
    def operator(self):
        return 'CROSS JOIN'

    def from_clause(self, semantics):
        return '{left} {op} {right}' \
               ''.format(op=self.operator,
                         left=self._format_child_clause(self.left, semantics),
                         right=self._format_child_clause(self.right, semantics))

    @staticmethod
    def _format_child_clause(child, semantics):
        """
        Return a string will be used in the from clause to represent the child.

        The from clause of a child that is also a JoinNode can be joined with
        the from clause of the parent. This allows any future parent nodes to
        access ambiguous attributes by prefixing the name of the relation.
        """
        if isinstance(child, JoinNode):
            return child.from_clause(semantics)
        else:
            return '({query}) AS {name}'.format(query=child.to_sql(semantics),
                                                name=child.name)


class NaturalJoinNode(JoinNode):
    """
    A relation that results from the relation algebra natural join operator.
    """

    def __init__(self, left, right):
        super().__init__(left, right)
        left_attributes = [attribute.prefixed
                           for attribute in self.left.attributes]
        left_names = self.left.attributes.names
        right_attributes = [attribute.prefixed
                            for attribute in self.right.attributes
                            if attribute.name not in left_names]
        self.attributes.restrict(left_attributes + right_attributes)

    @property
    def operator(self):
        return 'NATURAL JOIN'


class ThetaJoinNode(JoinNode):
    """
    A relation that results from the relation algebra theta join operator.
    """

    def __init__(self, left, right, conditions):
        super().__init__(left, right)
        self.conditions = conditions


class SetOperatorNode(BinaryNode):
    """
    An abstract class for binary nodes with set operators.
    """

    def __init__(self, left, right):
        super().__init__(left, right)

        names = left.attributes.names
        if not names == right.attributes.names:
            raise InputError(
                'Set operations require identical relation schemas.')

        self.attributes = AttributeList(names, None)

    @property
    def operator(self):
        raise NotImplementedError('operator method must be implemented.')

    def from_clause(self, semantics):
        return '({query}) AS {name}'.format(query=self.to_sql(semantics),
                                            name=self.name)

    def to_sql(self, semantics):
        use_all = ' ALL' if semantics == const.BAG_SEMANTICS else ''
        return '{left} {op}{use_all} {right}'.format(
            op=self.operator,
            use_all=use_all,
            left=self.left.to_sql(semantics),
            right=self.right.to_sql(semantics))


class UnionNode(SetOperatorNode):
    """
    A relation that results from the relation algebra union operator.
    """

    def __init__(self, left, right):
        super().__init__(left, right)

    @property
    def operator(self):
        return 'UNION'


class DifferenceNode(SetOperatorNode):
    """
    A relation that results from the relation algebra difference operator.
    """

    def __init__(self, left, right):
        super().__init__(left, right)

    @property
    def operator(self):
        return 'EXCEPT'


class IntersectNode(SetOperatorNode):
    """
    A relation that results from the relation algebra intersect operator.
    """

    def __init__(self, left, right):
        super().__init__(left, right)

    @property
    def operator(self):
        return 'INTERSECT'
