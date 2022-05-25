import src.interpreter.globals as globals
from src.interpreter.expression import Expression


def if_func(compare, true, false):
    if Expression(compare, globals.codebase):
        return Expression(true, globals.codebase)
    else:
        return Expression(false, globals.codebase)
