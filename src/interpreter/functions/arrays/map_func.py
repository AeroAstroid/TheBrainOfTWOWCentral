import src.interpreter.globals as globals
from src.interpreter.expression import Expression


def map_func(function, listToEdit):
    return map(Expression(function, globals.codebase), listToEdit)
