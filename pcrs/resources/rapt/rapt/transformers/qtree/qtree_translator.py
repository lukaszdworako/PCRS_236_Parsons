from ..base_translator import BaseTranslator
from .operators import latex_operator


class Translator(BaseTranslator):
    """
    A Translator defining the operations for translating a relational algebra
    statement into a latex tree output.
    """

    def relation(self, node):
        """
        Translate a relation node into latex qtree node.
        :param node: a treebrd node
        :return: a qtree subtree rooted at the node
        """
        return '[.${}$ ]'.format(node.name)

    def select(self, node):
        """
        Translate a select node into a latex qtree node.
        :param node: a treebrd node
        :return: a qtree subtree rooted at the node
        """
        child = self.translate(node.child)
        return '[.${op}_{{{conditions}}}$ {child} ]'\
            .format(op=latex_operator[node.operator],
                    conditions=node.conditions, child=child)

    def project(self, node):
        """
        Translate a project node into latex qtree node.
        :param node: a treebrd node
        :return: a qtree subtree rooted at the node
        """
        child = self.translate(node.child)
        return '[.${op}_{{{attributes}}}$ {child} ]'\
            .format(op=latex_operator[node.operator],
                    attributes=', '.join(node.attributes.names),
                    child=child)

    def rename(self, node):
        """
        Translate a rename node into latex qtree node.
        :param node: a treebrd node
        :return: a qtree subtree rooted at the node
        """
        child = self.translate(node.child)
        attributes = ''
        if node.attributes:
            attributes = '({})'.format(', '.join(node.attributes.names))
        return '[.${op}_{{{name}{attributes}}}$ {child} ]'\
            .format(op=latex_operator[node.operator], name=node.name,
                    attributes=attributes,
                    child=child)

    def assign(self, node):
        """
        Translate an assign node into latex qtree node.
        :param node: a treebrd node
        :return: a qtree subtree rooted at the node
        """
        child = self.translate(node.child)
        attributes = ''
        if node.attributes:
            attributes = '({})'.format(','.join(node.attributes.names))
        return '[.${name}{attributes}$ {child} ]'\
            .format(name=node.name, attributes=attributes, child=child)

    def theta_join(self, node):
        """
        Translate a join node into latex qtree node.
        :param node: a treebrd node
        :return: a qtree subtree rooted at the node
        """
        return '[.${op}_{{{conditions}}}$ {left} {right} ]'\
            .format(op=latex_operator[node.operator],
                    conditions=node.conditions,
                    left=self.translate(node.left),
                    right=self.translate(node.right))

    def cross_join(self, node):
        """
        Translate a cross node into latex qtree node.
        :param node: a treebrd node
        :return: a qtree subtree rooted at the node
        """
        return self._binary(node)

    def natural_join(self, node):
        """
        Translate a natural join node into latex qtree node.
        :param node: a treebrd node
        :return: a qtree subtree rooted at the node
        """
        return self._binary(node)

    def union(self, node):
        """
        Translate a union node into latex qtree node.
        :param node: a treebrd node
        :return: a qtree subtree rooted at the node
        """
        return self._binary(node)

    def difference(self, node):
        """
        Translate a difference node into latex qtree node.
        :param node: a treebrd node
        :return: a qtree subtree rooted at the node
        """
        return self._binary(node)

    def intersect(self, node):
        """
        Translate an intersect node into latex qtree node.
        :param node: a treebrd node
        :return: a qtree subtree rooted at the node
        """
        return self._binary(node)

    def _binary(self, node):
        """
        Translate a binary node into latex qtree node.
        :param node: a treebrd node
        :return: a qtree subtree rooted at the node
        """
        return '[.${op}$ {left} {right} ]'\
            .format(op=latex_operator[node.operator],
                    left=self.translate(node.left),
                    right=self.translate(node.right))


def translate(roots):
    """
    Translate a treebrd tree rooted at root into latex tree.
    :param root: a treebrd node
    :return:  a string representing a latex qtree rooted at root
    """
    return ['\\Tree{root}'.format(root=Translator().translate(root))
            for root in roots]