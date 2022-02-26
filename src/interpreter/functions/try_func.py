from typing import List

from src.interpreter.expression import Expression


def try_func(block: List, codebase):
    try:
        return Expression(block[1], codebase)
    except Exception:
        return Expression(block[2], codebase)
