from collections import namedtuple
import itertools

from .errors import InputError, AttributeReferenceError


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

    def __eq__(self, other):
        if type(self) is type(other):
            return self.prefixed == other.prefixed
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.prefixed)


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

    @staticmethod
    def has_duplicates(collection):
        """
        Return True if the collection has duplicate elements.
        """
        return len(set(collection)) != len(collection)

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

    def __eq__(self, other):
        if type(self) is type(other):
            return self.to_list() == other.to_list()
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __iter__(self):
        return iter(self._contents)

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

    def validate(self, references):
        """
        Check if all references exist and are unambiguous.
        """
        for reference in references:
            self.get_attribute(reference)

    def to_list(self):
        """
        Return a list of attributes. If an attribute has a prefix, return a
        prefixed attribute of the form: prefix.attribute.
        """
        return [attribute.prefixed for attribute in self._contents]

    def get_attribute(self, reference):
        """
        Return the attribute that matches the reference. Raise an error if
        the attribute cannot be found, or if there is more then one match.
        """
        prefix, _, name = reference.rpartition('.')

        match = None
        for attribute in self._contents:
            if name == attribute.name and \
                    (not prefix or prefix == attribute.prefix):
                if match:
                    raise AttributeReferenceError(
                        'Ambiguous attribute reference: {}.'.format(
                            attribute.name))
                else:
                    match = attribute

        if match:
            return match
        raise AttributeReferenceError(
            'Attribute does not exist: {}'.format(reference))

    def extend(self, attributes, prefix):
        """
        Add the attributes with the specified prefix to the end of the attribute
        list.
        """

        self._contents += [Attribute(attr, prefix) for attr in attributes]

    def trim(self, restriction_list):
        """
        Trim and reorder the attributes to the specifications in a restriction
        list.
        """
        replacement = []
        for reference in restriction_list:
            replacement.append(self.get_attribute(reference))

        if self.has_duplicates(replacement):
            raise AttributeReferenceError('Duplicate attribute reference.')
        self._contents = replacement

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
            if self.has_duplicates(names):
                raise InputError('Attributes are ambiguous.')
        else:
            # If the attributes are not renamed, but the relation / prefix is,
            # there is a risk of creating two or more attributes with the
            # same name and prefix.
            if prefix and self.has_duplicates(self.names):
                raise AttributeReferenceError('Attributes are ambiguous.')

        replacement = []
        for old, name in itertools.zip_longest(self._contents, names):
            new_name = name or old.name
            new_prefix = prefix or old.prefix
            replacement.append(Attribute(new_name, new_prefix))
        self._contents = replacement