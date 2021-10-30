from typing import List

import math

from src.interpreter.expression import Expression


def abs_func(block: List, codebase):
    return math.fabs(Expression(block[1], codebase))

