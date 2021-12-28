from typing import List

from src.interpreter.expression import Expression
from src.interpreter.userfunction import UserFunction


def function(block: List, codebase):
    name = Expression(block[1], codebase)

    # Assume block[2] is an array (it better be)
    args = {}

    # Code
    code = block[3:]

    # Stop non-blocks from being treated as blocks
    # if len(block) == 1:
    #     block = block[0]

    for i, argument in enumerate(Expression(block[2], codebase)):
        args[i] = argument

    UserFunction(name, args, code, codebase)
