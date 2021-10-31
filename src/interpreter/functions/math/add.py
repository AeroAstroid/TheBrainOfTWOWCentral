from typing import List

from src.interpreter.expression import Expression


def add(block: List, codebase):
    items = block[1:]
    result = 0

    for num in items:
        if type(num) == list:  # Array or String
            items.extend(Expression(num, codebase))
        else:
            result += Expression(str(num), codebase)
    return result
