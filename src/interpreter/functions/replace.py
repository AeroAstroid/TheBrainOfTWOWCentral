from typing import List
from src.interpreter.expression import Expression


def replace_func(block: List, codebase):
    return Expression(block[1], codebase).replace(str(Expression(block[2], codebase)), str(Expression(block[3], codebase)))
