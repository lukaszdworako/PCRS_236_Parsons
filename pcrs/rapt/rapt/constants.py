# General
TERMINATOR = ';'
DELIM = ','

# Logic operators
NOT_OP = 'not'
AND_OP = 'and'
OR_OP = 'or'

# Comparison operators
EQUAL_OP = '='
NOT_EQUAL_OP = '!='
NOT_EQUAL_ALT_OP = '<>'
LESS_THAN_OP = '<'
LESS_THAN_EQUAL_OP = '<='
GREATER_THAN_OP = '>'
GREATER_THAN_EQUAL_OP = '>='

# Relational algebra operators
PROJECT_OP = '\\project'
RENAME_OP = '\\rename'
SELECT_OP = '\\select'
ASSIGN_OP = ':='

JOIN_OP = '\\join'
THETA_JOIN_OP = '\\theta_join'
NATURAL_JOIN_OP = '\\natural_join'

DIFFERENCE_OP = '\\difference'
UNION_OP = '\\union'
INTERSECT_OP = '\\intersect'

UNARY_OP = {PROJECT_OP, RENAME_OP, SELECT_OP}
BINARY_OP = {DIFFERENCE_OP, UNION_OP, INTERSECT_OP, JOIN_OP, NATURAL_JOIN_OP}
BINARY_OP_PARAMS = {THETA_JOIN_OP, JOIN_OP}

# Lists and groups
PARAMS_START = '_{'
PARAMS_STOP = '}'
PAREN_LEFT = '('
PAREN_RIGHT = ')'

# Relational algebra semantics
SET_SEMANTICS = 'set_semantics'
BAG_SEMANTICS = 'bag_semantics'