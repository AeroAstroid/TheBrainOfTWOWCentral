from typing import List

from src.interpreter.expression import Expression


def join(block: List, codebase):
    first = Expression(block[1], codebase)
    delimiter = Expression(block[2], codebase) if len(block) >= 3 else ""
    
    buffer = first
    for i in block[2:]:
        buffer.extend(Expression(i, codebase))
        buffer = delimiter.join(buffer)
    return buffer
