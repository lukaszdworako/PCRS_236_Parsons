from ..treebrd.node import Operator


class BaseTranslator:
    """
    A Translator defining the operations for translating a relational algebra
    statement into some output format.
    """
    def __init__(self):
        self._translate_functions = {
            Operator.relation: self.relation,
            Operator.select: self.select,
            Operator.project: self.project,
            Operator.rename: self.rename,
            Operator.assign: self.assign,
            Operator.cross_join: self.cross_join,
            Operator.natural_join: self.natural_join,
            Operator.theta_join: self.theta_join,
            Operator.union: self.union,
            Operator.difference: self.difference,
            Operator.intersect: self.intersect
        }

    def translate(self, node):
        """
        Translate a node into some output format.
        :param node: a treebrd node
        :return: a node's translation to some format
        """
        _translate = self._translate_functions.get(node.operator)
        return _translate(node)


def translate(roots):
    """
    Translate a list of relational algebra trees into some output format.
    :param roots: a list of tree roots
    :return:  a list of translations
    """
    raise NotImplementedError('Must be implemented by translation modules.')