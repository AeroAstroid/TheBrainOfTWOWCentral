from typing import List
from src.interpreter.expression import Expression


def replace(block: List, codebase):
    return Expression(block[1], codebase).replace(Expression(block[2], codebase),Expression(block[3], codebase))
