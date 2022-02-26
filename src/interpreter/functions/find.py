from typing import List

from src.interpreter.expression import Expression

def find(block: List, codebase):
    if len(block) == 3:
        return Expression(block[1], codebase).index(Expression(block[2], codebase))
    elif len(block) == 4:
        return Expression(block[1], codebase).index(
            Expression(block[2], codebase), Expression(block[3], codebase))
    else:
        return Expression(block[1], codebase).index(
            Expression(block[2], codebase), Expression(block[3], codebase),
            Expression(block[4], codebase))
