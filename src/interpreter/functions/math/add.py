from typing import List

from src.interpreter.expression import Expression


def add(block: List, codebase):
    items = block[1:]
    result = 0

    for num in items:
        # if type(num) == list:  # Array or String
        #     print(Expression(num, codebase))
        #     items.extend(Expression(num, codebase))
        # else:
        result += Expression(num, codebase)
    return result
