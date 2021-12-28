from typing import List
from src.interpreter.expression import Expression


def split(block: List, codebase):
    return Expression(["ARRAY", *block[1]], codebase)
