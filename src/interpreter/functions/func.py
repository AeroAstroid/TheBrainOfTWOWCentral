import src.interpreter.globals as globals
from src.interpreter.userfunction import UserFunction


def func(name, args, code):
    # name = Expression(block[1], codebase)

    # Assume block[2] is an array (it better be)
    parsed_args = {}

    # Code
    # code = block[3:]

    # Stop non-blocks from being treated as blocks
    # if len(block) == 1:
    #     block = block[0]

    for i, argument in enumerate(args[1:]):
        parsed_args[i] = argument

    UserFunction(name, parsed_args, code, True)
