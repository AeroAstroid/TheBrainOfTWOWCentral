from typing import List

from src.interpreter.expression import Expression


def concat(block: List, codebase):
    # determine whether concat is concatenating strings or arrays
    first = Expression(block[1], codebase)
    is_array = (type(first) == list)
    buffer = [] if is_array else ""

    for i in block[1:]:
        element = Expression(i, codebase)
        if is_array != (type(element) == list):
            raise TypeError("Cannot call CONCAT with a mix of arrays and other types")
        if is_array:
            buffer.extend(element)
        else:
            buffer += str(element)

    return buffer
