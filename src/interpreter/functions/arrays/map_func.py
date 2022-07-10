import src.interpreter.globals as globals
from src.interpreter.expression import Expression


def map_func(function, listToEdit):
    print(list(map(lambda f: Expression(function, globals.codebase), listToEdit)))
    return map(lambda f: Expression(function, globals.codebase), listToEdit)
