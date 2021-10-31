from typing import List

from src.interpreter.expression import Expression


def index(block: List, codebase):
    return Expression(block[1][1:][Expression(block[2], codebase)], codebase)
