from typing import List

from src.interpreter.expression import Expression


def pow_func(block: List, codebase):
    result = Expression(block[1], codebase)

    for num in block[2:]:
        result **= Expression(num, codebase)
    return result