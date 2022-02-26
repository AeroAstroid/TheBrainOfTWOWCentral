from typing import List

from src.interpreter.expression import Expression


def joinall(block: List, codebase):
    return recursive_join(block[1:], codebase)

def recursive_join(block: List, codebase):
    result = ""
    
    for e in block:
        eval_e = Expression(e, codebase)
        if isinstance(eval_e, List):
            result += recursive_join(Expression(eval_e, codebase))
        else:
            result += str(eval_e)
