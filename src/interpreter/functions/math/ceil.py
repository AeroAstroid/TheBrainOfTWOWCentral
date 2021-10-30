from typing import List

import math

from src.interpreter.expression import Expression


def ceil(block: List, codebase):
    return math.ceil(Expression(block[1], codebase))
