from typing import List

from src.interpreter.expression import Expression


def define(block: List, codebase):
    codebase.variables[block[1]] = Expression(block[2], codebase)
