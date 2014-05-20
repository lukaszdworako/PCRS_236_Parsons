from collections import namedtuple

from rapt.translation_error import InputError, AttributeReferenceError


class Attribute(namedtuple('Attribute', ['name', 'prefix'])):
    """
    An Attribute is a relational algebra attribute. Attributes have optional
    prefixes which reference the relation they belong to.
    """

    @property
    def prefixed(self):
        if self.prefix:
            return '{pr}.{nm}'.format(pr=self.prefix, nm=self.name)
        else:
            return self.name


class AttributeList:
    """
    A AttributeList is an ordered collection of relational algebra attributes.

    Attributes can have a prefix, which reference the relation they belong to.
    """

    @classmethod
    def merge(cls, first, second):
        """
        Return an AttributeList that is the result of merging first with second.
        """
        merged = AttributeList([], None)

        assert (isinstance(first, AttributeList))
        assert (isinstance(second, AttributeList))
        merged._contents = first._contents[:]
        merged._contents += second._contents[:]

        return merged

    def __init__(self, names, prefix):
        self._contents = []
        self.extend(names, prefix)

    def __str__(self):
        """
        Return a comma delimitted string of prefixed attribute names.
        """
        return ', '.join(self.to_list())

    def __len__(self):
        return len(self._contents)

    def __getitem__(self, key):
        if not isinstance(key, str):
            raise TypeError

        prefix, _, name = key.rpartition('.')

        maybe = None
        for attribute in self._contents:
            if prefix:
                if attribute.name == name and attribute.prefix == prefix:
                    return attribute
            else:
                if attribute.name == name:
                    if maybe:
                        raise AttributeReferenceError(
                        'Ambiguous attribute reference.')
                    else:
                        maybe = attribute

        if maybe:
            return maybe

        raise KeyError

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __iter__(self):
        return self._contents.__iter__()

    def __reversed__(self):
        return self._contents.__reversed__()

    def __contains__(self, item):
        self._contents.__contains__(item)

    @property
    def contents(self):
        """
        Return a list of the Attributes in the AttributeList.
        """
        return self._contents

    @property
    def names(self):
        """
        Return a list of the names of the Attributes in the AttributeList.
        """
        return [name for name, _ in self._contents]

    def to_list(self):
        """
        Return a list of attributes. If an attribute has a prefix, return a
        prefixed attribute of the form: prefix.attribute.
        """
        return [attribute.prefixed for attribute in self._contents]

    def contains(self, attributes):
        """
        Return True if the attributes are in the AttributeList. Attributes may
        be prefixed with a relation name.
        """
        non_prefixed = [name for name, prefix in self._contents]
        prefixed = self.to_list()
        return set(attributes).issubset(set(prefixed + non_prefixed))

    def is_ambiguous(self):
        """
        Return True if the attributes in the AttributeList are ambiguous.

        Attributes are ambiguous if more than one attribute has the same name,
        regardless of prefix.
        """
        attributes = [name for name, prefix in self._contents]
        return len(set(attributes)) != len(attributes)

    def extend(self, attributes, prefix):
        """
        Add the attributes with the specified prefix to the end of the attribute
        list.
        """

        self._contents += [Attribute(attr, prefix) for attr in attributes]

    def restrict(self, restriction_list):
        """
        Restrict the attributes to those specified. Use the order in
        restriction_list.
        """
        new_attributes = []
        for reference in restriction_list:
            try:
                attribute = self[reference]
                if attribute in new_attributes:
                    raise AttributeReferenceError(
                        'Duplicate attribute reference.')
                new_attributes.append(attribute)
            except KeyError:
                raise AttributeReferenceError(
                    'At least one attribute does not exist.')
        self._contents = new_attributes

    def rename(self, names, prefix):
        """
        Rename the Attributes' names, prefixes, or both.
        If names are not specified, the current names must be unambiguous.
        :param names: A list of new names for each attribute or an empty list.
        :param prefix: A new prefix for the name or None
        """
        if names:
            if len(names) != len(self._contents):
                raise InputError('Attribute count mismatch.')

            if len(names) != len(set(names)):
                raise InputError('Attributes are ambiguous.')

            self._contents = []
            self.extend(names, prefix)

        elif prefix:
            if self.is_ambiguous():
                raise AttributeReferenceError('Attributes are ambiguous.')
            self._contents = [Attribute(name, prefix) for name, _ in
                              self._contents]