import src.interpreter.globals as globals
from src.interpreter.expression import Expression


def while_func(condition, *code):
    result = []
    while Expression(condition, globals.codebase):
        for line in code:
            line_result = Expression(line, globals.codebase)
            if line_result is not None:
                result.append(line_result)
    return result
