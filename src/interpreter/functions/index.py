from typing import List

from src.interpreter.expression import Expression


def index(block: List, codebase):
    arr = Expression(block[1], codebase)
    if type(arr) == list:
        block[1] = block[1][1:]

    return Expression(block[1][Expression(block[2], codebase)], codebase)
