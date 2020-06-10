class TreeBRDError(Exception):
    """
    Base class for exceptions in this module.
    """

    pass


class InputError(TreeBRDError):
    pass


class InputReferenceError(InputError):
    pass


class RelationReferenceError(InputReferenceError):
    pass


class AttributeReferenceError(InputReferenceError):
    pass