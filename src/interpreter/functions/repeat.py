from typing import List
from src.interpreter.expression import Expression


def repeat(block: List, codebase):
    return str(Expression(block[1], codebase)) * Expression(block[2], codebase)
