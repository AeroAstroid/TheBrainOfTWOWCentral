import Commands.b_star.interpreter.globals as globals
from Commands.b_star.interpreter.expression import Expression


def if_func(compare, true, false):
    # TODO: Get a better name
    false_arg = false is not False

    if Expression(compare, globals.codebase):
        return Expression(true, globals.codebase)
    else:
        if false_arg:
            return Expression(false, globals.codebase)
