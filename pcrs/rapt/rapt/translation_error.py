class TranslationError(Exception):
    """
    Base class for exceptions in this module.
    """

    pass


class InputError(TranslationError):
    pass


class InputReferenceError(InputError):
    pass


class RelationReferenceError(InputReferenceError):
    pass


class AttributeReferenceError(InputReferenceError):
    pass