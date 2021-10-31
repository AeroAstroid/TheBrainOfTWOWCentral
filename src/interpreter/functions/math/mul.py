from typing import List

from src.interpreter.expression import Expression


def mul(block: List, codebase):
    if type(block[1]) == list and block[1][0] == "ARRAY":
        block = block[1]
    
    result = Expression(block[1], codebase)

    for num in block[2:]:
        result *= Expression(num, codebase)
    return result
