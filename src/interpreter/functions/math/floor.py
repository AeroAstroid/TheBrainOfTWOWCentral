from typing import List

import math

from src.interpreter.expression import Expression


def floor(block: List, codebase):
    return math.floor(Expression(block[1], codebase))
