import src.interpreter.globals as globals
from src.interpreter.expression import Expression


def while_func(condition, *code):
    while Expression(condition, globals.codebase):
        for line in code:
            Expression(line, globals.codebase)