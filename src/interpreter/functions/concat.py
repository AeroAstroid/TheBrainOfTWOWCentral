from typing import List

from src.interpreter.expression import Expression


def concat(block: List, codebase):
    # determine whether concat is concatenating strings or arrays
    # string/array mix results in the first argument's data type
    is_array = False
    first = Expression(block[1], codebase)
    if type(first) == list:
        is_array = True
        buffer = first
    else:
        buffer = str(first)

    for i in block[2:]:
        if is_array:
            buffer.extend(Expression(i, codebase))
        else:
            buffer += str(Expression(i, codebase))

    return buffer
