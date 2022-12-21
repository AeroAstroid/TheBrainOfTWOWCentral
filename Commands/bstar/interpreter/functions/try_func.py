import Commands.bstar.interpreter.globals as globals
from Commands.bstar.interpreter.expression import Expression


def try_func(attempt, on_error):
    try:
        return Expression(attempt, globals.codebase)
    except Exception as err:
        globals.codebase.variables[0]["error"] = type(err).__name__
        return Expression(on_error, globals.codebase)
