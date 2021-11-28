from typing import List
from src.interpreter.expression import Expression


def replace_func(block: List, codebase):
    return Expression(block[0], codebase).replace(Expression(block[1], codebase),Expression(block[2], codebase))
