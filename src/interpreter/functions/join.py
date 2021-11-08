from typing import List

from src.interpreter.expression import Expression


def join(block: List, codebase):
    first = Expression(block[1], codebase)
    buffer = first
    for i in block[2:]:
        buffer.extend(Expression(i, codebase))
        buffer = "".join(buffer)
    return buffer
