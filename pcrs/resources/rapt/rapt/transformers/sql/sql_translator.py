from ...treebrd.node import Operator
from ..base_translator import BaseTranslator


class SQLQuery:
    """
    Structure defining the building blocks of a SQL query.
    """
    def __init__(self, select_block, from_block, where_block=''):
        self.prefix = ''
        self.select_block = select_block
        self.from_block = from_block
        self.where_block = where_block

    @property
    def _basic_query(self):
        if self.select_block:
            return '{prefix}' \
                   'SELECT {select} FROM {relation}'
        else:
            return '{prefix}{relation}'

    @property
    def _sql_query_skeleton(self):
        sql = self._basic_query
        if self.where_block:
            sql += ' WHERE {conditions}'
        return sql

    def to_sql(self):
        """
        Construct a SQL query based on the stored blocks.
        :return: a SQL query
        """
        return self._sql_query_skeleton.format(
            prefix=self.prefix, select=self.select_block,
            relation=self.from_block, conditions=self.where_block)


class SQLSetQuery(SQLQuery):
    """
    Structure defining the building blocks of a SQL query with set semantics.
    """

    @property
    def _basic_query(self):
        return '{prefix}' \
               'SELECT DISTINCT {select} FROM {relation}'


class Translator(BaseTranslator):
    """
    A Translator defining the operations for translating a relational algebra
    statement into a SQL statement using bag semantics.
    """
    query = SQLQuery

    @classmethod
    def _get_temp_name(cls, node):
        return node.name or '_{}'.format(id(node))

    @classmethod
    def _get_sql_operator(cls, node):
        operators = {
            Operator.union: 'UNION',
            Operator.difference: 'EXCEPT',
            Operator.intersect: 'INTERSECT',
            Operator.cross_join: 'CROSS JOIN',
            Operator.theta_join: 'CROSS JOIN',
            Operator.natural_join: 'NATURAL JOIN',
        }
        return operators[node.operator]

    def relation(self, node):
        """
        Translate a relation node into SQLQuery.
        :param node: a treebrd node
        :return: a SQLQuery object for the tree rooted at node
        """
        return self.query(select_block=str(node.attributes),
                          from_block=node.name)

    def select(self, node):
        """
        Translate a select node into SQLQuery.
        :param node: a treebrd node
        :return: a SQLQuery object for the tree rooted at node
        """

        child_object = self.translate(node.child)
        where_block = node.conditions
        if child_object.where_block:
              where_block = '({0}) AND ({1})'\
                  .format(child_object.where_block, node.conditions)
        child_object.where_block = where_block
        if not child_object.select_block:
            child_object.select_block = str(node.attributes)
        return child_object

    def project(self, node):
        """
        Translate a project node into SQLQuery.
        :param node: a treebrd node
        :return: a SQLQuery object for the tree rooted at node
        """
        child_object = self.translate(node.child)
        child_object.select_block = str(node.attributes)
        return child_object

    def rename(self, node):
        """
        Translate a rename node into SQLQuery.
        :param node: a treebrd node
        :return: a SQLQuery object for the tree rooted at node
        """
        child_object = self.translate(node.child)
        from_block = '({child}) AS {name}({attributes})'.format(
            child=child_object.to_sql(), name=node.name,
            attributes=', '.join(node.attributes.names))
        return self.query(str(node.attributes), from_block=from_block)

    def assign(self, node):
        """
        Translate an assign node into SQLQuery.
        :param node: a treebrd node
        :return: a SQLQuery object for the tree rooted at node
        """
        child_object = self.translate(node.child)
        child_object.prefix = 'CREATE TEMPORARY TABLE {name}({attributes}) AS '\
            .format(name=node.name, attributes=', '.join(node.attributes.names))
        return child_object

    def natural_join(self, node):
        """
        Translate an assign node into SQLQuery.
        :param node: a treebrd node
        :return: a SQLQuery object for the tree rooted at node
        """
        return self._join(node)

    def theta_join(self, node):
        """
        Translate an assign node into SQLQuery.
        :param node: a treebrd node
        :return: a SQLQuery object for the tree rooted at node
        """
        return self._join(node)

    def cross_join(self, node):
        """
        Translate a cross join node into SQLQuery.
        :param node: a treebrd node
        :return: a SQLQuery object for the tree rooted at node
        """
        return self._join(node)

    def union(self, node):
        """
        Translate a union node into SQLQuery.
        :param node: a treebrd node
        :return: a SQLQuery object for the tree rooted at node
        """
        return self._set_op(node)

    def intersect(self, node):
        """
        Translate an intersection node into SQLQuery.
        :param node: a treebrd node
        :return: a SQLQuery object for the tree rooted at node
        """
        return self._set_op(node)

    def difference(self, node):
        """
        Translate an difference node into SQLQuery.
        :param node: a treebrd node
        :return: a SQLQuery object for the tree rooted at node
        """
        return self._set_op(node)

    def _join_helper(self, node):
            sobject = self.translate(node)
            if node.operator in {Operator.cross_join, Operator.natural_join}:
                return sobject.from_block
            else:
                return '({subquery}) AS {name}'.format(
                    subquery=sobject.to_sql(), name=self._get_temp_name(node))

    def _join(self, node):
        """
        Translate a join node into SQLQuery.
        :param node: a treebrd node
        :return: a SQLQuery object for the tree rooted at node
        """

        select_block = str(node.attributes)
        from_block = '{left} {operator} {right}'.format(
            left=self._join_helper(node.left),
            right=self._join_helper(node.right),
            operator=self._get_sql_operator(node))
        where_block = node.conditions if hasattr(node, 'conditions') else ''
        return self.query(select_block, from_block, where_block)

    def _set_op(self, node):
        """
        Translate a set operator node into SQLQuery.
        :param node: a treebrd node
        :return: a SQLQuery object for the tree rooted at node
        """
        select_block = str(node.attributes)
        from_block = '({left} {operator} ALL {right}) AS {name}'.format(
            left=self.translate(node.left).to_sql(),
            right=self.translate(node.right).to_sql(),
            operator=self._get_sql_operator(node), name=self._get_temp_name(node))
        return self.query(select_block=select_block, from_block=from_block)


class SetTranslator(Translator):
    """
    A Translator defining the operations for translating a relational algebra
    statement into a SQL statement using set semantics.
    """
    query = SQLSetQuery

    def _set_op(self, node):
        """
        Translate a set operator node into SQLQuery, using set semantics.
        :param node: a treebrd node
        :return: a SQLSetQuery object for the tree rooted at node
        """
        select_block = str(node.attributes)
        from_block = '({left} {operator} {right}) AS {name}'.format(
            left=self.translate(node.left).to_sql(),
            right=self.translate(node.right).to_sql(),
            operator=self._get_sql_operator(node), name=self._get_temp_name(node))
        return self.query(select_block=select_block, from_block=from_block)


def translate(root_list, use_bag_semantics=False):
    """
    Translate a list of relational algebra trees into SQL statements.

    :param root_list: a list of tree roots
    :param use_bag_semantics: flag for using relational algebra bag semantics
    :return: a list of SQL statements
    """
    translator = (Translator() if use_bag_semantics else SetTranslator())
    return [translator.translate(root).to_sql() for root in root_list]