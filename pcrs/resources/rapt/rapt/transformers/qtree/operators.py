from .constants import *
from rapt.treebrd.node import Operator

latex_operator = {
    Operator.select: SELECT_OP,
    Operator.project: PROJECT_OP,
    Operator.rename: RENAME_OP,
    Operator.assign: ASSIGN_OP,
    Operator.cross_join: JOIN_OP,
    Operator.natural_join: NATURAL_JOIN_OP,
    Operator.theta_join: THETA_JOIN_OP,
    Operator.union: UNION_OP,
    Operator.difference: DIFFERENCE_OP,
    Operator.intersect: INTERSECT_OP
}