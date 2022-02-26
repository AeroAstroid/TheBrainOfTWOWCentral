from typing import List

from src.interpreter.expression import Expression


def args(block: List, codebase):
    return codebase.arguments[Expression(block[1], codebase)]
