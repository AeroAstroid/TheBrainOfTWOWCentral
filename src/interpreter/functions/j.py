from typing import List

from src.interpreter.expression import Expression


def j(block: List, codebase):
    return "j" * max(min(Expression(block[1], codebase), 250), 1)
