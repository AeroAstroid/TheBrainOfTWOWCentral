from typing import List

from src.interpreter.expression import Expression


def array(block: List, codebase):
    result = ["ARRAY"]
    items = block[1:]
    for item in items:
        result.append(Expression(item, codebase))
    return result
