from typing import List

from src.interpreter.expression import Expression


def j(block: List, codebase):
    return "j" * min(Expression(block[1], codebase), 50)
