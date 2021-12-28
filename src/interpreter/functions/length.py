from typing import List
from src.interpreter.expression import Expression


def length(block: List, codebase):
    return len(Expression(block[1], codebase))
