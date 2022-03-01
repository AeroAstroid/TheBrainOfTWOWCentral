from typing import List

from src.interpreter.expression import Expression


def index(block: List, codebase):
    arr = Expression(block[1], codebase)
    if type(arr) == list:
        arr = arr[1:]

    return Expression(arr[Expression(block[2], codebase)], codebase)
