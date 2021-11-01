from typing import List

from src.interpreter.expression import Expression


def var(block: List, codebase):
    return codebase.variables[Expression(block[1], codebase)]
