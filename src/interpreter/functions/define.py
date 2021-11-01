from typing import List

from src.interpreter.expression import Expression


def define(block: List, codebase):
    codebase.variables[Expression(block[1], codebase)] = Expression(block[2], codebase)
