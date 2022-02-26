from typing import List

from src.interpreter.expression import Expression


def joinall(block: List, codebase):
    return recursive_join(block[1:], codebase)

def recursive_join(block: List, codebase):
    result = ""
    
    for e in block:
        if isinstance(e, List):
            result += recursive_join(e)
        else:
            result += str(e)
