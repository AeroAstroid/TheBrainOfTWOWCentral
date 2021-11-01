from typing import List

from src.interpreter.expression import Expression


def concat(block: List, codebase):
    items = block[1:]
    buffer = ""
    for i in items:
        if type(i) == list:  # Array or String
            items.extend(Expression(i, codebase))
        else:
            buffer += Expression(i, codebase)
    return buffer
