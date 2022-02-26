from typing import List

from src.interpreter.expression import Expression

def slice_func(block: List, codebase):
    return Expression(block[1], codebase)[
        int(Expression(block[2], codebase)):int(Expression(block[3], codebase))
    ]
