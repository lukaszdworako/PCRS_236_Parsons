class Syntax:

    def __init__(self, **kwargs):

        # First initialize a default syntax.

        # General tokens.
        self.terminator = ';'
        self.delim = ','
        self.params_start = '_{'
        self.params_stop = '}'
        self.paren_left = '('
        self.paren_right = ')'

        # Logical tokens.
        self.not_op = 'not'
        self.and_op = 'and'
        self.or_op = 'or'

        # Comparison operators.
        self.equal_op = '='
        self.not_equal_op = '!='
        self.not_equal_alt_op = '<>'
        self.less_than_op = '<'
        self.less_than_equal_op = '<='
        self.greater_than_op = '>'
        self.greater_than_equal_op = '>='

        # Relational algebra operators.
        self.project_op = '\\project'
        self.rename_op = '\\rename'
        self.select_op = '\\select'
        self.assign_op = ':='
        self.join_op = '\\join'
        self.theta_join_op = '\\theta_join'
        self.natural_join_op = '\\natural_join'
        self.difference_op = '\\difference'
        self.union_op = '\\union'
        self.intersect_op = '\\intersect'

        # Now set any user defined syntax.
        for key in kwargs:
            if hasattr(self, key):
                setattr(self, key, kwargs[key])