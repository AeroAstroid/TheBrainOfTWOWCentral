import src.interpreter.globals as globals
from src.interpreter.expression import Expression


def try_func(attempt, on_error):
    try:
        return Expression(attempt, globals.codebase)
    except Exception:
        return Expression(on_error, globals.codebase)
